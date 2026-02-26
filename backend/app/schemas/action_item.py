from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActionItemBase(BaseModel):
    text: str
    assignee_email: str | None = None
    due_date: datetime | None = None
    status: str = "open"
    priority: str | None = "medium"


class ActionItemCreate(ActionItemBase):
    meeting_id: int


class ActionItemUpdate(BaseModel):
    text: str | None = None
    assignee_email: str | None = None
    due_date: datetime | None = None
    status: str | None = None
    priority: str | None = None
    completed: bool | None = None


class ActionItemResponse(ActionItemBase):
    id: int
    meeting_id: int
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
