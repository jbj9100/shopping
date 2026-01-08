from minio import Minio
from os import environ
from exceptions.ep_image import ImageUploadError, ImageTypeError, ImageMaxSizeError
from fastapi import UploadFile
from pathlib import Path
import uuid
import io

# MinIO 설정
MINIO_URL = environ.get("MINIO_URL")
MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
MINIO_SECURE = environ.get("MINIO_SECURE").lower() == "true"
PUBLIC_BASE_URL = environ.get("MINIO_PUBLIC_BASE_URL", f"http://{MINIO_URL}")
BUCKET_LIST = [b.strip() for b in environ.get("MINIO_BUCKET_LIST", "category,product").split(",")]

# 이미지 업로드 설정
MINIO_IMAGE_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# MinIO 클라이언트 생성
minio_client = Minio(
    endpoint=MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def svc_get_minio_client():
    return minio_client


def svc_exist_or_make_minio_bucket(minio_client: Minio) -> bool:
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


async def svc_upload_image(file: UploadFile, bucket: str) -> dict:
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in MINIO_IMAGE_ALLOWED_EXTENSIONS:
        raise ImageTypeError(f"허용되지 않는 파일 형식입니다. 허용: {', '.join(MINIO_IMAGE_ALLOWED_EXTENSIONS)}")
    
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise ImageMaxSizeError("파일 크기는 5MB를 초과할 수 없습니다.")
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    try:
        client = svc_get_minio_client()
        client.put_object(
            bucket_name=bucket,
            object_name=unique_filename,
            data=io.BytesIO(content),
            length=len(content),
            content_type=file.content_type or "application/octet-stream"
        )
        
        url = svc_get_image_url(bucket, unique_filename)
        
        return {
            "filename": unique_filename,
            "url": url
        }
    except Exception as e:
        raise ImageUploadError(f"MinIO 업로드 실패: {str(e)}")


def svc_get_image_url(bucket_name: str, filename: str) -> str:
    return f"{PUBLIC_BASE_URL}/{bucket_name}/{filename}"


def svc_remove_image_in_bucket(minio_client: Minio, bucket_name: str, filename: str) -> str:
    try:
        minio_client.remove_object(bucket_name, filename)
        return f"{filename} image removed successfully"
    except Exception as e:
        raise Exception(f"image removal failed: {e}")