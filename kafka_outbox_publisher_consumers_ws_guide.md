# Kafka 중심 구현 정리 (Outbox Publisher 1 + Consumers 4 + WebSocket 1)

> 이 문서는 **현재 DB 스키마(특히 outbox_events / processed_events / stock_history / daily_sales / product_daily_stats)**를 기준으로  
> Kafka 기반으로 **Outbox Publisher 1개 + Consumer 4개 + WebSocket Server 1개**를 구현하는 방법을 한 번에 정리한 자료입니다.

---

## 0) 전체 아키텍처 한 장 요약

### 컴포넌트(권장 6~7개)
1. **API(FastAPI)**  
   - 도메인 변경(주문 생성/결제/취소/상품 변경 등) + `outbox_events` INSERT를 **같은 DB 트랜잭션**으로 처리  
2. **Outbox Publisher(1개)**  
   - `outbox_events`에서 `PENDING/FAILED`를 가져와 Kafka로 발행 → 성공 시 `PUBLISHED`, 실패 시 `FAILED` + 재시도
3. **Stock Update Consumer(1개)**  
   - `ORDER_PAID/ORDER_CANCELED/RESTOCKED` 등 이벤트로 재고 변경 + `stock_history` 기록
4. **Analytics Consumer(1개)**  
   - `daily_sales`, `product_daily_stats` 집계 테이블 UPSERT
5. **Cache Consumer(1개)**  
   - Redis 캐시 삭제/갱신 (DB 불필요)
6. **Flash Queue Consumer(1개)**  
   - `flash_sale_queue_entries` 상태 갱신 (대기열/입장/퇴장)
7. **WebSocket Server(1개)**  
   - Kafka `realtime.events`를 consume해서 접속 클라이언트에게 push

---

## 1) 테이블의 역할(핵심 이해)

### `outbox_events` (Publisher용)
- DB 트랜잭션 내에서 **도메인 변경 + 이벤트 기록**을 함께 저장
- Publisher가 `PENDING/FAILED` 이벤트를 읽어서 Kafka로 발행
- 발행 성공/실패 결과를 outbox 상태로 관리

### `processed_events` (Consumer 멱등성용)
- Kafka는 기본적으로 at-least-once라 **중복 메시지**가 올 수 있음
- Consumer는 처리 시작 시 `processed_events(consumer_name, event_id)` INSERT
  - PK 충돌이면 **이미 처리됨** → 스킵
  - 처음이면 계속 처리

---

## 2) Kafka에서 해야 할 작업(Helm 설치 상태 기준)

### 2.1 토픽 생성(예시)
- `order.events`
- `stock.events`
- `product.events`
- `flashsale.events`
- `realtime.events`
- (선택) `deadletter.events` (DLQ)

일반 Kafka라면(브로커 Pod 내부에서):
```bash
kubectl -n <kafka-namespace> get pods | grep kafka

kubectl -n <kafka-namespace> exec -it <kafka-broker-pod> -- \
  kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic order.events --partitions 3 --replication-factor 1
```

> 브로커가 3개면 replication-factor 3, 1개면 1

### 2.2 Consumer Group 규칙(매우 중요)
- 같은 토픽이라도 **group.id가 다르면 각자 모두 메시지를 받음** (pub-sub처럼 동작)
- 같은 group.id로 여러 인스턴스를 띄우면 **파티션을 나눠 처리**(스케일 아웃)

권장 group_id:
- `stock-consumer`
- `analytics-consumer`
- `cache-consumer`
- `flash-queue-consumer`
- `ws-consumer`

---

## 3) 이벤트 메시지(Envelope) 표준

Publisher가 Kafka로 보낼 메시지 형태를 고정합니다.

```json
{
  "event_id": "UUID(outbox_events.id)",
  "occurred_at": "2026-01-13T10:00:00Z",
  "aggregate_type": "ORDER",
  "aggregate_id": 123,
  "event_type": "ORDER_PAID",
  "payload": { "..." : "..." },
  "version": 1
}
```

- `event_id` = outbox ID → Consumer 멱등키로 사용 가능
- `key`는 보통 `aggregate_id`를 사용(같은 aggregate는 순서 보장에 유리)

---

## 4) 프로젝트 구조(권장)

```
app/
  common/
    config.py
    db.py
    idempotency.py
  publisher/
    main.py
  consumers/
    base.py
    stock.py
    analytics.py
    cache.py
    flash_queue.py
  ws_server/
    app.py
```

---

## 5) 공통 코드(Async DB / 멱등성)

### 5.1 Async DB 세션
```python
# app/common/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

def db_session():
    return SessionLocal()
```

### 5.2 Consumer 멱등성(핵심)
```python
# app/common/idempotency.py
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

SQL_INSERT = '''
INSERT INTO processed_events(consumer_name, event_id)
VALUES (:consumer_name, :event_id)
'''

async def claim_event(db: AsyncSession, consumer_name: str, event_id: str) -> bool:
    """True=처음 처리, False=이미 처리됨(중복)"""
    try:
        await db.execute(text(SQL_INSERT), {"consumer_name": consumer_name, "event_id": event_id})
        return True
    except IntegrityError:
        return False
```

---

## 6) Outbox Publisher(1개) 스켈레톤

Publisher가 하는 일:
1) outbox에서 `PENDING/FAILED` 이벤트를 **잠금으로 안전하게** 가져옴
2) Kafka Produce
3) 성공 → `PUBLISHED`
4) 실패 → `FAILED`, `retry_count++`, `next_attempt_at` 뒤로(backoff)

```python
# app/publisher/main.py
import asyncio, json
from sqlalchemy import text
from aiokafka import AIOKafkaProducer
from app.common.db import db_session

BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"  # 환경에 맞게
WORKER_ID = "publisher-1"

PICK_SQL = '''
SELECT id, topic, aggregate_type, aggregate_id, event_type, payload, retry_count
FROM outbox_events
WHERE status IN ('PENDING','FAILED')
  AND next_attempt_at <= now()
ORDER BY created_at
FOR UPDATE SKIP LOCKED
LIMIT :limit
'''

MARK_PROCESSING = '''
UPDATE outbox_events
SET status='PROCESSING', locked_at=now(), locked_by=:worker
WHERE id = ANY(:ids)
'''

MARK_PUBLISHED = '''
UPDATE outbox_events
SET status='PUBLISHED', published_at=now(), locked_at=NULL, locked_by=NULL, error_message=NULL
WHERE id=:id
'''

MARK_FAILED = '''
UPDATE outbox_events
SET status='FAILED',
    retry_count=retry_count+1,
    error_message=:err,
    next_attempt_at=now() + (:delay || ' seconds')::interval,
    locked_at=NULL,
    locked_by=NULL
WHERE id=:id
'''

def backoff(retry_count: int) -> int:
    return min(300, 2 ** max(0, retry_count))  # 1,2,4,... max 5분

async def loop():
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP)
    await producer.start()
    try:
        while True:
            async with db_session() as db:
                async with db.begin():
                    rows = (await db.execute(text(PICK_SQL), {"limit": 100})).mappings().all()
                    if rows:
                        ids = [r["id"] for r in rows]
                        await db.execute(text(MARK_PROCESSING), {"worker": WORKER_ID, "ids": ids})

            for r in rows:
                event_id = str(r["id"])
                topic = r["topic"] or "default.events"

                envelope = {
                    "event_id": event_id,
                    "aggregate_type": r["aggregate_type"],
                    "aggregate_id": int(r["aggregate_id"]),
                    "event_type": r["event_type"],
                    "payload": r["payload"],
                    "version": 1,
                }

                try:
                    key = str(r["aggregate_id"]).encode()
                    value = json.dumps(envelope, ensure_ascii=False).encode()
                    await producer.send_and_wait(topic, key=key, value=value)

                    async with db_session() as db2:
                        async with db2.begin():
                            await db2.execute(text(MARK_PUBLISHED), {"id": r["id"]})

                except Exception as e:
                    delay = backoff(int(r["retry_count"]))
                    async with db_session() as db2:
                        async with db2.begin():
                            await db2.execute(text(MARK_FAILED), {"id": r["id"], "err": str(e)[:2000], "delay": delay})

            await asyncio.sleep(0.2)
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(loop())
```

---

## 7) Consumer 4개(공통 베이스 + 예시)

### 7.1 Base Consumer
```python
# app/consumers/base.py
import json
from aiokafka import AIOKafkaConsumer
from app.common.db import db_session
from app.common.idempotency import claim_event

class BaseConsumer:
    def __init__(self, *, topics: list[str], group_id: str, name: str, bootstrap: str):
        self.topics = topics
        self.group_id = group_id
        self.name = name
        self.bootstrap = bootstrap
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap,
            group_id=group_id,
            enable_auto_commit=False,      # ✅ 직접 커밋(안전)
            auto_offset_reset="earliest",
        )

    async def start(self):
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                event = json.loads(msg.value.decode())
                event_id = event["event_id"]

                async with db_session() as db:
                    async with db.begin():
                        ok = await claim_event(db, self.name, event_id)
                        if not ok:
                            await self.consumer.commit()
                            continue

                        await self.handle(db, event)

                await self.consumer.commit()
        finally:
            await self.consumer.stop()

    async def handle(self, db, event: dict):
        raise NotImplementedError
```

### 7.2 Stock Consumer (재고 + 이력)
```python
# app/consumers/stock.py
from sqlalchemy import text
from app.consumers.base import BaseConsumer

GET_PRODUCT_LOCK = "SELECT id, stock FROM products WHERE id=:pid FOR UPDATE"
UPDATE_STOCK = "UPDATE products SET stock=:stock, is_sold_out=(:stock=0) WHERE id=:pid"
INSERT_HISTORY = '''
INSERT INTO stock_history(product_id, order_id, event_id, reason, stock_before, stock_after, delta)
VALUES (:pid, :oid, :eid, :reason, :before, :after, :delta)
'''

class StockConsumer(BaseConsumer):
    async def handle(self, db, event: dict):
        et = event["event_type"]
        p = event["payload"]

        if et == "ORDER_PAID":
            order_id = int(p["order_id"])
            for it in p["items"]:
                pid = int(it["product_id"])
                qty = int(it["qty"])

                row = (await db.execute(text(GET_PRODUCT_LOCK), {"pid": pid})).mappings().one()
                before = int(row["stock"])
                after = before - qty
                if after < 0:
                    raise ValueError(f"insufficient stock pid={pid} before={before} qty={qty}")

                await db.execute(text(UPDATE_STOCK), {"pid": pid, "stock": after})
                await db.execute(text(INSERT_HISTORY), {
                    "pid": pid, "oid": order_id, "eid": event["event_id"],
                    "reason": "ORDER_PAID", "before": before, "after": after, "delta": -qty
                })

        elif et == "ORDER_CANCELED":
            order_id = int(p["order_id"])
            for it in p["items"]:
                pid = int(it["product_id"])
                qty = int(it["qty"])

                row = (await db.execute(text(GET_PRODUCT_LOCK), {"pid": pid})).mappings().one()
                before = int(row["stock"])
                after = before + qty

                await db.execute(text(UPDATE_STOCK), {"pid": pid, "stock": after})
                await db.execute(text(INSERT_HISTORY), {
                    "pid": pid, "oid": order_id, "eid": event["event_id"],
                    "reason": "ORDER_CANCELED", "before": before, "after": after, "delta": qty
                })
```

### 7.3 Analytics Consumer (집계 UPSERT)
```python
# app/consumers/analytics.py
from sqlalchemy import text
from app.consumers.base import BaseConsumer

UPSERT_DAILY = '''
INSERT INTO daily_sales(date, total_orders, total_revenue, unique_customers)
VALUES (:d, :orders, :rev, :uniq)
ON CONFLICT (date) DO UPDATE SET
  total_orders = daily_sales.total_orders + EXCLUDED.total_orders,
  total_revenue = daily_sales.total_revenue + EXCLUDED.total_revenue,
  unique_customers = daily_sales.unique_customers + EXCLUDED.unique_customers,
  updated_at = now()
'''

UPSERT_PROD = '''
INSERT INTO product_daily_stats(product_id, date, purchase_count, revenue)
VALUES (:pid, :d, :pc, :rev)
ON CONFLICT (product_id, date) DO UPDATE SET
  purchase_count = product_daily_stats.purchase_count + EXCLUDED.purchase_count,
  revenue = product_daily_stats.revenue + EXCLUDED.revenue,
  updated_at = now()
'''

class AnalyticsConsumer(BaseConsumer):
    async def handle(self, db, event: dict):
        if event["event_type"] != "ORDER_PAID":
            return
        p = event["payload"]
        d = p["date"]  # "YYYY-MM-DD"를 넣어주거나, 없으면 Consumer에서 계산

        await db.execute(text(UPSERT_DAILY), {"d": d, "orders": 1, "rev": int(p["total_amount"]), "uniq": 1})

        for it in p["items"]:
            pid = int(it["product_id"])
            qty = int(it["qty"])
            price = int(it["price"])
            await db.execute(text(UPSERT_PROD), {"pid": pid, "d": d, "pc": qty, "rev": price * qty})
```

### 7.4 Cache Consumer (Redis DEL 템플릿)
```python
# app/consumers/cache.py
from app.consumers.base import BaseConsumer

class CacheConsumer(BaseConsumer):
    async def handle(self, db, event: dict):
        et = event["event_type"]
        if et in ("PRICE_UPDATED","STOCK_UPDATED","PRODUCT_UPDATED"):
            # TODO: Redis DEL/갱신
            return
```

### 7.5 Flash Queue Consumer (상태 갱신 템플릿)
```python
# app/consumers/flash_queue.py
from sqlalchemy import text
from app.consumers.base import BaseConsumer

UPDATE_STATUS = '''
UPDATE flash_sale_queue_entries
SET status=:status
WHERE flash_sale_id=:fsid AND user_id=:uid
'''

class FlashQueueConsumer(BaseConsumer):
    async def handle(self, db, event: dict):
        et = event["event_type"]
        p = event["payload"]
        fsid = int(p["flash_sale_id"])
        uid = int(p["user_id"])

        if et == "QUEUE_ADMITTED":
            await db.execute(text(UPDATE_STATUS), {"status": "ADMITTED", "fsid": fsid, "uid": uid})
        elif et == "QUEUE_LEFT":
            await db.execute(text(UPDATE_STATUS), {"status": "LEFT", "fsid": fsid, "uid": uid})
```

---

## 8) WebSocket Server (Kafka → WS Push)

```python
# app/ws_server/app.py
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer

BOOTSTRAP = "kafka.kafka.svc.cluster.local:9092"
TOPIC = "realtime.events"

app = FastAPI()
clients: set[WebSocket] = set()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # 필요 없으면 keepalive 용도로만 사용
    except WebSocketDisconnect:
        clients.discard(ws)

async def kafka_broadcast_loop():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id="ws-consumer",
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            data = msg.value.decode()
            dead = []
            for ws in clients:
                try:
                    await ws.send_text(data)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                clients.discard(ws)
    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup():
    asyncio.create_task(kafka_broadcast_loop())
```

---

## 9) 실행 순서(추천 학습 루트)

1. Kafka 토픽 생성  
2. outbox_events에 샘플 이벤트 INSERT  
3. Publisher 실행 → Kafka에 메시지 생성 확인  
4. Stock Consumer 실행 → `processed_events`, `stock_history`, `products.stock` 변화를 확인  
5. Analytics Consumer 실행 → 집계 테이블이 업데이트되는지 확인  
6. realtime.events 토픽에 메시지 넣고 WS 서버가 push 하는지 확인

---

## 10) Alembic이 왜 필요할 수 있는가(요약)

- Alembic은 **DB 스키마 변경(테이블/컬럼/인덱스/제약)**을 기록/배포하기 위한 도구
- outbox/queue 같은 구조는 partial index/unique, CHECK, extension 등이 포함되어 **수동 SQL이 금방 꼬이기 쉬움**
- dev/stage/prod 환경이 생기면 Alembic으로 “같은 변경을 같은 순서로 적용”하는 것이 안전

> 학습 단계에서는 없어도 되지만, 배포/운영/환경 여러 개가 생기면 매우 유용합니다.
