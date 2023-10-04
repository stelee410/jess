"""sharing link table

Revision ID: b7ddae214070
Revises: eb38664f994d
Create Date: 2023-10-04 11:03:08.299772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7ddae214070'
down_revision: Union[str, None] = 'eb38664f994d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sharing_link',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(100)),
        sa.Column('profile_name', sa.String(100)),
        sa.Column('extra_description', sa.String(100)),
        sa.Column('link', sa.String(200)),
        sa.Column('status', sa.Integer),#0:active, 1:inactive
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )



def downgrade() -> None:
    op.drop_table('sharing_link')
