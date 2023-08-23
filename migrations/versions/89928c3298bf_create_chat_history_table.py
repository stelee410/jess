"""create chat_history_table

Revision ID: 89928c3298bf
Revises: 
Create Date: 2023-08-23 11:15:00.343793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89928c3298bf'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(10)),
        sa.Column('name', sa.String(100)),
        sa.Column('message', sa.String(1000)),
    )


def downgrade() -> None:
    op.drop_table('chat_history')
