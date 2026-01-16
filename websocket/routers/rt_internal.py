from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.websocket.websocket_manager import manager
import logging

router = APIRouter(prefix="/internal", tags=["Internal"])
logger = logging.getLogger(__name__)

class BroadcastRequest(BaseModel):
    channel: str       # "stock", "analytics", "flash_queue"
    data: dict         # 전송할 데이터

@router.post("/ws/broadcast")
async def broadcast_to_websocket(request: BroadcastRequest):
    """
    Consumer가 WebSocket으로 메시지 브로드캐스트 요청
    
    Consumer → Backend → Frontend
    """
    try:
        await manager.broadcast(request.channel, request.data)
        return {"status": "ok", "channel": request.channel}
    except Exception as e:
        logger.error(f"브로드캐스트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
