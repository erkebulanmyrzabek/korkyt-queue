from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import QueueRegistration
from app.bot.utils import get_user_language, telegram_language_to_supported
from app.core.config import settings
from app.core.i18n import translate
from app.db.session import async_session_factory
from app.services.queue_service import QueueService

router = Router()
queue_service = QueueService()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return

    telegram_id = message.from_user.id
    fallback_language = telegram_language_to_supported(message.from_user.language_code)
    language = await get_user_language(telegram_id, fallback=fallback_language)

    async with async_session_factory() as session:
        active_entry = await queue_service.get_active_entry_by_telegram(
            session=session,
            telegram_id=telegram_id,
        )

    if active_entry:
        await message.answer(
            translate(
                "queue.already_in_queue",
                language,
                queue_number=active_entry.queue_number,
            )
        )
        await state.clear()
        return

    await state.set_state(QueueRegistration.waiting_for_iin)
    await message.answer(translate("bot.ask_iin", language))


@router.message(QueueRegistration.waiting_for_iin, F.text)
async def receive_iin(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return

    language = await get_user_language(
        message.from_user.id,
        fallback=telegram_language_to_supported(message.from_user.language_code),
    )
    iin = "".join(char for char in message.text.strip() if char.isdigit())
    if len(iin) != 12:
        await message.answer(translate("bot.invalid_iin", language))
        return

    await state.update_data(iin=iin)
    await state.set_state(QueueRegistration.waiting_for_photo)
    await message.answer(translate("bot.ask_photo", language))


@router.message(QueueRegistration.waiting_for_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.photo:
        return

    language = await get_user_language(
        message.from_user.id,
        fallback=telegram_language_to_supported(message.from_user.language_code),
    )
    state_data = await state.get_data()
    iin = state_data.get("iin")
    if not iin:
        await state.set_state(QueueRegistration.waiting_for_iin)
        await message.answer(translate("bot.ask_iin", language))
        return

    photos_dir = settings.media_root_path / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    photo_name = f"{message.from_user.id}_{message.message_id}.jpg"
    photo_path = photos_dir / photo_name
    await bot.download(message.photo[-1], destination=photo_path)

    async with async_session_factory() as session:
        entry, _ = await queue_service.join_queue(
            session=session,
            telegram_id=message.from_user.id,
            iin=iin,
            photo=f"photos/{photo_name}",
            language=language,
        )

    await state.clear()
    await message.answer(
        translate("queue.join_success", language, queue_number=entry.queue_number)
    )


@router.message(QueueRegistration.waiting_for_photo)
async def receive_invalid_photo(message: Message) -> None:
    if not message.from_user:
        return

    language = await get_user_language(
        message.from_user.id,
        fallback=telegram_language_to_supported(message.from_user.language_code),
    )
    await message.answer(translate("bot.ask_photo", language))
