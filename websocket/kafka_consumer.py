import asyncio
import json
import logging
import os
import uuid
import time
from collections import OrderedDict
from aiokafka import AIOKafkaConsumer
from core.websocket.websocket_manager import manager

logger = logging.getLogger(__name__)

# Dedupe 캐시 (LRU)
recent_events: OrderedDict[str, float] = OrderedDict()
MAX_CACHE_SIZE = 10000
CACHE_TTL = 300  # 5분 (초)

async def consume_realtime_events():
    """
    Kafka realtime.events 토픽 구독 및 WebSocket 브로드캐스트
    
    HPA 대응:
    - group_id를 unique하게 설정 → 모든 WS 인스턴스가 같은 메시지 받음
    - 각 인스턴스가 자기 연결 클라이언트에게만 전송
    
    Dedupe:
    - event_id 기반으로 중복 메시지 필터링
    - LRU 캐시로 메모리 관리
    """
    # Kafka Consumer 설정
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    unique_group_id = f"websocket-server-{uuid.uuid4().hex[:8]}"
    
    consumer = AIOKafkaConsumer(
        "realtime.events",
        bootstrap_servers=bootstrap_servers,
        group_id=unique_group_id,  # ✅ HPA: 각 인스턴스 다른 ID
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest'
    )
    
    await consumer.start()
    logger.info(f"✅ Kafka Consumer 시작: group_id={unique_group_id}")
    
    try:
        async for msg in consumer:
            try:
                event_data = msg.value
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
                
                # WebSocket 브로드캐스트
                await manager.broadcast(channel, event_data)
                
                logger.debug(f"📤 브로드캐스트 완료: channel={channel}, event_id={event_id}")
                
            except Exception as e:
                logger.error(f"❌ 메시지 처리 실패: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"❌ Kafka Consumer 에러: {e}", exc_info=True)
    
    finally:
        await consumer.stop()
        logger.info("Kafka Consumer 종료")
