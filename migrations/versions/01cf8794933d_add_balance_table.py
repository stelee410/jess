"""add balance table

Revision ID: 01cf8794933d
Revises: 415ad4d8d7d1
Create Date: 2023-09-26 10:11:10.087009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01cf8794933d'
down_revision: Union[str, None] = '415ad4d8d7d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "balance",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id")),
        sa.Column("balance", sa.Integer, default=0),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("user.id")),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("created_with", sa.String(128))
    )


def downgrade() -> None:
    op.drop_table("balance")
