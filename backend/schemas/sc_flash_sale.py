from datetime import datetime
from typing import Optional
from .common import APIModel


class FlashSaleJoinOut(APIModel):
    ok: bool
    status: str  # WAITING/ADMITTED...
    position: Optional[int] = None


class FlashSaleStatusOut(APIModel):
    flash_sale_id: int
    status: FlashQueueStatus
    position: Optional[int] = None
    joined_at: datetime