from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InstructorStatus

if TYPE_CHECKING:
    from app.models.queue_entry import QueueEntry
    from app.models.service_session import ServiceSession


class Instructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    login: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    instructor_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_plain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[InstructorStatus] = mapped_column(
        Enum(InstructorStatus, name="instructor_status"),
        default=InstructorStatus.offline,
        nullable=False,
    )
    accepted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    queue_entries: Mapped[list["QueueEntry"]] = relationship(back_populates="instructor")
    service_sessions: Mapped[list["ServiceSession"]] = relationship(back_populates="instructor")
