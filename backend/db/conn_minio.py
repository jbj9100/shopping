from services.minio.svc_minio import get_minio_client, exist_or_make_minio_bucket
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

load_dotenv()

async def ping_minio() -> bool:
    try:
        minio_client = get_minio_client()
        return exist_or_make_minio_bucket(minio_client)
    except S3Error as e:
        return False
    except Exception as e:
        return False


async def close_minio() -> None:
    """MinIO 연결 종료 (MinIO는 stateless이므로 실제로는 아무것도 안 함)"""
    print("MinIO connection closed (stateless)")

