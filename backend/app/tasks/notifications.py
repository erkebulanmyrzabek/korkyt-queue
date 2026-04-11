from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notifications.send_telegram_message")
def send_telegram_message(chat_id: int, text: str) -> None:
    logger.info("Queued telegram message for %s: %s", chat_id, text)


@celery_app.task(name="app.tasks.notifications.check_queue_notifications")
def check_queue_notifications() -> None:
    logger.info("Queue proximity notification sweep executed.")

