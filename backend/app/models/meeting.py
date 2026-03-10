from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy import JSON as SAJSON

# Use generic JSON type for portability with SQLite tests.
JSON_TYPE = SAJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    calendar_id: Mapped[str] = mapped_column(String(256), default="primary")
    external_id: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True, index=True)
    google_event_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="scheduled", nullable=False, index=True)
    meet_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_key_points: Mapped[dict | None] = mapped_column(JSON_TYPE, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recall_bot_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    attendees: Mapped[list["Attendee"]] = relationship("Attendee", back_populates="meeting", cascade="all, delete-orphan")
    action_items: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
