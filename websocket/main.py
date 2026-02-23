from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from websocket_manager import manager
from kafka_consumer import consume_realtime_events
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# 로그 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# FastAPI 앱
app = FastAPI(title="WebSocket Server", version="1.0.0")

# CORS 설정
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/websocket/ws/{channel}")    # 채널선택
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
        # 연결 유지 (메시지는 Kafka Consumer → broadcast로만 전송)
        while True:
            # Frontend에서 보낸 메시지 수신 (ping/pong 등)
            data = await websocket.receive_text()
            logger.debug(f"Received from client ({channel}): {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info(f"Client disconnected from {channel}")

# ============ 1단계: 맨처음 실행 ============
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 Kafka Consumer 시작"""
    logger.info("🚀 WebSocket Server 시작")
    # ============ 2단계: kafka_consumer.py 백그라운드로 실행 ============
    asyncio.create_task(consume_realtime_events())

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "service": "websocket-server"}

if __name__ == "__main__":
    import uvicorn
    
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
