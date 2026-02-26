from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.attendee import Attendee
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.utils.datetime_utils import utcnow, is_within_minutes

from datetime import timedelta


class MeetingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Meeting]:
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.attendees), selectinload(Meeting.action_items))
            .order_by(Meeting.start_time.desc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            stmt = stmt.where(Meeting.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, meeting_id: int) -> Meeting | None:
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.attendees), selectinload(Meeting.action_items))
            .where(Meeting.id == meeting_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Meeting | None:
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.attendees), selectinload(Meeting.action_items))
            .where(Meeting.external_id == external_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: MeetingCreate) -> Meeting:
        meeting = Meeting(**data.model_dump())
        self.db.add(meeting)
        await self.db.flush()
        await self.db.refresh(meeting)
        return meeting

    async def update(self, meeting_id: int, data: MeetingUpdate) -> Meeting | None:
        meeting = await self.get_by_id(meeting_id)
        if not meeting:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(meeting, k, v)
        await self.db.flush()
        await self.db.refresh(meeting)
        return meeting

    async def delete(self, meeting_id: int) -> bool:
        meeting = await self.get_by_id(meeting_id)
        if not meeting:
            return False
        await self.db.delete(meeting)
        await self.db.flush()
        return True

    async def get_upcoming(self, minutes_ahead: int = 20) -> list[Meeting]:
        now = utcnow()
        end = now + timedelta(minutes=minutes_ahead)
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.attendees), selectinload(Meeting.action_items))
            .where(
                Meeting.start_time >= now,
                Meeting.start_time <= end,
                Meeting.status == "scheduled",
            )
            .order_by(Meeting.start_time.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_notified(self, meeting_id: int, attendee_email: str) -> None:
        stmt = select(Attendee).where(
            Attendee.meeting_id == meeting_id,
            Attendee.email == attendee_email,
        )
        result = await self.db.execute(stmt)
        att = result.scalar_one_or_none()
        if att:
            att.notified_at = utcnow()
            await self.db.flush()

    async def search(self, query: str, limit: int = 20) -> list[Meeting]:
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.attendees), selectinload(Meeting.action_items))
            .where(Meeting.title.ilike(f"%{query}%"))
            .order_by(Meeting.start_time.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
