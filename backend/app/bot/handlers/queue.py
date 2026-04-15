from __future__ import annotations

import redis.asyncio as redis
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.utils import (
    get_user_language,
    localized_command_texts,
    main_keyboard,
    telegram_language_to_supported,
)
from app.core.config import settings
from app.core.i18n import translate
from app.db.session import async_session_factory
from app.services.queue_service import QueueService

router = Router()
queue_service = QueueService()
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


@router.message(Command("queue"))
@router.message(F.text.in_(localized_command_texts("bot.button.queue")))
async def command_queue(message: Message) -> None:
    if not message.from_user:
        return

    telegram_id = message.from_user.id
    language = await get_user_language(
        telegram_id,
        fallback=telegram_language_to_supported(message.from_user.language_code),
    )

    rate_limit_key = f"queue_rate_limit:{telegram_id}"
    counter = await redis_client.incr(rate_limit_key)
    if counter == 1:
        await redis_client.expire(rate_limit_key, 60)
    if counter > 1:
        await message.answer(
            translate("queue.rate_limit", language),
            reply_markup=main_keyboard(language),
        )
        return

    async with async_session_factory() as session:
        payload = await queue_service.get_position(session=session, telegram_id=telegram_id)

    if not payload:
        await message.answer(
            translate("queue.not_found", language),
            reply_markup=main_keyboard(language),
        )
        return

    await message.answer(
        translate(
            "queue.position",
            language,
            queue_number=payload["queue_number"],
            ahead=payload["ahead"],
        ),
        reply_markup=main_keyboard(language),
    )

