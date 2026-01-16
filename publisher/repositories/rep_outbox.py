from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.m_outbox import OutboxEvent
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)


class OutboxRepository:
    """Outbox 이벤트 조회/업데이트 전용 Repository"""

    @staticmethod
    async def get_pending_events(db: AsyncSession, limit: int = 100) -> List[OutboxEvent]:
        """
        발행 대기 중인 이벤트 조회 (PENDING + FAILED with retry)
        
        Args:
            db: DB 세션
            limit: 최대 조회 개수
            
        Returns:
            발행 대기 이벤트 리스트
        """
        query = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status.in_(['PENDING', 'FAILED']),
                OutboxEvent.next_attempt_at <= datetime.now(),
                OutboxEvent.locked_at.is_(None)  # 다른 Publisher가 처리중이지 않은 것만
            )
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)  # ✅ 동시성 제어: 다른 트랜잭션이 락 획득한 행은 건너뜀
        )
        
        result = await db.execute(query)
        events = result.scalars().all()
        logger.info(f"📥 조회된 pending 이벤트: {len(events)}개")
        return list(events)

    @staticmethod
    async def mark_as_processing(
        db: AsyncSession, 
        event_id: str, 
        publisher_id: str
    ) -> bool:
        """
        이벤트를 PROCESSING 상태로 변경 + 락 설정
        
        Args:
            db: DB 세션
            event_id: 이벤트 ID
            publisher_id: Publisher 인스턴스 ID
            
        Returns:
            업데이트 성공 여부
        """
        query = (
            update(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.locked_at.is_(None)  # 락이 없는 경우만
            )
            .values(
                status='PROCESSING',
                locked_at=datetime.now(),
                locked_by=publisher_id
            )
        )
        
        result = await db.execute(query)
        await db.commit()
        
        success = result.rowcount > 0
        if not success:
            logger.warning(f"⚠️ 이벤트 {event_id} 락 획득 실패 (다른 Publisher가 처리중)")
        
        return success

    @staticmethod
    async def mark_as_published(db: AsyncSession, event_id: str) -> None:
        """
        이벤트를 PUBLISHED 상태로 변경
        
        Args:
            db: DB 세션
            event_id: 이벤트 ID
        """
        query = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status='PUBLISHED',
                published_at=datetime.now(),
                locked_at=None,
                locked_by=None
            )
        )
        
        await db.execute(query)
        await db.commit()
        logger.info(f"✅ 이벤트 {event_id} 발행 완료")

    @staticmethod
    async def mark_as_failed(
        db: AsyncSession, 
        event_id: str, 
        error_message: str,
        retry_delay_seconds: int = 60
    ) -> None:
        """
        이벤트를 FAILED 상태로 변경 + 재시도 스케줄링
        
        Args:
            db: DB 세션
            event_id: 이벤트 ID
            error_message: 에러 메시지
            retry_delay_seconds: 재시도 대기 시간 (초)
        """
        query = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status='FAILED',
                retry_count=OutboxEvent.retry_count + 1,
                error_message=error_message,
                next_attempt_at=datetime.now() + timedelta(seconds=retry_delay_seconds),
                locked_at=None,
                locked_by=None
            )
        )
        
        await db.execute(query)
        await db.commit()
        logger.error(f"❌ 이벤트 {event_id} 발행 실패: {error_message}")
