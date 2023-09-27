"""add short description for profile table

Revision ID: 73a190b407f7
Revises: 01cf8794933d
Create Date: 2023-09-27 13:05:30.903921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73a190b407f7'
down_revision: Union[str, None] = '01cf8794933d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profile', sa.Column('short_description', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('profile','short_description')
