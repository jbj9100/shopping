import asyncio
import os
import logging
import uuid
from dotenv import load_dotenv
from db.conn_db import get_db, ping_db, dispose_engine
from db.conn_kafka import (
    KAFKA_BOOTSTRAP_SERVERS, 
    KAFKA_USER, 
    KAFKA_PASSWORD, 
    KAFKA_SASL_MECHANISM,
    list_kafka_topics  # 토픽 목록 조회
)
from repositories.rep_outbox import OutboxRepository
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Publisher 설정
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS")) 
BATCH_SIZE = int(os.getenv("BATCH_SIZE")) 
PUBLISHER_ID = f"publisher-{uuid.uuid4().hex[:8]}"  


class OutboxPublisher:
    """Transactional Outbox Pattern - Publisher"""

    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        self.repository = OutboxRepository()

    async def init_kafka_producer(self) -> None:
        """Kafka Producer 초기화"""
        bootstrap_servers = [s.strip() for s in KAFKA_BOOTSTRAP_SERVERS.split(",")]
        
        logger.info(f"Kafka 브로커 연결 시도: {bootstrap_servers}")
        logger.info(f"SASL 인증 사용: mechanism={KAFKA_SASL_MECHANISM}, user={KAFKA_USER}")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism=KAFKA_SASL_MECHANISM,
            sasl_plain_username=KAFKA_USER,
            sasl_plain_password=KAFKA_PASSWORD,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=10000,
        )

        await self.producer.start()
        logger.info("✅ Kafka Producer 시작 완료")

    async def close_kafka_producer(self) -> None:
        """Kafka Producer 종료"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka Producer 종료")

    async def process_event(self, db, event) -> None:
        """
        단일 이벤트 처리
        
        1. PROCESSING 상태로 변경 (락 획득)
        2. Kafka로 전송
        3. 성공 시 PUBLISHED로 변경
        4. 실패 시 FAILED로 변경 + 재시도 스케줄링
        """
        # 1. 락 획득 시도
        locked = await self.repository.mark_as_processing(db, event.id, PUBLISHER_ID)
        if not locked:
            return  # 다른 Publisher가 처리중
        
        try:
            # 2. Kafka로 전송
            topic = event.topic or f"{event.aggregate_type.lower()}-events"
            
            await self.producer.send_and_wait(
                topic=topic,
                value=event.payload,
                key=str(event.aggregate_id).encode('utf-8')
            )
            
            # 3. 성공 처리
            await self.repository.mark_as_published(db, event.id)
            logger.info(f"📤 이벤트 발행 성공: {event.event_type} (topic={topic})")
            
        except KafkaError as e:
            # 4. 실패 처리
            error_msg = f"Kafka 전송 실패: {str(e)}"
            await self.repository.mark_as_failed(db, event.id, error_msg, retry_delay_seconds=60)
            
        except Exception as e:
            # 예상치 못한 에러
            error_msg = f"예상치 못한 에러: {type(e).__name__}: {str(e)}"
            await self.repository.mark_as_failed(db, event.id, error_msg, retry_delay_seconds=300)

    async def poll_and_publish(self) -> None:
        """DB polling 후 이벤트 발행 (메인 루프)"""
        logger.info(f"🚀 Publisher 시작 (ID={PUBLISHER_ID}, interval={POLL_INTERVAL_SECONDS}s)")
        
        while True: # 무한 루프
            try:
                # 1. DB에서 pending 이벤트 조회
                async for db in get_db():
                    events = await self.repository.get_pending_events(db, limit=BATCH_SIZE)
                    
                    if not events:
                        logger.debug("발행할 이벤트 없음")
                        break         # 이벤트 없으면 조회 종료
                    
                    # 2. 각 이벤트 kafka 발행 처리 (순차)
                    for event in events:
                        await self.process_event(db, event)
                
                # 3. 설정한 interval 1초 후 다시 반복
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                
            except Exception as e:
                logger.error(f"❌ Polling 중 에러: {type(e).__name__}: {str(e)}")
                await asyncio.sleep(5)  # 에러 시 5초 대기 후 재시도

    async def run(self) -> None:
        """Publisher 실행"""
        try:
            # 1. DB 연결 테스트
            logger.info("PostgreSQL 연결 테스트...")
            success, error = await ping_db()
            if not success:
                raise Exception(f"DB 연결 실패: {error}")
            
            # 2. Kafka Producer 초기화
            await self.init_kafka_producer()
            
            # 3. Kafka 토픽 목록 확인 (간단히)
            success, topics, error = await list_kafka_topics()
            if not success:
                logger.warning(f"⚠️  토픽 조회 실패: {error}")
            
            # 4. 메인 루프 실행
            await self.poll_and_publish()
            
        except KeyboardInterrupt:
            logger.info("Publisher 종료 중...")
        except Exception as e:
            logger.error(f"❌ Publisher 실행 중 에러: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # 정리
            await self.close_kafka_producer()
            await dispose_engine()
            logger.info("Publisher 완전 종료")


async def main():
    """메인 엔트s리포인트"""
    publisher = OutboxPublisher()
    await publisher.run()


if __name__ == "__main__":
    asyncio.run(main())
