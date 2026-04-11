from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Instructor, InstructorStatus, QueueEntry, QueueStatus
from app.schemas.queue import DashboardSummary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(session: AsyncSession = Depends(get_db)) -> DashboardSummary:
    active_statuses = [QueueStatus.waiting, QueueStatus.assigned, QueueStatus.in_service]
    queue_total = await session.scalar(
        select(func.count()).select_from(QueueEntry).where(QueueEntry.status.in_(active_statuses))
    )
    active_instructors = await session.scalar(
        select(func.count()).select_from(Instructor).where(Instructor.is_active.is_(True))
    )
    available_instructors = await session.scalar(
        select(func.count())
        .select_from(Instructor)
        .where(
            Instructor.is_active.is_(True),
            Instructor.status == InstructorStatus.available,
        )
    )

    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, time.min, tzinfo=timezone.utc)
    tomorrow_start = today_start + timedelta(days=1)
    served_today = await session.scalar(
        select(func.count())
        .select_from(QueueEntry)
        .where(
            QueueEntry.status == QueueStatus.completed,
            QueueEntry.completed_at >= today_start,
            QueueEntry.completed_at < tomorrow_start,
        )
    )

    return DashboardSummary(
        total_people_in_queue=queue_total or 0,
        active_instructors=active_instructors or 0,
        available_instructors=available_instructors or 0,
        users_served_today=served_today or 0,
    )

