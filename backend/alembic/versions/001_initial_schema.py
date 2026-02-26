"""initial_schema: tenants, meetings, attendees, action_items

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-02-25

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("google_credentials_encrypted", sa.Text(), nullable=True),
        sa.Column("notification_channels", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("retention_days", sa.Integer(), nullable=False, server_default="365"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("calendar_id", sa.String(256), nullable=True),
        sa.Column("external_id", sa.String(256), nullable=True),
        sa.Column("google_event_id", sa.String(256), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="scheduled"),
        sa.Column("meet_url", sa.String(1024), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("transcript_path", sa.String(512), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("summary_key_points", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meetings_external_id"), "meetings", ["external_id"], unique=True)
    op.create_index(op.f("ix_meetings_start_time"), "meetings", ["start_time"], unique=False)
    op.create_index(op.f("ix_meetings_status"), "meetings", ["status"], unique=False)

    op.create_table(
        "attendees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(256), nullable=False),
        sa.Column("name", sa.String(256), nullable=True),
        sa.Column("response_status", sa.String(32), nullable=True),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendees_meeting_id"), "attendees", ["meeting_id"], unique=False)
    op.create_index(op.f("ix_attendees_email"), "attendees", ["email"], unique=False)

    op.create_table(
        "action_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(1024), nullable=False),
        sa.Column("assignee_email", sa.String(256), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(16), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_action_items_meeting_id"), "action_items", ["meeting_id"], unique=False)
    op.create_index(op.f("ix_action_items_status"), "action_items", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_action_items_status"), table_name="action_items")
    op.drop_index(op.f("ix_action_items_meeting_id"), table_name="action_items")
    op.drop_table("action_items")
    op.drop_index(op.f("ix_attendees_email"), table_name="attendees")
    op.drop_index(op.f("ix_attendees_meeting_id"), table_name="attendees")
    op.drop_table("attendees")
    op.drop_index(op.f("ix_meetings_status"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_start_time"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_external_id"), table_name="meetings")
    op.drop_table("meetings")
    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")
