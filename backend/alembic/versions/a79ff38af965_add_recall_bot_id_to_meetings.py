"""Add recall_bot_id to meetings

Revision ID: a79ff38af965
Revises: ba249132bcec
Create Date: 2026-03-09 10:43:57.691128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a79ff38af965'
down_revision: Union[str, None] = 'ba249132bcec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('meetings', sa.Column('recall_bot_id', sa.String(length=128), nullable=True))

def downgrade() -> None:
    op.drop_column('meetings', 'recall_bot_id')
