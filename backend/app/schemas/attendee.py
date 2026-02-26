from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttendeeBase(BaseModel):
    email: str
    name: str | None = None
    response_status: str | None = None


class AttendeeCreate(AttendeeBase):
    meeting_id: int


class AttendeeUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    response_status: str | None = None


class AttendeeSchema(AttendeeBase):
    id: int
    meeting_id: int
    notified_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
