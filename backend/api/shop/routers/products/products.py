from fastapi import APIRouter, Request, Response



router = APIRouter(prefix="/api/shop/products", tags=["products"])


@router.get("/")
def products_get():
    return {"message": "products page"}



@router.post("/images/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    product_id: Optional[int] = None,
):
    minio = get_minio(request)
    try:
        result = await upload_image_and_get_url(minio, file, product_id=product_id)
        return {"url": result.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()