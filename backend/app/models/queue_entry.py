from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import QueueStatus

if TYPE_CHECKING:
    from app.models.instructor import Instructor
    from app.models.user import User


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    queue_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    status: Mapped[QueueStatus] = mapped_column(
        Enum(QueueStatus, name="queue_status"),
        default=QueueStatus.waiting,
        nullable=False,
    )
    instructor_id: Mapped[int | None] = mapped_column(
        ForeignKey("instructors.id"),
        nullable=True,
    )
    notification_flags: Mapped[dict[str, bool]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="queue_entries")
    instructor: Mapped["Instructor | None"] = relationship(back_populates="queue_entries")

