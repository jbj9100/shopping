import os
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
import logging
import asyncio

load_dotenv()

logger = logging.getLogger(__name__)

# Kafka 서버 주소 (콤마로 구분된 여러 브로커 지원)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_USER = os.getenv("KAFKA_USER")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM")


async def ping_kafka() -> tuple[bool, str | None]:
    """
    Kafka 브로커 연결 테스트 (간단한 헬스체크)
    
    Returns:
        (성공 여부, 에러 메시지 또는 None)
    
    Note:
        - FastAPI 앱 시작 시 Kafka 연결 확인용
        - Producer/Consumer는 별도 프로세스에서 실행되므로 여기서는 생성하지 않음
        - SASL 인증이 설정되어 있으면 자동으로 사용
    """
    producer = None
    
    # Bootstrap 서버 파싱
    if not KAFKA_BOOTSTRAP_SERVERS:
        return False, "KAFKA_BOOTSTRAP_SERVERS 환경변수가 설정되지 않았습니다"
    
    bootstrap_servers = [s.strip() for s in KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]
    
    if not bootstrap_servers:
        return False, "유효한 Kafka 브로커 주소가 없습니다"
    
    logger.info(f"Kafka 브로커 연결 시도: {bootstrap_servers}")
    
    try:
        # SASL 인증 사용 여부 확인
        if KAFKA_USER and KAFKA_PASSWORD:
            logger.info(f"SASL 인증 사용: mechanism={KAFKA_SASL_MECHANISM}, user={KAFKA_USER}")
            producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                security_protocol="SASL_PLAINTEXT",
                sasl_mechanism=KAFKA_SASL_MECHANISM,
                sasl_plain_username=KAFKA_USER,
                sasl_plain_password=KAFKA_PASSWORD,
                request_timeout_ms=10000,
            )
        else:
            logger.info("SASL 인증 없이 연결 시도")
            producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=10000,
            )
        
        # Producer 시작 (타임아웃 15초)
        await asyncio.wait_for(producer.start(), timeout=15.0)
        logger.info("✅ Kafka connection successfully")
        return True, None
        
    except KafkaConnectionError as e:
        error_msg = f"Kafka connection failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    except asyncio.TimeoutError:
        error_msg = f"Kafka 연결 타임아웃 (15s): {bootstrap_servers}"
        logger.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Kafka 예상치 못한 에러: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    finally:
        if producer is not None:
            try:
                await producer.stop()
            except Exception as e:
                logger.warning(f"Producer 종료 실패 (무시): {str(e)}")
