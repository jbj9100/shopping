from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from services.ai.ai_service import ai_service

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)

class GenerateDescriptionRequest(BaseModel):
    product_name: str
    category: str

class GenerateDescriptionResponse(BaseModel):
    description: str

@router.post("/generate-description", response_model=GenerateDescriptionResponse)
async def generate_product_description(request: GenerateDescriptionRequest):
    try:
        description = await ai_service.generate_product_description(
            product_name=request.product_name,
            category=request.category
        )
        return GenerateDescriptionResponse(description=description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
