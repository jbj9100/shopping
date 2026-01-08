from fastapi import APIRouter, UploadFile, File, HTTPException
from minio.error import S3Error
from pathlib import Path
import uuid
import io
from services.minio.svc_minio import get_minio_client, get_image_url

router = APIRouter(prefix="/api/shop/images", tags=["images"])

# 허용 확장자
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload")
async def upload_image(
        file: UploadFile = File(...),
        bucket: str = Query(..., regex="^(category|product)$")):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    content = await file.read()  # uploadfile을 bytes로 읽어서 업로드
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 5MB를 초과할 수 없습니다.")
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    try:
        minio_client = get_minio_client()
        minio_client.put_object(
            bucket_name=bucket,
            object_name=unique_filename,
            data=io.BytesIO(content),
            length=len(content),
            content_type=file.content_type or "application/octet-stream"
        )
        
        url = get_image_url(bucket, unique_filename)
        
        return {
            "filename": unique_filename,
            "url": url
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO 업로드 실패: {str(e)}")


@router.delete("/{filename}")
async def delete_image(
        filename: str, 
        bucket: str = Query(..., regex="^(category|product)$")):
    try:
        minio_client = get_minio_client()
        minio_client.remove_object(bucket, filename)
        return {"message": "이미지가 삭제되었습니다."}
    except S3Error as e:
        if "NoSuchKey" in str(e):
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")
        raise HTTPException(status_code=500, detail=f"MinIO 삭제 실패: {str(e)}")
