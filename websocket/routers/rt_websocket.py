from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket.websocket_manager import manager
import logging

router = APIRouter(prefix="/websocket", tags=["WebSocket"])
logger = logging.getLogger(__name__)

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """
    WebSocket 엔드포인트 (Frontend 연결)
    
    채널 종류:
    - stock: 재고 변경
    - analytics: 매출/통계
    - flash_queue: 플래시 세일 대기열
    """
    await manager.connect(websocket, channel)
    try:
        # 연결 유지 (메시지는 broadcast로만 전송)
        while True:
            # Frontend에서 보낸 메시지 수신 (ping/pong 등)
            data = await websocket.receive_text()
            logger.debug(f"Received from client ({channel}): {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info(f"Client disconnected from {channel}")
