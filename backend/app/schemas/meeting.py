from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.attendee import AttendeeSchema
from app.schemas.action_item import ActionItemResponse


class MeetingBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    calendar_id: str = "primary"
    transcript: str | None = None
    notes: str | None = None


class MeetingCreate(MeetingBase):
    google_event_id: str | None = None
    external_id: str | None = None
    status: str = "scheduled"
    meet_url: str | None = None


class MeetingUpdate(BaseModel):
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    transcript: str | None = None
    transcript_path: str | None = None
    summary: str | None = None
    summary_key_points: dict | None = None
    notes: str | None = None
    status: str | None = None
    meet_url: str | None = None


class MeetingResponse(MeetingBase):
    id: int
    external_id: str | None
    google_event_id: str | None
    status: str
    meet_url: str | None
    recall_bot_id: str | None = None
    transcript_path: str | None
    summary: str | None
    summary_key_points: dict | None
    created_at: datetime
    updated_at: datetime
    attendees: list[AttendeeSchema] = []
    action_items: list[ActionItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SummaryStorePayload(BaseModel):
    summary: str
    key_points: list[str] | None = None
    decisions: list[str] | None = None
    action_items_summary: list[dict] | None = None
    follow_ups: list[str] | None = None
