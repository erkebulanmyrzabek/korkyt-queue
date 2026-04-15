from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from app.bot.handlers.language import router as language_router
from app.bot.handlers.queue import router as queue_router
from app.bot.handlers.start import router as start_router
from app.core.config import settings
from app.db.init_db import init_db


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=settings.bot_parse_mode),
    )

    global_commands = [
        BotCommand(command="start", description="Join the queue"),
        BotCommand(command="queue", description="Check your queue position"),
        BotCommand(command="language", description="Choose interface language"),
    ]
    ru_commands = [
        BotCommand(command="start", description="Встать в очередь"),
        BotCommand(command="queue", description="Узнать позицию в очереди"),
        BotCommand(command="language", description="Выбрать язык"),
    ]
    kk_commands = [
        BotCommand(command="start", description="Кезекке тұру"),
        BotCommand(command="queue", description="Кезектегі орынды көру"),
        BotCommand(command="language", description="Тілді таңдау"),
    ]

    await bot.set_my_commands(commands=global_commands)
    await bot.set_my_commands(commands=ru_commands, language_code="ru")
    await bot.set_my_commands(commands=kk_commands, language_code="kk")

    dispatcher = Dispatcher()
    dispatcher.include_router(language_router)
    dispatcher.include_router(queue_router)
    dispatcher.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

