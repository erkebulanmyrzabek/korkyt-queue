from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.queue import InstructorActionResponse, TvQueueRow
from app.services.queue_service import QueueService

router = APIRouter()
queue_service = QueueService()


@router.get("/tv", response_model=list[TvQueueRow])
async def tv_queue(session: AsyncSession = Depends(get_db)) -> list[TvQueueRow]:
    rows = await queue_service.get_tv_rows(session=session, limit=10)
    return [TvQueueRow(**row) for row in rows]


@router.post("/instructors/{instructor_id}/available", response_model=InstructorActionResponse)
async def instructor_available(
    instructor_id: int,
    session: AsyncSession = Depends(get_db),
) -> InstructorActionResponse:
    try:
        payload = await queue_service.assign_next_user(session=session, instructor_id=instructor_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return InstructorActionResponse(**payload)


@router.post("/instructors/{instructor_id}/next", response_model=InstructorActionResponse)
async def instructor_next(
    instructor_id: int,
    session: AsyncSession = Depends(get_db),
) -> InstructorActionResponse:
    try:
        payload = await queue_service.complete_and_assign_next(
            session=session,
            instructor_id=instructor_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return InstructorActionResponse(**payload)

