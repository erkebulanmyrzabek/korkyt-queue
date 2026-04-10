from __future__ import annotations

from sqlalchemy import select

from app.core.i18n import resolve_language
from app.db.session import async_session_factory
from app.models import User


def telegram_language_to_supported(value: str | None) -> str:
    code = (value or "").split("-")[0].lower()
    return resolve_language(code)


async def get_user_language(telegram_id: int, fallback: str | None = None) -> str:
    async with async_session_factory() as session:
        language = await session.scalar(
            select(User.language).where(User.telegram_id == telegram_id)
        )
    return resolve_language(language or fallback)

