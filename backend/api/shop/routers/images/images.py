from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from services.minio.svc_minio import svc_get_minio_client, svc_upload_image, svc_remove_image_in_bucket
from exceptions.ep_image import ImageUploadError, ImageTypeError, ImageMaxSizeError

router = APIRouter(prefix="/api/shop/images", tags=["images"])

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    bucket: str = Query(..., pattern="^(category|product)$")
):
    try:
        result = await svc_upload_image(file, bucket)
        return result
    except ImageTypeError as e:
        raise HTTPException(400, str(e))
    except ImageMaxSizeError as e:
        raise HTTPException(400, str(e))
    except ImageUploadError as e:
        raise HTTPException(500, str(e))


@router.delete("/{filename}")
async def delete_image(
    filename: str,
    bucket: str = Query(..., pattern="^(category|product)$")
):
    try:
        client = svc_get_minio_client()
        message = svc_remove_image_in_bucket(client, bucket, filename)
        return {"message": message}
    except Exception as e:
        raise HTTPException(500, f"삭제 실패: {str(e)}")
