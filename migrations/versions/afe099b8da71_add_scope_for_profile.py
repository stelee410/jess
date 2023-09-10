"""add scope for profile

Revision ID: afe099b8da71
Revises: dc777cb48ea9
Create Date: 2023-09-10 16:11:41.484654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afe099b8da71'
down_revision: Union[str, None] = 'dc777cb48ea9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profile', sa.Column('scope', sa.Integer, nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('profile', 'scope')
