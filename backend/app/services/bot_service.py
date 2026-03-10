import structlog
import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.meeting import Meeting
from app.tasks.notification_tasks import send_summary_notification
from app.services import nlp_service
from app.models.action_item import ActionItem
from sqlalchemy.orm import selectinload
from app.services.transcription_service import TranscriptionService

logger = structlog.get_logger()
settings = get_settings()

class BotService:
    def __init__(self):
        # We will need the user to provide this key in the .env later,
        # but for now we expect it in config.
        self.api_key = getattr(settings, "recall_api_key", None)
        self.base_url = "https://ap-northeast-1.recall.ai/api/v1/bot"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_bot(self, meeting_id: int):
        """Creates a Recall.ai bot to join the meeting."""
        if not self.api_key:
            logger.error("bot_recall_api_key_missing")
            return None

        async with AsyncSessionLocal() as session:
            stmt = select(Meeting).where(Meeting.id == meeting_id)
            result = await session.execute(stmt)
            meeting = result.scalar_one_or_none()
            
            if not meeting or not meeting.meet_url:
                logger.error("bot_meeting_invalid", meeting_id=meeting_id)
                return None
            
            meet_url = meeting.meet_url
            
        logger.info(
            "bot_creating_recall_bot", 
            meeting_id=meeting_id, 
            url=meet_url,
            start_time=meeting.start_time.isoformat() if meeting.start_time else None,
            timezone=meeting.start_time.tzname() if meeting.start_time else None
        )
        
        payload = {
            "meeting_url": meet_url,
            "bot_name": "MeetEdge Assistant",
            "metadata": {
                "internal_meeting_id": meeting_id
            }
        }
        
        # If the meeting has a start time in the future, tell the bot to join then.
        # Strict validation: `join_at` must be strictly in the future.
        now_utc = datetime.now(timezone.utc)
        if meeting.start_time and meeting.start_time > (now_utc + timedelta(minutes=1)):
            payload["join_at"] = meeting.start_time.isoformat()
        else:
            logger.info("bot_joining_immediately", meeting_id=meeting_id, start_time=meeting.start_time.isoformat() if meeting.start_time else None)
        
        async with httpx.AsyncClient() as client:
            try:
                # Add trailing slash for POST /api/v1/bot/ as it is sometimes required
                endpoint_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"
                response = await client.post(endpoint_url, json=payload, headers=self.headers, timeout=10.0)
                
                # Log the API response per user request
                logger.info("bot_recall_api_response", status_code=response.status_code, body=response.text)
                
                response.raise_for_status()
                data = response.json()
                bot_id = data.get("id")
                
                logger.info("bot_recall_created_successfully", bot_id=bot_id, meeting_id=meeting_id)
                return bot_id
                
            except httpx.HTTPError as e:
                error_body = getattr(e.response, 'text', '') if hasattr(e, 'response') else ""
                logger.error("bot_recall_creation_failed", error=str(e), body=error_body)
                # Update status back to scheduled so it can be retried or marked failed
                return None

    async def fetch_transcript(self, bot_id: str, meeting_id: int):
        """Fetches the transcript for a completed bot and saves it."""
        if not self.api_key:
            return None
            
        logger.info("bot_fetching_transcript", bot_id=bot_id, meeting_id=meeting_id)
        transcript_url = f"{self.base_url}/{bot_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(transcript_url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Format transcript from chunks
                # Recall API returns a list of dictionaries in 'transcripts'
                transcripts_list = data.get("transcripts", [])
                
                # If there are no transcripts from Recall (or it's still processing),
                # attempt a local transcription fallback (if a recorded file path exists)
                if not transcripts_list:
                    logger.info("bot_no_transcript_from_recall", bot_id=bot_id)
                    # Try fallback: use Meeting.transcript_path if present
                    async with AsyncSessionLocal() as session:
                        stmt = select(Meeting).where(Meeting.id == meeting_id)
                        result = await session.execute(stmt)
                        meeting = result.scalar_one_or_none()
                        if meeting and meeting.transcript_path:
                            try:
                                ts = TranscriptionService()
                                # request both Hindi and English as hints
                                res = await ts.transcribe_audio(meeting.transcript_path, languages=["hi-IN", "en-US"])
                                transcript_text = res.get("text", "")
                            except Exception as e:
                                logger.error("fallback_transcription_failed", meeting_id=meeting_id, error=str(e))
                                transcript_text = ""
                        else:
                            transcript_text = ""

                    if not transcript_text:
                        logger.info("bot_no_transcript_captured", bot_id=bot_id)
                        return False

                words = []
                for entry in transcripts_list:
                    words.extend(entry.get("words", []))
                    
                transcript_text = " ".join([w.get("text", "") for w in words])
                
                if transcript_text:
                    logger.info("bot_saving_transcript", length=len(transcript_text))
                    async with AsyncSessionLocal() as session:
                        await session.execute(
                            update(Meeting)
                            .where(Meeting.id == meeting_id)
                            .values(
                                transcript=transcript_text, 
                                status="completed", 
                                updated_at=datetime.now(timezone.utc)
                            )
                        )
                        await session.commit()

                    # Post-process transcript: summarization and action-item extraction
                    try:
                        async with AsyncSessionLocal() as session:
                            stmt = select(Meeting).options(selectinload(Meeting.attendees)).where(Meeting.id == meeting_id)
                            result = await session.execute(stmt)
                            meeting = result.scalar_one_or_none()

                            if meeting:
                                attendees = [{"name": a.name or "", "email": a.email} for a in meeting.attendees]

                                # Prefer LLM-based summarization/extraction when available
                                try:
                                    from app.services.llm_service import LLMService
                                    llm = LLMService()
                                except Exception:
                                    llm = None

                                summary = None
                                key_points = []
                                action_items = []

                                if llm and llm.available:
                                    try:
                                        llm_result = llm.summarize_and_extract(transcript_text, attendees)
                                        if llm_result:
                                            summary = llm_result.get("summary")
                                            key_points = llm_result.get("key_points") or []
                                            action_items = llm_result.get("action_items") or []
                                    except Exception as e:
                                        logger.error("llm_processing_failed", meeting_id=meeting_id, error=str(e))

                                # Fallback to rule-based NLP if LLM not available or failed
                                if not summary:
                                    summary, key_points = nlp_service.summarize_transcript(transcript_text)
                                    action_items = nlp_service.extract_action_items(transcript_text, attendees)

                                # Update meeting summary
                                await session.execute(
                                    update(Meeting)
                                    .where(Meeting.id == meeting_id)
                                    .values(summary=summary, summary_key_points=key_points)
                                )

                                # Insert action items into DB (avoid duplicates)
                                for ai in action_items:
                                    text = ai.get("text")
                                    assignee = ai.get("assignee_email")
                                    exists_stmt = select(ActionItem).where(
                                        ActionItem.meeting_id == meeting_id,
                                        ActionItem.text == text
                                    )
                                    exists_res = await session.execute(exists_stmt)
                                    existing = exists_res.scalar_one_or_none()
                                    if existing:
                                        continue
                                    new_ai = ActionItem(meeting_id=meeting_id, text=text, assignee_email=assignee)
                                    session.add(new_ai)

                                await session.commit()
                    except Exception as e:
                        logger.error("postprocess_transcript_failed", meeting_id=meeting_id, error=str(e))

                    # Trigger summary notification
                    send_summary_notification.delay(meeting_id)
                    return True
                else:
                    logger.info("bot_no_transcript_captured", bot_id=bot_id)
                    return False
                    
            except httpx.HTTPError as e:
                error_body = getattr(e.response, 'text', '') if hasattr(e, 'response') else ""
                logger.error("bot_transcript_fetch_failed", error=str(e), body=error_body)
                return False
