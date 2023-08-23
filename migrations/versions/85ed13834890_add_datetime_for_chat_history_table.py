"""add datetime for  chat_history_table

Revision ID: 85ed13834890
Revises: 89928c3298bf
Create Date: 2023-08-23 13:56:38.566943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85ed13834890'
down_revision: Union[str, None] = '89928c3298bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_history', sa.Column('created_at', sa.DateTime, default=sa.func.now()))


def downgrade() -> None:
    op.drop_column('chat_history', 'created_at')
