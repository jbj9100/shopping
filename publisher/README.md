# Publisher Service

Transactional Outbox Pattern의 **Publisher** 서비스입니다.  
Backend(FastAPI)가 `outbox_events` 테이블에 저장한 이벤트를 **polling** 방식으로 읽어 Kafka로 전송합니다.

## 📋 역할

```
Backend (FastAPI)
    ↓ INSERT
PostgreSQL의 outbox_events 테이블
    ↓ polling (비동기)
Publisher (이 서비스)
    ↓ send
Kafka
```

- **Backend**: `outbox_events` 테이블에 이벤트 저장만 함 (Kafka 직접 통신 ❌)
- **Publisher**: DB를 주기적으로 확인하고 Kafka로 전송

## 🚀 실행 방법

### 1. 의존성 설치
```bash
cd publisher
pip install -r requirements.txt
```

### 2. 환경변수 설정 (`.env`)
```env
# PostgreSQL (Backend와 같은 DB 사용)
DATABASE_CONN=postgresql+asyncpg://postgres:password@localhost:5432/shopping

# Kafka 브로커
KAFKA_BOOTSTRAP_SERVERS=localhost:9092,localhost:9093,localhost:9094

# Kafka SASL 인증 (필요시)
KAFKA_USER=user1
KAFKA_PASSWORD=password
KAFKA_SASL_MECHANISM=PLAIN

# Publisher 설정
POLL_INTERVAL_SECONDS=1  # DB 조회 주기 (초)
BATCH_SIZE=100            # 한 번에 처리할 이벤트 수
```

### 3. 실행
```bash
python main.py
```

## 📊 로그 예시

```
2026-01-16 09:50:00 - __main__ - INFO - PostgreSQL 연결 테스트...
2026-01-16 09:50:00 - conn_db - INFO - ✅ PostgreSQL 연결 성공
2026-01-16 09:50:01 - __main__ - INFO - Kafka 브로커 연결 시도: ['192.168.19.143:32222', ...]
2026-01-16 09:50:01 - __main__ - INFO - ✅ Kafka Producer 시작 완료
2026-01-16 09:50:01 - __main__ - INFO - 🚀 Publisher 시작 (ID=publisher-a1b2c3d4, interval=1s)
2026-01-16 09:50:02 - rep_outbox - INFO - 📥 조회된 pending 이벤트: 3개
2026-01-16 09:50:02 - __main__ - INFO - 📤 이벤트 발행 성공: order.created (topic=order-events)
```

## 🔧 동작 방식

### 1. Polling 루프
```python
while True:
    # 1. PENDING/FAILED 이벤트 조회
    events = await repository.get_pending_events(db, limit=100)
    
    # 2. 각 이벤트 처리
    for event in events:
        await process_event(db, event)
    
    # 3. 1초 대기
    await asyncio.sleep(1)
```

### 2. 이벤트 처리 흐름
1. **락 획득**: `status='PROCESSING'` + `locked_by=publisher_id`
2. **Kafka 전송**: `await producer.send_and_wait()`
3. **성공**: `status='PUBLISHED'`, `published_at=now()`
4. **실패**: `status='FAILED'`, `retry_count++`, `next_attempt_at=now() + 60s`

### 3. 동시성 제어
- 여러 Publisher 인스턴스 실행 가능
- `locked_at` 컬럼으로 중복 처리 방지
- 락 획득 실패 시 해당 이벤트 스킵

## 🎯 비동기를 사용하는 이유

**Q: Publisher도 FastAPI처럼 비동기를 써야 하나요?**  
**A: 네, 비동기가 더 효율적입니다!**

### 비동기의 장점
```python
# 여러 이벤트를 병렬로 Kafka 전송 가능
tasks = [send_to_kafka(e) for e in events]
await asyncio.gather(*tasks)  # 동시 전송!
```

- Kafka 전송 대기 시간 동안 다른 작업 수행 가능
- 배치 처리 시 throughput 향상
- `aiokafka` 라이브러리 활용

### 동기 방식의 단점
```python
# 하나씩 순차 전송 (느림)
for event in events:
    send_to_kafka(event)  # 각각 대기...
```

## 🛠️ ORM 사용

**Q: ORM은 FastAPI에서만 사용 가능한가요?**  
**A: 아니요! SQLAlchemy는 독립적인 라이브러리입니다.**

```python
# 순수 Python 스크립트에서도 ORM 사용 가능
from sqlalchemy.ext.asyncio import create_async_engine
from models.m_outbox import OutboxEvent

engine = create_async_engine("postgresql+asyncpg://...")
# FastAPI 없이도 ORM 모델 사용!
```

## 📝 Backend 연동

Backend에서는 `outbox_events` 테이블에 이벤트를 INSERT만 하면 됩니다:

```python
# backend/services/order_service.py
async def create_order(db: AsyncSession, ...):
    # 1. 주문 저장
    order = Orders(...)
    db.add(order)
    
    # 2. 같은 트랜잭션 내에서 outbox 이벤트 저장
    outbox_event = OutboxEvent(
        aggregate_type="ORDER",
        aggregate_id=order.id,
        event_type="order.created",
        payload={"order_id": order.id, "user_id": order.user_id},
        topic="order-events",  # 옵션
        status="PENDING"
    )
    db.add(outbox_event)
    await db.commit()  # 원자적 커밋
```

**Backend는 Kafka 연결 불필요!** (`conn_kafka.py` 제거 가능)

---

## 🏗️ 코드 구조

### 📂 디렉터리 구조
```
publisher/
├── main.py                    # 엔트리포인트 + 전체 오케스트레이션
├── db/
│   ├── conn_db.py            # PostgreSQL 연결 관리
│   └── conn_kafka.py         # Kafka 설정값
├── models/
│   ├── m_common.py           # SQLAlchemy Base
│   └── m_outbox.py           # OutboxEvent 모델
├── repositories/
│   └── rep_outbox.py         # Outbox DB 쿼리 로직
├── .env                       # 환경변수
└── requirements.txt           # 의존성
```

### 🎯 main.py에 모든 로직을 넣는 이유

**Q: 왜 main.py에 클래스와 실행 로직을 다 넣나요?**

**A: Publisher는 "단순한 백그라운드 작업"이기 때문입니다.**

#### ✅ 현재 구조의 장점

1. **단순성**: 
   - Publisher 역할: DB polling → Kafka 전송 (단일 책임)
   - 복잡한 비즈니스 로직 없음
   - 파일 하나에서 전체 흐름 파악 가능

2. **유지보수**:
   - 150줄 정도의 코드로 전체 로직 완성
   - 디버깅 시 파일 하나만 보면 됨
   - 로직 추적이 쉬움

3. **의존성 분리**:
   - `db/`: DB 연결만 담당
   - `models/`: 테이블 정의만 담당
   - `repositories/`: 쿼리만 담당
   - `main.py`: 위 모듈들을 조합해서 실행

#### ❌ 분리했을 때의 단점

```python
# 불필요하게 분리할 경우
publisher/
├── main.py               # run() 호출만?
├── services/
│   └── publisher_service.py  # poll_and_publish() 로직
├── core/
│   └── kafka_producer.py     # init_kafka_producer() 로직
└── workers/
    └── event_processor.py    # process_event() 로직
```

- 파일 4개를 왔다갔다 해야 함
- 로직이 간단한데 과도한 추상화
- 코드 150줄을 4개의 파일로 나누면 오히려 복잡함

#### 🎯 언제 분리해야 하나?

다음과 같은 경우에만 분리 권장:

1. **여러 종류의 Publisher**가 필요할 때
   ```python
   publisher/
   ├── workers/
   │   ├── order_publisher.py
   │   ├── payment_publisher.py
   │   └── notification_publisher.py
   └── main.py  # 여러 worker 관리
   ```

2. **복잡한 변환 로직**이 추가될 때
   ```python
   publisher/
   ├── transformers/
   │   └── event_transformer.py  # payload 가공
   └── main.py
   ```

3. **코드가 500줄 이상**으로 증가할 때

#### ✅ 결론

현재는 **150줄의 단순한 로직**이므로 `main.py` 하나로 충분합니다!

---

## 🔄 전체 실행 흐름

### 1. 프로그램 시작
```python
if __name__ == "__main__":
    asyncio.run(main())  # ← 여기서 시작!
```

### 2. 초기화 단계
```python
async def main():
    publisher = OutboxPublisher()  # 객체 생성
    await publisher.run()           # 실행

async def run(self):
    # 1. DB 연결 테스트
    await ping_db()
    
    # 2. Kafka Producer 시작
    await self.init_kafka_producer()
    
    # 3. 무한 루프 시작
    await self.poll_and_publish()
```

### 3. 무한 루프 (핵심)
```python
async def poll_and_publish(self):
    while True:  # 무한 반복!
        # [1] DB에서 pending 이벤트 조회 (최대 100개)
        events = await self.repository.get_pending_events(db, limit=100)
        
        # [2] 각 이벤트를 순차 처리
        for event in events:
            await self.process_event(db, event)
        
        # [3] 1초 대기 후 다시 반복
        await asyncio.sleep(1)
```

### 4. 개별 이벤트 처리
```python
async def process_event(self, db, event):
    # 1️⃣ 락 획득 (다른 Publisher 중복 방지)
    locked = await self.repository.mark_as_processing(db, event.id, PUBLISHER_ID)
    if not locked:
        return  # 다른 Publisher가 처리중이면 스킵
    
    try:
        # 2️⃣ Kafka로 전송
        await self.producer.send_and_wait(topic=topic, value=event.payload)
        
        # 3️⃣ 성공 처리
        await self.repository.mark_as_published(db, event.id)
        
    except KafkaError as e:
        # 4️⃣ 실패 처리 (60초 후 재시도)
        await self.repository.mark_as_failed(db, event.id, str(e), retry_delay_seconds=60)
```

### 📊 시각적 흐름도

```
python main.py 실행
    ↓
main() 함수
    ↓
OutboxPublisher 객체 생성
    ↓
run() 실행
    ├─ 1. DB 연결 테스트 (ping_db)
    ├─ 2. Kafka Producer 시작 (init_kafka_producer)
    └─ 3. poll_and_publish() 호출
        ↓
┌───────────────────────────────────────────────┐
│ while True: (무한 루프)                        │
│                                               │
│  [1단계] DB 조회                               │
│     ↓                                         │
│  repository.get_pending_events()              │
│     ↓                                         │
│  100개 이벤트 가져옴                           │
│                                               │
│  [2단계] 순차 처리                             │
│     ↓                                         │
│  for event in events:                         │
│     ├─ process_event(event1)                  │
│     │    ├─ 락 획득 (mark_as_processing)      │
│     │    ├─ Kafka 전송 (send_and_wait)        │
│     │    └─ 성공 처리 (mark_as_published)     │
│     ├─ process_event(event2)                  │
│     └─ ...                                    │
│                                               │
│  [3단계] 대기                                  │
│     ↓                                         │
│  await asyncio.sleep(1초)                     │
│                                               │
└────────────────↑──────────────────────────────┘
                 │
               다시 반복
```

### 💡 핵심 포인트

1. **무한 루프**: `while True`로 계속 실행
2. **배치 조회**: 한 번에 최대 100개 이벤트 조회
3. **순차 처리**: `for` 문으로 하나씩 Kafka 전송
4. **재시도 메커니즘**: 실패 시 자동으로 60초 후 재시도
5. **동시성 제어**: `locked_by` 컬럼으로 여러 Publisher 인스턴스 실행 가능

---

## 🔧 모듈별 역할

| 모듈 | 역할 | 책임 |
|------|------|------|
| `main.py` | 오케스트레이션 | 전체 흐름 제어, 초기화, 무한 루프 |
| `db/conn_db.py` | DB 연결 | PostgreSQL 세션 관리 |
| `db/conn_kafka.py` | Kafka 설정 | 환경변수 로드 (연결은 main.py에서) |
| `models/m_outbox.py` | 테이블 정의 | OutboxEvent SQLAlchemy 모델 |
| `repositories/rep_outbox.py` | DB 쿼리 | CRUD 로직 (조회/업데이트) |

**설계 원칙**: 각 모듈은 단일 책임만 가지고, `main.py`가 이들을 조합하여 실행
