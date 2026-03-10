import asyncio
import structlog
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.calendar_service import CalendarService

logger = structlog.get_logger()


@celery_app.task(name="app.tasks.calendar_tasks.poll_calendar", bind=True, max_retries=3)
def poll_calendar(self):
    async def run():
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                svc = CalendarService(db=session)
                result = await svc.sync_upcoming_meetings()
                await session.commit()
                return result
        finally:
            from app.core.database import engine
            await engine.dispose()
            
    try:
        result = asyncio.run(run())
        logger.info("poll_calendar_done", synced=result.get("synced", 0), skipped=result.get("skipped", 0))
        return result
    except Exception as e:
        logger.exception("poll_calendar_failed", error=str(e))
        countdown = 30 * (self.request.retries + 1)
        raise self.retry(exc=e, countdown=countdown)
