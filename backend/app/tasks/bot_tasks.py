import asyncio
from datetime import timedelta
import structlog
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.meeting import Meeting
from app.tasks.celery_app import celery_app
from app.services.bot_service import BotService
from app.utils.datetime_utils import utcnow
from app.tasks.celery_app import celery_app
from app.services.bot_service import BotService

logger = structlog.get_logger()

@celery_app.task(name="app.tasks.bot_tasks.join_meeting_bot", bind=True, max_retries=1)
def join_meeting_bot(self, meeting_id: int):
    """
    Requests Recall.ai to join the meeting.
    """
    logger.info("bot_task_started", meeting_id=meeting_id)
    
    async def run():
        bot_created = False
        try:
            bot = BotService()
            bot_id = await bot.create_bot(meeting_id)
            
            # Save the bot_id to meeting record so we can poll for it
            if bot_id:
                bot_created = True
                from sqlalchemy import update
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    await session.execute(
                        update(Meeting)
                        .where(Meeting.id == meeting_id)
                        .values(recall_bot_id=bot_id)
                    )
                    await session.commit()
        except Exception as e:
            logger.exception("bot_task_failed", error=str(e))
            if not bot_created:
                # If bot failed to create, revert status to scheduled so it gets picked up again
                from sqlalchemy import update
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    await session.execute(
                        update(Meeting)
                        .where(Meeting.id == meeting_id)
                        .values(status="scheduled")
                    )
                    await session.commit()
            raise
        finally:
            from app.core.database import engine
            await engine.dispose()
            
    try:
        asyncio.run(run())
    except Exception as e:
        pass # Already logged and reraised in run()

@celery_app.task(name="app.tasks.bot_tasks.check_upcoming_meetings_for_bot")
def check_upcoming_meetings_for_bot():
    """
    Runs every minute. Finds meetings starting in <= 2 minutes (or already started)
    that are still 'scheduled'. Dispatches join_meeting_bot.
    """
    logger.info("checking_meetings_for_bot")
    
    async def run():
        try:
            now = utcnow()
            start_window = now + timedelta(minutes=2)
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                # Find meetings starting within 2 mins, or that are currently active
                stmt = select(Meeting).where(
                    Meeting.start_time <= start_window,
                    Meeting.end_time >= now,
                    Meeting.status == "scheduled", 
                    Meeting.meet_url.is_not(None)
                )
                result = await session.execute(stmt)
                meetings = result.scalars().all()
                
                dispatched = 0
                for meeting in meetings:
                    logger.info("dispatching_bot", meeting_id=meeting.id, title=meeting.title)
                    # We update status to 'in_progress' so we don't dispatch twice
                    meeting.status = "in_progress"
                    join_meeting_bot.delay(meeting.id)
                    dispatched += 1
                    
                if dispatched > 0:
                    await session.commit()
            
            return dispatched
        finally:
            from app.core.database import engine
            await engine.dispose()
                
    try:
        dispatched_count = asyncio.run(run())
        return {"dispatched": dispatched_count}
    except Exception as e:
        logger.error("check_upcoming_meetings_for_bot_failed", error=str(e))

@celery_app.task(name="app.tasks.bot_tasks.check_bot_status")
def check_bot_status():
    """
    Runs every minute. Finds meetings in 'in_progress' state with a recall_bot_id,
    checks if bot is done, and triggers trace retrieval.
    """
    logger.info("checking_bot_status")
    
    async def run():
        try:
            bot_service = BotService()
            if not bot_service.api_key:
                return {"error": "no_api_key"}

            from app.core.database import AsyncSessionLocal
            import httpx
            
            processed = 0
            async with AsyncSessionLocal() as session:
                # Fetch meetings in progress that have a bot ID
                stmt = select(Meeting).where(
                    Meeting.status == "in_progress",
                    Meeting.recall_bot_id.is_not(None)
                )
                result = await session.execute(stmt)
                meetings = result.scalars().all()
                
                if not meetings:
                    return 0

                async with httpx.AsyncClient() as client:
                    for meeting in meetings:
                        try:
                            # Check status from Recall API
                            url = f"https://ap-northeast-1.recall.ai/api/v1/bot/{meeting.recall_bot_id}"
                            resp = await client.get(url, headers=bot_service.headers, timeout=5.0)
                            if resp.status_code == 200:
                                bot_data = resp.json()
                                # 'done' could mean finished processing
                                if bot_data.get("status_changes"):
                                    latest_status = bot_data["status_changes"][-1].get("code")
                                    if latest_status in ["done", "fatal"]:
                                        logger.info("bot_finished", meeting_id=meeting.id, status=latest_status)
                                        await bot_service.fetch_transcript(meeting.recall_bot_id, meeting.id)
                                        processed += 1
                        except Exception as e:
                            logger.error("bot_status_check_failed", meeting_id=meeting.id, error=str(e))

            return processed
        finally:
            from app.core.database import engine
            await engine.dispose()
                
    try:
        processed_count = asyncio.run(run())
        return {"processed": processed_count}
    except Exception as e:
        logger.error("check_bot_status_failed", error=str(e))
