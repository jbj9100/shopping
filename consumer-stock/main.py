import asyncio
import os
import logging
import json
import uuid
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from db.conn_db import get_db, ping_db, dispose_engine
from repositories.rep_stock_history import create_stock_history_idempotent

load_dotenv()

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


class StockConsumer:
    """재고 이벤트 Consumer - StockHistory 기록 + realtime 재발행"""
    
    def __init__(self):
        self.consumer: AIOKafkaConsumer = None
        self.producer: AIOKafkaProducer = None  # realtime 재발행용
        
    async def init_consumer(self):
        """Kafka Consumer 초기화"""
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        
        self.consumer = AIOKafkaConsumer(
            os.getenv("CONSUMER_TOPIC", "product-events"),
            bootstrap_servers=bootstrap_servers,
            group_id=os.getenv("CONSUMER_GROUP_ID", "stock-consumer-group"),
            enable_auto_commit=False,  # ✅ 수동 커밋 (성공 시에만)
            auto_offset_reset='earliest',  # 처음 시작 시 모든 메시지 읽기
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
            sasl_plain_username=os.getenv("KAFKA_USER"),
            sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        )
        await self.consumer.start()
        logger.info(f"✅ Kafka Consumer 시작: topic={os.getenv('CONSUMER_TOPIC')}, group_id={os.getenv('CONSUMER_GROUP_ID')}")
        
    async def init_producer(self):
        """Kafka Producer 초기화 (realtime 재발행용)"""
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_PLAINTEXT"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
            sasl_plain_username=os.getenv("KAFKA_USER"),
            sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        )
        await self.producer.start()
        logger.info(f"✅ Kafka Producer 시작: realtime_topic={os.getenv('REALTIME_TOPIC')}")
    
    async def process_event(self, msg):
        """
        단일 이벤트 처리 (멱등성 + 트랜잭션)
        
        처리 순서:
        1. 필수 필드 검증
        2. DB 트랜잭션: StockHistory 기록
        3. realtime-events로 재발행 (DB 커밋 후)
        """
        event_data = msg.value
        
        try:
            # 1. 필수 필드 검증
            event_id = event_data.get("event_id")
            if not event_id:
                logger.warning(f"⚠️ event_id 없음, 스킵: {event_data}")
                # TODO: DLQ 토픽으로 전송
                return
            
            product_id = event_data.get("product_id")
            if not product_id:
                logger.warning(f"⚠️ product_id 없음, 스킵: {event_data}")
                return
            
            # 2. DB 트랜잭션: StockHistory 기록
            async for db in get_db():
                # delta 계산 (payload에 없으면 자동 계산)
                old_stock = event_data.get("old_stock", 0)
                new_stock = event_data.get("new_stock", 0)
                delta = event_data.get("delta")
                
                # 디버깅: delta 계산 확인
                logger.info(f"🔍 받은 payload delta: {delta}, old_stock: {old_stock}, new_stock: {new_stock}")
                
                if delta is None:
                    delta = new_stock - old_stock  # 자동 계산
                    logger.info(f"🔍 delta 자동 계산: {delta}")
                else:
                    logger.info(f"🔍 delta payload에 포함됨: {delta}")
                
                history = await create_stock_history_idempotent(
                    db=db,
                    event_id=uuid.UUID(event_id),
                    product_id=product_id,
                    order_id=event_data.get("order_id"),
                    reason=event_data.get("change_reason", "UNKNOWN"),
                    stock_before=old_stock,
                    stock_after=new_stock,
                    delta=delta
                )
                
                if history is None:
                    logger.info(f"⏭️ 중복 이벤트 무시: {event_id}")
                    return  # 이미 처리됨, offset은 커밋해야 다시 안 읽음
                
                await db.commit()  # ✅ DB 먼저 커밋
                logger.info(f"✅ StockHistory 기록 완료: event_id={event_id}, product_id={product_id}")
            
            # 3. realtime-events로 재발행 (DB 커밋 후)
            try:
                realtime_payload = {
                    "event_id": event_id,
                    "channel": "stock",  # 모든 재고 이벤트는 stock 채널로
                    "type": "STOCK_UPDATED",
                    "data": {
                        "product_id": product_id,
                        "new_stock": event_data.get("new_stock", 0),
                        "is_out_of_stock": event_data.get("is_out_of_stock", False)
                    },
                    "timestamp": event_data.get("timestamp")
                }
                
                await self.producer.send_and_wait(
                    topic=os.getenv("REALTIME_TOPIC", "realtime-events"),
                    value=realtime_payload
                )
                logger.info(f"📤 realtime 재발행 완료: event_id={event_id}")
                
            except KafkaError as e:
                # realtime 발행 실패는 로그만 (최종 정합성 허용)
                logger.error(f"❌ realtime 발행 실패 (무시): {e}")
            
        except Exception as e:
            logger.error(f"❌ 이벤트 처리 실패: {e}", exc_info=True)
            raise  # 실패 시 offset 커밋 안 함 → 재처리
    
    async def consume_loop(self):
        """메인 소비 루프"""
        logger.info("🚀 Stock Consumer 메인 루프 시작")
        
        try:
            async for msg in self.consumer:
                try:
                    await self.process_event(msg)
                    
                    # ✅ 성공 시에만 offset 커밋
                    await self.consumer.commit()
                    
                except Exception as e:
                    logger.error(f"❌ 처리 실패, offset 커밋 안 함: {e}")
                    # offset 커밋 안 하면 재시작 시 다시 처리됨
                    
        except KeyboardInterrupt:
            logger.info("Consumer 종료 중...")
        finally:
            await self.consumer.stop()
            await self.producer.stop()
            logger.info("Kafka Consumer/Producer 종료 완료")
    
    async def run(self):
        """Consumer 실행"""
        try:
            # 1. DB 연결 테스트
            logger.info("PostgreSQL 연결 테스트...")
            success, error = await ping_db()
            if not success:
                raise Exception(f"DB 연결 실패: {error}")
            logger.info("✅ PostgreSQL 연결 성공")
            
            # 2. Kafka Consumer 초기화
            await self.init_consumer()
            
            # 3. Kafka Producer 초기화 (realtime용)
            await self.init_producer()
            
            # 4. 메인 루프 실행
            await self.consume_loop()
            
        except KeyboardInterrupt:
            logger.info("Stock Consumer 종료 중...")
        except Exception as e:
            logger.error(f"❌ Consumer 실행 중 에러: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # 정리
            await dispose_engine()
            logger.info("Stock Consumer 완전 종료")


async def main():
    """메인 엔트리포인트"""
    consumer = StockConsumer()
    await consumer.run()


if __name__ == "__main__":
    asyncio.run(main())
