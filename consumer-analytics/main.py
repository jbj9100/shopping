import asyncio
import os
import logging
import json
from datetime import datetime, date
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from db.conn_db import get_db, ping_db, dispose_engine
from services.svc_daily_sales import update_daily_sales, get_daily_sales
from services.svc_product_stats import update_product_stats, get_top_products

load_dotenv()

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


class AnalyticsConsumer:
    """통계 집계 Consumer - DailySales + ProductDailyStats 업데이트"""
    
    def __init__(self):
        self.consumer: AIOKafkaConsumer = None
        self.producer: AIOKafkaProducer = None  # realtime 재발행용
        
    async def init_consumer(self):
        """Kafka Consumer 초기화"""
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        
        self.consumer = AIOKafkaConsumer(
            os.getenv("CONSUMER_TOPIC", "order-events"),
            bootstrap_servers=bootstrap_servers,
            group_id=os.getenv("CONSUMER_GROUP_ID", "analytics-consumer-group"),
            enable_auto_commit=False,  # 수동 커밋
            auto_offset_reset='earliest',
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
        단일 이벤트 처리
        
        처리 순서:
        1. order.created 이벤트만 처리
        2. DB 트랜잭션: DailySales + ProductDailyStats 업데이트
        3. realtime-events로 재발행 (WebSocket 전송용)
        """
        event_data = msg.value
        
        # 디버깅: 이벤트 전체 출력
        logger.info(f"📨 이벤트 수신: {event_data}")
        
        try:
            # 1. 이벤트 타입 확인
            event_type = event_data.get("event_type")
            logger.info(f"🔍 이벤트 타입: {event_type}")
            
            if event_type != "order.created":
                logger.warning(f"⚠️ 무시: {event_type} (order.created만 처리)")
                await self.consumer.commit()
                return
                # order.created만 처리
                return
            
            # 2. 필수 필드 추출
            order_id = event_data.get("order_id")
            total_amount = event_data.get("total_amount", 0)
            items = event_data.get("items", [])  # [{product_id, quantity, price}]
            
            if not order_id:
                logger.warning(f"⚠️ order_id 없음, 스킵: {event_data}")
                return
            
            # 주문 날짜 (created_at 또는 현재 시각)
            order_date = date.today()
            
            # 3. DB 트랜잭션: 통계 업데이트
            async for db in get_db():
                # 3.1. 일별 매출 업데이트
                await update_daily_sales(db, order_date, total_amount)
                
                # 3.2. 상품별 통계 업데이트
                for item in items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 0)
                    price = item.get("price", 0)
                    amount = price * quantity
                    
                    await update_product_stats(
                        db=db,
                        product_id=product_id,
                        stat_date=order_date,
                        quantity=quantity,
                        amount=amount
                    )
                
                # 3.3. 통계 조회 (commit 이전에 수행)
                daily_stats = await get_daily_sales(db, order_date)
                top_products = await get_top_products(db, order_date, limit=10)
                
                # 3.4. 커밋
                await db.commit()
                logger.info(f"✅ 통계 업데이트 완료: order_id={order_id}, amount={total_amount}")
            
            # 5. realtime-events로 재발행
            try:
                realtime_payload = {
                    "channel": "analytics",
                    "type": "STATS_UPDATED",
                    "data": {
                        "daily_sales": daily_stats,
                        "top_products": top_products
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.producer.send_and_wait(
                    topic=os.getenv("REALTIME_TOPIC", "realtime-events"),
                    value=realtime_payload
                )
                logger.info(f"📤 realtime 재발행 완료: order_id={order_id}")
                
            except KafkaError as e:
                logger.error(f"❌ realtime 발행 실패 (무시): {e}")
            
        except Exception as e:
            logger.error(f"❌ 이벤트 처리 실패: {e}", exc_info=True)
            raise
    
    async def consume_loop(self):
        """메인 소비 루프"""
        logger.info("🚀 Analytics Consumer 메인 루프 시작")
        
        try:
            async for msg in self.consumer:
                try:
                    await self.process_event(msg)
                    
                    # 성공 시에만 offset 커밋
                    await self.consumer.commit()
                    
                except Exception as e:
                    logger.error(f"❌ 처리 실패, offset 커밋 안 함: {e}")
                    
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
            logger.info("Analytics Consumer 종료 중...")
        except Exception as e:
            logger.error(f"❌ Consumer 실행 중 에러: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # 정리
            await dispose_engine()
            logger.info("Analytics Consumer 완전 종료")


async def main():
    """메인 엔트리포인트"""
    logger.info("🚀 Consumer Analytics 메인 함수 시작")
    
    consumer = AnalyticsConsumer()
    await consumer.run()


if __name__ == "__main__":
    asyncio.run(main())
