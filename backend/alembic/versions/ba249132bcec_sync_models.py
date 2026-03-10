"""sync models

Revision ID: ba249132bcec
Revises: 001_initial_schema
Create Date: 2026-03-08 16:29:57.800515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ba249132bcec'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('meetings', sa.Column('calendar_id', sa.String(length=256), nullable=True))
    op.add_column('meetings', sa.Column('external_id', sa.String(length=256), nullable=True))
    op.add_column('meetings', sa.Column('status', sa.String(length=32), nullable=True))
    op.add_column('meetings', sa.Column('meet_url', sa.String(length=1024), nullable=True))
    op.add_column('meetings', sa.Column('transcript', sa.Text(), nullable=True))
    op.add_column('meetings', sa.Column('transcript_path', sa.String(length=512), nullable=True))
    op.add_column('meetings', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('meetings', sa.Column('summary_key_points', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('meetings', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('meetings', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    pass
