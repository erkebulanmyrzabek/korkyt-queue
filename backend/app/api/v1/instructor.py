from __future__ import annotations

from secrets import token_urlsafe

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import verify_password
from app.db.session import get_db
from app.models import Instructor, QueueEntry, QueueStatus
from app.schemas.admin import (
    InstructorBase,
    InstructorCurrentEntry,
    InstructorDashboardResponse,
    InstructorLoginRequest,
    InstructorLoginResponse,
)
from app.schemas.queue import InstructorActionResponse
from app.services.queue_service import QueueService

router = APIRouter()
queue_service = QueueService()

# In-memory token store is sufficient for this development scaffold.
_sessions: dict[str, int] = {}


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
        )
    return value.strip()


async def _require_instructor(
    session: AsyncSession,
    authorization: str | None,
) -> Instructor:
    token = _extract_bearer_token(authorization)
    instructor_id = _sessions.get(token)
    if instructor_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    instructor = await session.get(Instructor, instructor_id)
    if instructor is None or not instructor.is_active:
        _sessions.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Instructor is not available.",
        )
    return instructor


async def _get_current_entry(
    session: AsyncSession,
    instructor_id: int,
) -> InstructorCurrentEntry | None:
    current_entry = await session.scalar(
        select(QueueEntry)
        .options(selectinload(QueueEntry.user))
        .where(
            QueueEntry.instructor_id == instructor_id,
            QueueEntry.status.in_((QueueStatus.assigned, QueueStatus.in_service)),
        )
        .order_by(QueueEntry.assigned_at.desc())
    )
    if current_entry is None or current_entry.user is None:
        return None

    return InstructorCurrentEntry(
        queue_number=current_entry.queue_number,
        iin=current_entry.user.iin,
        photo_url=f"/media/{current_entry.user.photo}" if current_entry.user.photo else None,
    )


@router.post("/login", response_model=InstructorLoginResponse)
async def login_instructor(
    payload: InstructorLoginRequest,
    session: AsyncSession = Depends(get_db),
) -> InstructorLoginResponse:
    instructor = await session.scalar(
        select(Instructor).where(Instructor.login == payload.login.strip(), Instructor.is_active.is_(True))
    )
    if instructor is None or not verify_password(payload.password, instructor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password.",
        )

    token = token_urlsafe(32)
    _sessions[token] = instructor.id
    return InstructorLoginResponse(
        access_token=token,
        instructor=InstructorBase.model_validate(instructor),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_instructor(
    authorization: str | None = Header(default=None),
) -> None:
    token = _extract_bearer_token(authorization)
    _sessions.pop(token, None)


@router.get("/me", response_model=InstructorDashboardResponse)
async def get_instructor_dashboard(
    session: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> InstructorDashboardResponse:
    instructor = await _require_instructor(session=session, authorization=authorization)
    current_entry = await _get_current_entry(session=session, instructor_id=instructor.id)
    return InstructorDashboardResponse(
        instructor=InstructorBase.model_validate(instructor),
        current_entry=current_entry,
    )


@router.post("/me/available", response_model=InstructorActionResponse)
async def set_available(
    session: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> InstructorActionResponse:
    instructor = await _require_instructor(session=session, authorization=authorization)
    payload = await queue_service.assign_next_user(session=session, instructor_id=instructor.id)
    return InstructorActionResponse(**payload)


@router.post("/me/next", response_model=InstructorActionResponse)
async def complete_and_next(
    session: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> InstructorActionResponse:
    instructor = await _require_instructor(session=session, authorization=authorization)
    payload = await queue_service.complete_and_assign_next(
        session=session,
        instructor_id=instructor.id,
    )
    return InstructorActionResponse(**payload)
