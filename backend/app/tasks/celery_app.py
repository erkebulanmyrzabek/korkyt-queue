from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "korkyt_queue",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_default_queue="korkyt",
    timezone="Asia/Almaty",
    enable_utc=True,
    beat_schedule={
        "queue-notification-check": {
            "task": "app.tasks.notifications.check_queue_notifications",
            "schedule": 30.0,
        }
    },
)

celery_app.autodiscover_tasks(["app.tasks"])

