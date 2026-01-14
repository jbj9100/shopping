import os
import json
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Optional, List
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Kafka 서버 주소
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")


class KafkaProducerSingleton:
    """Kafka Producer 싱글톤 인스턴스 관리"""
    _instance: Optional[AIOKafkaProducer] = None
    _started: bool = False

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        """Kafka Producer 인스턴스 반환 (재사용)"""
        if cls._instance is None:
            cls._instance = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                compression_type='gzip',
                acks='all',  # 모든 replica 확인
                retries=3,
                max_in_flight_requests_per_connection=1,  # 순서 보장
            )
        
        if not cls._started:
            await cls._instance.start()
            cls._started = True
            logger.info(f"Kafka Producer started: {KAFKA_BOOTSTRAP_SERVERS}")
        
        return cls._instance

    @classmethod
    async def close_producer(cls) -> None:
        """Producer 종료"""
        if cls._instance is not None and cls._started:
            await cls._instance.stop()
            cls._started = False
            cls._instance = None
            logger.info("Kafka Producer stopped")


async def get_kafka_producer() -> AIOKafkaProducer:
    """
    Kafka Producer 반환 (싱글톤)
    
    Usage:
        producer = await get_kafka_producer()
        await producer.send('topic-name', value={'key': 'value'}, key='partition-key')
    """
    return await KafkaProducerSingleton.get_producer()


async def create_kafka_consumer(
    topics: List[str],
    group_id: str,
    auto_offset_reset: str = 'earliest',
    enable_auto_commit: bool = False
) -> AIOKafkaConsumer:
    """
    Kafka Consumer 생성 및 시작
    
    Args:
        topics: 구독할 토픽 리스트
        group_id: Consumer Group ID
        auto_offset_reset: 'earliest' | 'latest'
        enable_auto_commit: 자동 커밋 여부 (일반적으로 False로 수동 관리)
    
    Returns:
        시작된 AIOKafkaConsumer 인스턴스
    
    Usage:
        consumer = await create_kafka_consumer(['topic-1'], 'my-consumer-group')
        try:
            async for msg in consumer:
                # 처리 로직
                await consumer.commit()
        finally:
            await consumer.stop()
    """
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=enable_auto_commit,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
    )
    
    await consumer.start()
    logger.info(f"Kafka Consumer started: group_id={group_id}, topics={topics}")
    
    return consumer


async def close_kafka_producer() -> None:
    """Producer 종료 (애플리케이션 종료 시 호출)"""
    await KafkaProducerSingleton.close_producer()


async def ping_kafka() -> bool:
    """
    Kafka 연결 테스트
    
    Returns:
        연결 성공 여부
    """
    try:
        producer = await get_kafka_producer()
        # Producer가 시작되었으면 연결 성공으로 간주
        return True
    except Exception as e:
        logger.error(f"Kafka ping failed: {e}")
        return False
