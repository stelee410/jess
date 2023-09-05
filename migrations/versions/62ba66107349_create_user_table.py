"""create user table

Revision ID: 62ba66107349
Revises: 5cfa5c4694f7
Create Date: 2023-09-05 17:25:57.765719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62ba66107349'
down_revision: Union[str, None] = '5cfa5c4694f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(100)),
        sa.Column('displayName', sa.String(100)),
        sa.Column('password', sa.String(100)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
def downgrade() -> None:
    op.drop_table('user')
