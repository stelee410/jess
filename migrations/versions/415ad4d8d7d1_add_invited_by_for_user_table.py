"""add invited by for user table

Revision ID: 415ad4d8d7d1
Revises: 07e0a9bdcbb9
Create Date: 2023-09-15 16:03:24.580648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '415ad4d8d7d1'
down_revision: Union[str, None] = '07e0a9bdcbb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('invited_by', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('invitation_code', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('invitation_count', sa.Integer(), nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('user', 'invited_by')
    op.drop_column('user', 'invitation_code')
    op.drop_column('user', 'invitation_count')
