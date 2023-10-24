"""add saved_flag for chat history

Revision ID: 662bee5b4d31
Revises: b7ddae214070
Create Date: 2023-10-24 16:42:45.909641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '662bee5b4d31'
down_revision: Union[str, None] = 'b7ddae214070'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_history', sa.Column('saved_flag', sa.Integer, default=0))

def downgrade() -> None:
    op.drop_column('chat_history', 'saved_flag')
