"""add table user_profile_rel

Revision ID: 07e0a9bdcbb9
Revises: afe099b8da71
Create Date: 2023-09-11 14:13:11.374855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07e0a9bdcbb9'
down_revision: Union[str, None] = 'afe099b8da71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_profile_rel',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(100)),
        sa.Column('profile_name', sa.String(100)),
        sa.Column('last_chat_at', sa.DateTime, default=sa.func.now()),
        sa.Column('number_of_chats', sa.Integer, default=0),
        sa.Column('relations', sa.Integer, default=0),  #0: stranger, 1: friends, 2: close friends
    )


def downgrade() -> None:
    op.drop_table('user_profile_rel')
