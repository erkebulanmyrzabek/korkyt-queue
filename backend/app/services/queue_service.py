from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Instructor, InstructorStatus, LogEntry, QueueEntry, QueueStatus, ServiceSession, User


class QueueService:
    active_statuses = (QueueStatus.waiting, QueueStatus.assigned, QueueStatus.in_service)

    async def get_active_entry_by_telegram(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> QueueEntry | None:
        statement = (
            select(QueueEntry)
            .join(User)
            .options(selectinload(QueueEntry.user))
            .where(
                User.telegram_id == telegram_id,
                QueueEntry.status.in_(self.active_statuses),
            )
            .order_by(QueueEntry.created_at.asc())
        )
        return await session.scalar(statement)

    async def join_queue(
        self,
        session: AsyncSession,
        telegram_id: int,
        iin: str,
        photo: str,
        language: str,
    ) -> tuple[QueueEntry, bool]:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            user = User(
                telegram_id=telegram_id,
                iin=iin,
                photo=photo,
                language=language,
            )
            session.add(user)
            await session.flush()
        else:
            user.iin = iin
            user.photo = photo
            user.language = language

        active_entry = await self.get_active_entry_by_telegram(session=session, telegram_id=telegram_id)
        if active_entry:
            await session.commit()
            return active_entry, False

        entry = QueueEntry(
            user_id=user.id,
            queue_number="pending",
            status=QueueStatus.waiting,
        )
        session.add(entry)
        await session.flush()

        entry.queue_number = f"Q-{entry.id + 100}"
        session.add(
            LogEntry(
                action="queue.joined",
                metadata_json={
                    "user_id": user.id,
                    "queue_entry_id": entry.id,
                    "queue_number": entry.queue_number,
                },
            )
        )
        await session.commit()

        created_entry = await self._load_entry_with_user(session=session, entry_id=entry.id)
        if created_entry is None:
            raise RuntimeError("Queue entry was not persisted.")
        return created_entry, True

    async def get_position(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> dict[str, int | str] | None:
        entry = await self.get_active_entry_by_telegram(session=session, telegram_id=telegram_id)
        if entry is None:
            return None

        ahead = 0
        if entry.status == QueueStatus.waiting:
            ahead = await session.scalar(
                select(func.count())
                .select_from(QueueEntry)
                .where(
                    QueueEntry.status == QueueStatus.waiting,
                    QueueEntry.created_at < entry.created_at,
                )
            ) or 0

        return {
            "queue_number": entry.queue_number,
            "ahead": ahead,
        }

    async def get_tv_rows(self, session: AsyncSession, limit: int = 10) -> list[dict]:
        statement = (
            select(QueueEntry, Instructor.instructor_number)
            .join(Instructor, QueueEntry.instructor_id == Instructor.id, isouter=True)
            .where(QueueEntry.status.in_(self.active_statuses))
            .order_by(QueueEntry.created_at.asc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return [
            {
                "queue_number": entry.queue_number,
                "status": entry.status.value,
                "instructor_number": instructor_number,
            }
            for entry, instructor_number in result.all()
        ]

    async def assign_next_user(
        self,
        session: AsyncSession,
        instructor_id: int,
    ) -> dict:
        instructor = await session.get(Instructor, instructor_id)
        if instructor is None or not instructor.is_active:
            raise ValueError("Instructor not found or inactive.")

        current_entry = await session.scalar(
            select(QueueEntry)
            .options(selectinload(QueueEntry.user))
            .where(
                QueueEntry.instructor_id == instructor.id,
                QueueEntry.status.in_((QueueStatus.assigned, QueueStatus.in_service)),
            )
            .order_by(QueueEntry.assigned_at.desc())
        )
        if current_entry:
            return self._build_instructor_payload(
                instructor=instructor,
                current_entry=current_entry,
                message="Instructor already has an active user.",
            )

        statement = (
            select(QueueEntry)
            .where(QueueEntry.status == QueueStatus.waiting)
            .order_by(QueueEntry.created_at.asc(), QueueEntry.id.asc())
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(statement)
        next_entry = result.scalars().first()

        if next_entry is None:
            instructor.status = InstructorStatus.available
            await session.commit()
            return self._build_instructor_payload(
                instructor=instructor,
                current_entry=None,
                message="Queue is empty.",
            )

        now = datetime.now(timezone.utc)
        next_entry.status = QueueStatus.assigned
        next_entry.instructor_id = instructor.id
        next_entry.assigned_at = now
        instructor.status = InstructorStatus.busy
        session.add(
            ServiceSession(
                instructor_id=instructor.id,
                user_id=next_entry.user_id,
                start_time=now,
            )
        )
        session.add(
            LogEntry(
                action="queue.assigned",
                metadata_json={
                    "queue_entry_id": next_entry.id,
                    "instructor_id": instructor.id,
                },
            )
        )
        await session.commit()

        current_entry = await self._load_entry_with_user(session=session, entry_id=next_entry.id)
        return self._build_instructor_payload(
            instructor=instructor,
            current_entry=current_entry,
            message="Next user assigned.",
        )

    async def complete_and_assign_next(
        self,
        session: AsyncSession,
        instructor_id: int,
    ) -> dict:
        instructor = await session.get(Instructor, instructor_id)
        if instructor is None or not instructor.is_active:
            raise ValueError("Instructor not found or inactive.")

        now = datetime.now(timezone.utc)
        current_entry = await session.scalar(
            select(QueueEntry)
            .options(selectinload(QueueEntry.user))
            .where(
                QueueEntry.instructor_id == instructor.id,
                QueueEntry.status.in_((QueueStatus.assigned, QueueStatus.in_service)),
            )
            .order_by(QueueEntry.assigned_at.desc())
        )
        if current_entry is not None:
            current_entry.status = QueueStatus.completed
            current_entry.completed_at = now
            instructor.accepted_count += 1
            session.add(
                LogEntry(
                    action="queue.completed",
                    metadata_json={
                        "queue_entry_id": current_entry.id,
                        "instructor_id": instructor.id,
                    },
                )
            )
            service_session = await session.scalar(
                select(ServiceSession)
                .where(
                    ServiceSession.instructor_id == instructor.id,
                    ServiceSession.user_id == current_entry.user_id,
                    ServiceSession.end_time.is_(None),
                )
                .order_by(ServiceSession.start_time.desc())
            )
            if service_session is not None:
                service_session.end_time = now

        instructor.status = InstructorStatus.available
        await session.flush()

        statement = (
            select(QueueEntry)
            .where(QueueEntry.status == QueueStatus.waiting)
            .order_by(QueueEntry.created_at.asc(), QueueEntry.id.asc())
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(statement)
        next_entry = result.scalars().first()

        if next_entry is None:
            await session.commit()
            return self._build_instructor_payload(
                instructor=instructor,
                current_entry=None,
                message="Service completed. Queue is empty.",
            )

        next_entry.status = QueueStatus.assigned
        next_entry.instructor_id = instructor.id
        next_entry.assigned_at = now
        instructor.status = InstructorStatus.busy
        session.add(
            ServiceSession(
                instructor_id=instructor.id,
                user_id=next_entry.user_id,
                start_time=now,
            )
        )
        session.add(
            LogEntry(
                action="queue.reassigned",
                metadata_json={
                    "queue_entry_id": next_entry.id,
                    "instructor_id": instructor.id,
                },
            )
        )
        await session.commit()

        loaded_entry = await self._load_entry_with_user(session=session, entry_id=next_entry.id)
        return self._build_instructor_payload(
            instructor=instructor,
            current_entry=loaded_entry,
            message="Service completed. Next user assigned.",
        )

    async def _load_entry_with_user(
        self,
        session: AsyncSession,
        entry_id: int,
    ) -> QueueEntry | None:
        statement = (
            select(QueueEntry)
            .options(selectinload(QueueEntry.user))
            .where(QueueEntry.id == entry_id)
        )
        return await session.scalar(statement)

    def _build_instructor_payload(
        self,
        instructor: Instructor,
        current_entry: QueueEntry | None,
        message: str,
    ) -> dict:
        entry_payload = None
        if current_entry and current_entry.user:
            entry_payload = {
                "queue_number": current_entry.queue_number,
                "iin": current_entry.user.iin,
                "photo_url": (
                    f"/media/{current_entry.user.photo}"
                    if current_entry.user.photo
                    else None
                ),
            }

        return {
            "instructor_id": instructor.id,
            "instructor_number": instructor.instructor_number,
            "status": instructor.status.value,
            "message": message,
            "current_entry": entry_payload,
        }

