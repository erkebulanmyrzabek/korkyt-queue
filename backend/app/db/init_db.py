from __future__ import annotations

from sqlalchemy import text
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import async_session_factory, engine
from app.models import Instructor, InstructorStatus


async def init_db() -> None:
    settings.media_root_path.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        # Lightweight bootstrap migration for existing dev volumes.
        await connection.execute(text("ALTER TABLE instructors ADD COLUMN IF NOT EXISTS login VARCHAR(64)"))
        await connection.execute(text("UPDATE instructors SET login = CONCAT('instr', instructor_number) WHERE login IS NULL"))
        await connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_instructors_login ON instructors (login)"))

    async with async_session_factory() as session:
        instructor_count = await session.scalar(select(func.count()).select_from(Instructor))
        if not instructor_count and settings.app_env == "development":
            for number in range(1, 4):
                session.add(
                    Instructor(
                        name=f"Instructor {number}",
                        login=f"instr{number}",
                        instructor_number=number,
                        password_hash=hash_password(f"10000{number}"),
                        status=InstructorStatus.available,
                        is_active=True,
                    )
                )
            await session.commit()
