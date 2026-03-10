import asyncio
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.models.meeting import Meeting
from app.models.attendee import Attendee
from app.services.notification_service import NotificationService
from app.utils.datetime_utils import utcnow
from datetime import timedelta

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.notification_tasks.send_upcoming_reminders")
def send_upcoming_reminders():
    async def run():
        try:
            now = utcnow()
            start = now + timedelta(minutes=14)
            end = now + timedelta(minutes=16)
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(Meeting)
                    .options(selectinload(Meeting.attendees))
                    .where(
                        Meeting.start_time >= start,
                        Meeting.start_time <= end,
                        Meeting.status == "scheduled",
                    )
                )
                result = await session.execute(stmt)
                meetings = list(result.scalars().all())
                sent = 0
                for meeting in meetings:
                    to_notify = [a for a in meeting.attendees if a.notified_at is None and a.email]
                    if not to_notify:
                        continue
                    emails = [a.email for a in to_notify]
                    notif = NotificationService()
                    await notif.send_meeting_reminder(meeting, emails)
                    for a in to_notify:
                        a.notified_at = now
                    sent += len(emails)
                await session.commit()
                logger.info("send_upcoming_reminders_done", meetings=len(meetings), reminders_sent=sent)
                return {"meetings": len(meetings), "reminders_sent": sent}
        finally:
            await engine.dispose()

    return asyncio.run(run())


@celery_app.task(name="app.tasks.notification_tasks.send_summary_notification")
def send_summary_notification(meeting_id: str):
    async def run():
        try:
            mid = int(meeting_id)
            async with AsyncSessionLocal() as session:
                stmt = select(Meeting).options(selectinload(Meeting.attendees)).where(Meeting.id == mid)
                result = await session.execute(stmt)
                meeting = result.scalar_one_or_none()
                if not meeting:
                    logger.warning("send_summary_notification_meeting_not_found", meeting_id=mid)
                    return
                emails = [a.email for a in meeting.attendees if a.email]
                if emails:
                    notif = NotificationService()
                    await notif.send_summary_ready(meeting, emails)
                logger.info("send_summary_notification_done", meeting_id=mid)
        finally:
            await engine.dispose()

    return asyncio.run(run())
