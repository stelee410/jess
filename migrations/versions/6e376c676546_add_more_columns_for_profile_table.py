"""add more columns for profile table

Revision ID: 6e376c676546
Revises: 62ba66107349
Create Date: 2023-09-05 18:34:40.324583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e376c676546'
down_revision: Union[str, None] = '62ba66107349'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



# Define the upgrade function
def upgrade():
    op.add_column('profile', sa.Column('offline', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('profile', sa.Column('deleted', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('profile', sa.Column('owned_by', sa.String(length=50), nullable=False, server_default='stelee'))


# Define the downgrade function
def downgrade():
    op.drop_column('profile', 'offline')
    op.drop_column('profile', 'deleted')
    op.drop_column('profile', 'owned_by')
