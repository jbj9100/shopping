from fastapi import APIRouter


router = APIRouter(prefix="/api/shop/price_alert", tags=["price_alert"])

@router.get("/")
async def get_price_alerts():
    pass