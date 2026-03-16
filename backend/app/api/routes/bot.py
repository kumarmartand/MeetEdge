from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
import structlog
from app.services.bot_service import BotService
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.meeting import Meeting

logger = structlog.get_logger()
router = APIRouter(prefix="/bot", tags=["bot"])

@router.post("/webhook")
async def recall_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive events from Recall.ai.
    Expects payload containing bot status changes.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event")
    data = payload.get("data", {})
    bot_id = data.get("bot_id")
    
    logger.info("recall_webhook_received", event_type=event_type, bot_id=bot_id)

    if event_type == "bot.status_change" and bot_id:
        status_code = data.get("status", {}).get("code")
        
        # When bot is done or fatal, fetch transcript and process
        if status_code in ["done", "fatal"]:
            logger.info("bot_completed_via_webhook", bot_id=bot_id, status=status_code)
            
            # Find the meeting associated with this bot_id
            async with AsyncSessionLocal() as session:
                stmt = select(Meeting).where(Meeting.recall_bot_id == bot_id)
                result = await session.execute(stmt)
                meeting = result.scalar_one_or_none()
                
                if meeting:
                    # Run the transcript fetching and summarization in the background
                    bot_service = BotService()
                    background_tasks.add_task(bot_service.fetch_transcript, bot_id, meeting.id)
                else:
                    logger.warning("webhook_meeting_not_found", bot_id=bot_id)

    return {"status": "received"}
