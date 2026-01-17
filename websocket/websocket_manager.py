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
        # 마지막 통계 데이터 캐싱 (초기 접속자용)
        self.last_analytics_stats: Dict = None
    
    async def connect(self, websocket: WebSocket, channel: str):
        """클라이언트 연결"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"✅ WebSocket 연결: channel={channel}, 현재 {len(self.active_connections[channel])}명")
        
        # 전체 접속자 수 브로드캐스트
        await self.broadcast_user_count()

        # [NEW] analytics 채널 접속 시, 마지막 통계 데이터 즉시 전송
        if channel == "analytics" and self.last_analytics_stats:
            try:
                await websocket.send_json(self.last_analytics_stats)
                logger.info("📊 신규 접속자에게 초기 통계 데이터 전송 완료")
            except Exception as e:
                logger.error(f"❌ 초기 데이터 전송 실패: {e}")

    def disconnect(self, websocket: WebSocket, channel: str):
        """클라이언트 연결 해제"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
                logger.info(f"❌ WebSocket 연결 해제: channel={channel}, 남은 {len(self.active_connections[channel])}명")
                
                # 전체 접속자 수 브로드캐스트 (비동기 처리)
                asyncio.create_task(self.broadcast_user_count())
    
    async def broadcast(self, channel: str, message: dict):
        # [NEW] 통계 데이터 업데이트면 캐싱
        if channel == "analytics" and message.get("type") == "STATS_UPDATED":
            self.last_analytics_stats = message

        # ============ 7단계: 브로드캐스트 (병렬 전송) ============
        # 특정 채널의 모든 클라이언트에게 메시지 전송 (Backpressure 처리)
        
        if channel not in self.active_connections:
            # Stats update는 연결된 클라이언트가 없어도 캐싱되어야 하므로 return 안 함 (위에서 처리됨)
            if channel != "analytics": 
                logger.warning(f"⚠️ 채널 '{channel}'에 연결된 클라이언트 없음")
            return

        # channel="stock"이면 해당 채널에 있는 사람들을 찾음
        # connections = [사용자A, 사용자B, 사용자C]       
        connections = self.active_connections[channel]

        if not connections:
            return
        
        # 병렬 전송 태스크(할일) 생성하고 아직 보내진 않음
        # tasks = [
        #     "A에게 보내는 작업",
        #     "B에게 보내는 작업",
        #     "C에게 보내는 작업"
        # ]
        tasks = [
            self._send_with_timeout(ws, message)
            for ws in connections
        ]
        
        # 모든 전송 동시 실행 (gather)
        # 채널에 있는 모든 사람들에게 동시에 메시지 전송
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
       
        # ============ 8단계: Frontend로 JSON 전송! ============
        # 타임아웃 적용한 메시지 전송
        
        try:
            await asyncio.wait_for(
                ws.send_json(message),
                timeout=3.0  # 3초 타임아웃
            )
        except asyncio.TimeoutError:
            logger.error(f"⏱️ 전송 타임아웃 (3초 초과)")
            raise
        except Exception as e:
            logger.error(f"❌ 전송 중 에러: {e}")
            raise

    def get_total_user_count(self) -> int:
        """analytics 채널 접속자 수 (실제 사용자 수)"""
        return len(self.active_connections.get("analytics", []))

    async def broadcast_user_count(self):
        """전체 접속자 수를 analytics 채널로 브로드캐스트"""
        total_count = self.get_total_user_count()
        message = {
            "channel": "analytics",
            "type": "USER_COUNT_UPDATED",
            "count": total_count
        }
        await self.broadcast("analytics", message)
        logger.info(f"👥 접속자 수 브로드캐스트: {total_count}명")
manager = ConnectionManager()
