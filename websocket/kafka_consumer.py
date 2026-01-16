import asyncio
import json
import logging
import os
import uuid
import time
from collections import OrderedDict
from aiokafka import AIOKafkaConsumer
from websocket_manager import manager

logger = logging.getLogger(__name__)

# Dedupe 캐시 (LRU)
recent_events: OrderedDict[str, float] = OrderedDict()
MAX_CACHE_SIZE = 10000
CACHE_TTL = 300  # 5분 (초)

async def consume_realtime_events():
   
     # ============ 3단계: Kafka Consumer 설정 ============
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    unique_group_id = f"websocket-server-{uuid.uuid4().hex[:8]}"
    
    consumer = AIOKafkaConsumer(
        "realtime.events",       # 3. 구독할 토픽
        bootstrap_servers=bootstrap_servers,
        group_id=unique_group_id,  # ✅ HPA: 각 인스턴스 다른 ID
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest'
    )
    # 여기까지는 그냥 설정만! 아직 연결 안 됨
    
     # ============ 4단계: Kafka 연결 시작 ============
    await consumer.start() # ← Kafka 서버에 연결!
    logger.info(f"✅ Kafka Consumer 시작: group_id={unique_group_id}")
    
    try:         
        async for msg in consumer: 
            # 무한 루프: Kafka에 메시지 올 때까지 계속 기다림...
            # 메시지 없으면 여기서 계속 대기!
            try: 
                # ============ 5단계: 메시지 받음! ============
                event_data = msg.value # ← 메시지 도착하면 여기 실행!
            
                event_id = event_data.get("event_id")
                # Dedupe: 중복 이벤트 필터링
                if event_id and event_id in recent_events:
                    logger.debug(f"⏭️ 중복 이벤트 무시: {event_id}")
                    continue
                
                # 캐시 추가 (LRU)
                if event_id:
                    recent_events[event_id] = time.time()
                    
                    # 캐시 크기 제한
                    if len(recent_events) > MAX_CACHE_SIZE:
                        recent_events.popitem(last=False)  # 가장 오래된 것 제거
                
                # 채널 추출
                channel = event_data.get("channel", "stock")
                
                # ============ 6단계: Frontend로 전송하는데 websocket_manager.py의 broadcast 함수를 사용하는것
                # 그래서 이 함수를 실행하면 7,8단계 실행한다. 그다음 끝나면 다시 5단계로 돌아감
                await manager.broadcast(channel, event_data)
                
                logger.debug(f"📤 브로드캐스트 완료: channel={channel}, event_id={event_id}")
                # ============ 다시 5단계로 돌아감 ============
                # async for 루프가 다시 돌면서 다음 메시지 대기
            except Exception as e:
                logger.error(f"❌ 메시지 처리 실패: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"❌ Kafka Consumer 에러: {e}", exc_info=True)
    
    finally:
        await consumer.stop()
        logger.info("Kafka Consumer 종료")
