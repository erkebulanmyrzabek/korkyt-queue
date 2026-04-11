from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select

from app.bot.utils import get_user_language, telegram_language_to_supported
from app.core.i18n import SUPPORTED_LANGUAGES, translate
from app.db.session import async_session_factory
from app.models import User

router = Router()


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Қазақша", callback_data="lang:kk"),
                InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="English", callback_data="lang:en"),
            ]
        ]
    )


@router.message(Command("language"))
async def command_language(message: Message) -> None:
    if not message.from_user:
        return

    language = await get_user_language(
        message.from_user.id,
        fallback=telegram_language_to_supported(message.from_user.language_code),
    )
    await message.answer(
        translate("bot.language_select", language),
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def change_language(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.data:
        return

    language = callback.data.split(":")[-1]
    async with async_session_factory() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        if user is None:
            user = User(
                telegram_id=callback.from_user.id,
                language=language,
            )
            session.add(user)
        else:
            user.language = language
        await session.commit()

    updated_text = translate(
        "bot.language_updated",
        language,
        language_name=SUPPORTED_LANGUAGES[language],
    )
    if callback.message:
        await callback.message.edit_text(updated_text)
    await callback.answer()

