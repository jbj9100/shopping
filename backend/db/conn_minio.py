from services.minio.svc_minio import svc_get_minio_client, svc_exist_or_make_minio_bucket
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

async def ping_minio() -> tuple[bool, str | None]:
    """
    MinIO 연결 테스트 및 버킷 생성
    
    Returns:
        (성공 여부, 에러 메시지 또는 None)
    """
    try:
        minio_client = svc_get_minio_client()
        result = svc_exist_or_make_minio_bucket(minio_client)
        if result:
            return True, None
        else:
            return False, "MinIO bucket creation/verification failed"
    except S3Error as e:
        return False, f"MinIO S3 error: {str(e)}"
    except Exception as e:
        return False, f"MinIO connection error: {str(e)}"



async def close_minio() -> None:
    """MinIO 연결 종료 (MinIO는 stateless이므로 실제로는 아무것도 안 함)"""
    print("MinIO connection closed (stateless)")

