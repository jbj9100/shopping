from fastapi import WebSocket
from typing import Dict, List
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket 연결 관리 (채널별)"""
    
    def __init__(self):
        # 채널별 활성 연결 목록
        # {"stock": [ws1, ws2], "analytics": [ws3]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        """클라이언트 연결"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"✅ WebSocket 연결: channel={channel}, 현재 {len(self.active_connections[channel])}명")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """클라이언트 연결 해제"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
                logger.info(f"❌ WebSocket 연결 해제: channel={channel}, 남은 {len(self.active_connections[channel])}명")
    
    async def broadcast(self, channel: str, message: dict):
        """
        특정 채널의 모든 클라이언트에게 메시지 전송 (Backpressure 처리)
        
        - asyncio.gather로 병렬 전송 (순차보다 빠름)
        - 3초 타임아웃 (느린 클라이언트 격리)
        - 실패한 연결 자동 제거
        """
        if channel not in self.active_connections:
            logger.warning(f"⚠️ 채널 '{channel}'에 연결된 클라이언트 없음")
            return
        
        connections = self.active_connections[channel]
        if not connections:
            return
        
        # 병렬 전송 태스크 생성
        tasks = [
            self._send_with_timeout(ws, message)
            for ws in connections
        ]
        
        # 모든 전송 동시 실행 (gather)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 실패한 연결 제거
        dead_connections = []
        for ws, result in zip(connections, results):
            if isinstance(result, Exception):
                logger.error(f"❌ 전송 실패: {result}")
                dead_connections.append(ws)
        
        for ws in dead_connections:
            self.disconnect(ws, channel)
        
        success_count = len(connections) - len(dead_connections)
        logger.info(f"📤 브로드캐스트: channel={channel}, 성공={success_count}/{len(connections)}명")
    
    async def _send_with_timeout(self, ws: WebSocket, message: dict):
        """타임아웃 적용한 메시지 전송"""
        try:
            await asyncio.wait_for(
                ws.send_json(message),
                timeout=3.0  # 3초 타임아웃
            )
        except asyncio.TimeoutError:
            raise Exception("전송 타임아웃 (3초)")
        except Exception as e:
            raise Exception(f"전송 에러: {e}")

# 전역 매니저 인스턴스
manager = ConnectionManager()
