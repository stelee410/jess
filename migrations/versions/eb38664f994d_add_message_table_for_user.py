"""add message table for user

Revision ID: eb38664f994d
Revises: 73a190b407f7
Create Date: 2023-10-01 19:19:43.722891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb38664f994d'
down_revision: Union[str, None] = '73a190b407f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.create_table(
        "message",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("receiver", sa.String(100), nullable=False),#username for receiver
        sa.Column("sender", sa.String(100), nullable=False),#username for sender
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now()),
        sa.Column("status", sa.Integer, nullable=False, default=0),#0:unread,1:read,2:deleted,3:archived
     )


def downgrade() -> None:
    op.drop_table("message")
