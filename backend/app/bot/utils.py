from __future__ import annotations

from sqlalchemy import select
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.core.i18n import SUPPORTED_LANGUAGES, resolve_language, translate
from app.db.session import async_session_factory
from app.models import User


def telegram_language_to_supported(value: str | None) -> str:
    code = (value or "").split("-")[0].lower()
    return resolve_language(code)


def main_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=translate("bot.button.start", language)),
                KeyboardButton(text=translate("bot.button.queue", language)),
            ],
            [KeyboardButton(text=translate("bot.button.language", language))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def localized_command_texts(value: str) -> list[str]:
    return [translate(value, lang) for lang in SUPPORTED_LANGUAGES]


async def get_user_language(telegram_id: int, fallback: str | None = None) -> str:
    async with async_session_factory() as session:
        language = await session.scalar(
            select(User.language).where(User.telegram_id == telegram_id)
        )
    return resolve_language(language or fallback)

