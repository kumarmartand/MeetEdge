from celery import Celery
from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "meetedge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.calendar_tasks", "app.tasks.notification_tasks", "app.tasks.gmail_tasks", "app.tasks.bot_tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "poll_calendar_every_10m": {
        "task": "app.tasks.calendar_tasks.poll_calendar",
        "schedule": crontab(minute="*/10"),
    },
    "send_reminders_every_1m": {
        "task": "app.tasks.notification_tasks.send_upcoming_reminders",
        "schedule": crontab(minute="*/1"),
    },
    "check_bot_join_every_1m": {
        "task": "app.tasks.bot_tasks.check_upcoming_meetings_for_bot",
        "schedule": crontab(minute="*/1"),
    },
    "check_bot_status_every_1m": {
        "task": "app.tasks.bot_tasks.check_bot_status",
        "schedule": crontab(minute="*/1"),
    },
}
