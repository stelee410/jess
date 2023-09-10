"""alter message column of chat history to text

Revision ID: dc777cb48ea9
Revises: b87ab078ae07
Create Date: 2023-09-08 19:54:07.792229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc777cb48ea9'
down_revision: Union[str, None] = 'b87ab078ae07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('chat_history', 'message', type_=sa.Text)


def downgrade() -> None:
    op.alter_column('chat_history', 'message', type_=sa.String(1000))
