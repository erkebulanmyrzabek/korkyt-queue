from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from secrets import choice
from string import digits

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Instructor, InstructorStatus, QueueEntry, QueueStatus
from app.schemas.admin import CreateInstructorRequest, CreateInstructorResponse, InstructorBase
from app.schemas.queue import DashboardSummary
from app.core.security import hash_password

router = APIRouter()


def _generate_password(length: int = 6) -> str:
    return "".join(choice(digits) for _ in range(length))


@router.get("/dashboard/summary", response_model=DashboardSummary)
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


@router.get("/instructors", response_model=list[InstructorBase])
async def list_instructors(session: AsyncSession = Depends(get_db)) -> list[InstructorBase]:
    result = await session.execute(select(Instructor).order_by(Instructor.instructor_number.asc()))
    return [InstructorBase.model_validate(row) for row in result.scalars().all()]


@router.post(
    "/instructors",
    response_model=CreateInstructorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_instructor(
    payload: CreateInstructorRequest,
    session: AsyncSession = Depends(get_db),
) -> CreateInstructorResponse:
    existing = await session.scalar(
        select(Instructor).where(
            or_(
                Instructor.login == payload.login.strip(),
                Instructor.instructor_number == payload.instructor_number,
            )
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Instructor with this login or instructor number already exists.",
        )

    generated_password = _generate_password()
    instructor = Instructor(
        name=payload.name.strip(),
        login=payload.login.strip(),
        instructor_number=payload.instructor_number,
        password_hash=hash_password(generated_password),
        status=InstructorStatus.available,
        is_active=True,
    )
    session.add(instructor)
    await session.commit()
    await session.refresh(instructor)

    return CreateInstructorResponse(
        instructor=InstructorBase.model_validate(instructor),
        generated_password=generated_password,
    )
