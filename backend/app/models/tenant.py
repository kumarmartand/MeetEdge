import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime
from sqlalchemy import JSON as SAJSON

# Use portable SQLAlchemy types in models so the test suite (SQLite) can
# create the schema. Production migrations can still use PostgreSQL-specific
# JSONB in alembic migration files when deploying to Postgres.
JSON_TYPE = SAJSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"
    # Store UUIDs as strings for portability across SQLite (tests) and Postgres
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    google_credentials_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    notification_channels: Mapped[dict] = mapped_column(JSON_TYPE, default=dict, nullable=False)
    retention_days: Mapped[int] = mapped_column(Integer, default=365, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
