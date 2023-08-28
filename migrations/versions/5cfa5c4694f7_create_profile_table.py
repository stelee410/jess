"""create profile table

Revision ID: 5cfa5c4694f7
Revises: 85ed13834890
Create Date: 2023-08-24 21:18:56.315979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cfa5c4694f7'
down_revision: Union[str, None] = '85ed13834890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profile',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('displayName', sa.String(100)),
        sa.Column('avatar', sa.String(100)),
        sa.Column('bot', sa.String(100)),
        sa.Column('description', sa.Text), #The system set for the profile
        sa.Column('message', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('profile')
