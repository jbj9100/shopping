from minio import Minio
from os import environ


# MinIO 설정
MINIO_URL = environ.get("MINIO_URL")
MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
MINIO_SECURE = environ.get("MINIO_SECURE").lower() == "true"  # boolean 변환
PUBLIC_BASE_URL = environ.get("MINIO_PUBLIC_BASE_URL", f"http://{MINIO_URL}")
BUCKET_LIST = [b.strip() for b in environ.get("MINIO_BUCKET_LIST", "category,product").split(",")]
# env에 하드코딩된것 리스트가 아니라 문자열이라서 구분필요 + 공백 제거

# MinIO 클라이언트 생성
minio_client = Minio(
    endpoint=MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def get_minio_client():
    return minio_client

def exist_or_make_minio_bucket(minio_client: Minio) -> bool:
    try:
        for bucket in BUCKET_LIST:
            if minio_client.bucket_exists(bucket):
                print(f"{bucket} bucket exists")
            else:
                minio_client.make_bucket(bucket)
                print(f"{bucket} bucket created")
        return True
    except Exception as e:
        print(f"bucket processing failed: {e}")
        return False


def get_image_url(bucket_name: str, filename: str) -> str:
    return f"{PUBLIC_BASE_URL}/{bucket_name}/{filename}"
