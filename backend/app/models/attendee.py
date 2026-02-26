from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Attendee(Base):
    __tablename__ = "attendees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    response_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="attendees")
