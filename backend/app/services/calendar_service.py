import re
import structlog
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.meeting import Meeting
from app.models.attendee import Attendee
from app.utils.datetime_utils import parse_google_datetime, utcnow
from app.utils.google_auth import load_credentials

logger = structlog.get_logger()


class CalendarService:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self.settings = get_settings()

    def _get_credentials(self) -> Any:
        try:
            return load_credentials()
        except FileNotFoundError as e:
            logger.warning("google_credentials_missing", path=str(e))
            return None
        except Exception as e:
            logger.exception("google_credentials_load_error", error=str(e))
            return None

    def check_auth(self) -> bool:
        return self._get_credentials() is not None

    def _get_service(self) -> Any:
        from googleapiclient.discovery import build
        creds = self._get_credentials()
        if not creds:
            return None
        return build("calendar", "v3", credentials=creds)

    def _extract_meet_url(self, event: dict) -> str | None:
        entry_points = (event.get("conferenceData") or {}).get("entryPoints") or []
        for ep in entry_points:
            if ep.get("entryPointType") == "video" and ep.get("uri"):
                return ep["uri"]
        for field in [event.get("description") or "", event.get("location") or ""]:
            match = re.search(r"https?://meet\.google\.com/[a-z\-]+", field, re.I)
            if match:
                return match.group(0)
        return None

    def fetch_upcoming_events(self, hours_ahead: int | None = None) -> list[dict]:
        service = self._get_service()
        if not service:
            return []
        try:
            now = utcnow()
            end = now + timedelta(hours=hours_ahead or 168)
            time_min = now.isoformat().replace("+00:00", "Z")
            time_max = end.isoformat().replace("+00:00", "Z")
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            items = events_result.get("items", [])
            result = []
            for ev in items:
                meet_url = self._extract_meet_url(ev)
                if not meet_url:
                    continue
                start_info = ev.get("start") or {}
                end_info = ev.get("end") or {}
                start_str = start_info.get("dateTime") or start_info.get("date")
                end_str = end_info.get("dateTime") or end_info.get("date")
                if not start_str or not end_str:
                    continue
                result.append(ev)
            return result
        except Exception as e:
            from googleapiclient.errors import HttpError
            if isinstance(e, HttpError):
                logger.error("google_calendar_http_error", status=e.resp.status, content=str(e))
                raise
            logger.exception("fetch_upcoming_events_error", error=str(e))
            return []

    async def _upsert_meeting(self, event: dict) -> tuple[Meeting, bool]:
        start_info = event.get("start") or {}
        end_info = event.get("end") or {}
        start_str = start_info.get("dateTime") or start_info.get("date")
        end_str = end_info.get("dateTime") or end_info.get("date")
        start_dt = parse_google_datetime(start_str)
        end_dt = parse_google_datetime(end_str)
        external_id = event.get("id")
        
        existing_stmt = select(Meeting.id).where(Meeting.external_id == external_id)
        existing_result = await self.db.execute(existing_stmt)
        is_new = existing_result.scalar_one_or_none() is None

        title = event.get("summary") or "Untitled"
        meet_url = self._extract_meet_url(event)
        stmt = insert(Meeting).values(
            external_id=external_id,
            google_event_id=external_id,
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            calendar_id="primary",
            status="scheduled",
            meet_url=meet_url,
        ).on_conflict_do_update(
            index_elements=["external_id"],
            set_={
                "title": title,
                "start_time": start_dt,
                "end_time": end_dt,
                "meet_url": meet_url,
                "updated_at": utcnow(),
            },
        ).returning(Meeting)
        result = await self.db.execute(stmt)
        row = result.scalar_one()
        await self.db.flush()
        return row, is_new

    async def _upsert_attendees(self, meeting: Meeting, attendees: list[dict]) -> None:
        emails = {a.get("email") for a in attendees if a.get("email")}
        for email in emails:
            stmt = select(Attendee).where(
                Attendee.meeting_id == meeting.id,
                Attendee.email == email,
            )
            r = await self.db.execute(stmt)
            if r.scalar_one_or_none():
                continue
            self.db.add(
                Attendee(
                    meeting_id=meeting.id,
                    email=email,
                    name=next((a.get("displayName") for a in attendees if a.get("email") == email), None),
                    response_status=next((a.get("responseStatus") for a in attendees if a.get("email") == email), None),
                )
            )
        await self.db.flush()

    async def sync_upcoming_meetings(self) -> dict[str, int]:
        if not self.db:
            return {"synced": 0, "skipped": 0}
        try:
            events = self.fetch_upcoming_events(hours_ahead=168)
        except Exception:
            raise
        synced = 0
        skipped = 0
        for event in events:
            try:
                meeting, is_new = await self._upsert_meeting(event)
                attendees = event.get("attendees") or []
                await self._upsert_attendees(meeting, attendees)
                
                if is_new and meeting.meet_url:
                    from app.services.notification_service import NotificationService
                    
                    creator_email = event.get("creator", {}).get("email")
                    organizer_email = event.get("organizer", {}).get("email")
                    target_email = organizer_email or creator_email
                    
                    if target_email:
                        notif = NotificationService()
                        await notif.send_bot_joining_email(meeting, [target_email])
                        
                synced += 1
            except Exception as e:
                logger.warning("sync_meeting_skip", event_id=event.get("id"), error=str(e))
                skipped += 1
        logger.info("calendar_sync_done", synced=synced, skipped=skipped)
        return {"synced": synced, "skipped": skipped}
