"""add more columns for user table

Revision ID: b87ab078ae07
Revises: 6e376c676546
Create Date: 2023-09-06 10:00:32.260826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b87ab078ae07'
down_revision: Union[str, None] = '6e376c676546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('avatar', sa.String, nullable=False, server_default='images/default.png'))
    op.add_column('user', sa.Column('description', sa.Text, nullable=True, server_default=''))


def downgrade() -> None:
    op.drop_column('user', 'avatar')
    op.drop_column('user', 'description')
