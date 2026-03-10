"""
Gmail push processing: fetch history, parse new messages, extract calendar invites, upsert meetings, notify.
See GMAIL_SETUP.md. Expand process_gmail_push as needed (e.g. fetch .ics, find Meet URL, email attendees).
"""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.gmail_tasks.process_gmail_push", bind=True, max_retries=3)
def process_gmail_push(self, history_id: str):
    """
    Process Gmail push notification: sync calendar.
    """
    import asyncio
    import structlog
    from app.core.database import AsyncSessionLocal
    from app.services.calendar_service import CalendarService
    
    log = structlog.get_logger()
    log.info("gmail_push_received", history_id=history_id)
    
    async def run():
        try:
            from app.core.database import AsyncSessionLocal, engine
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
        log.info("gmail_push_processed", synced=result.get("synced", 0))
        return {"history_id": history_id, "processed": True, "result": result}
    except Exception as e:
        log.exception("gmail_push_failed", error=str(e))
        raise self.retry(exc=e, countdown=30)
