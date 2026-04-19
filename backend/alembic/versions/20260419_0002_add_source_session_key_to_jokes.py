"""add source and session_key columns to jokes

Revision ID: add_source_session_key_jokes
Revises: add_app_logs_table
Create Date: 2026-04-19 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "add_source_session_key_jokes"
down_revision: Union[str, None] = "add_app_logs_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # source — tracks which pipeline produced the joke
    op.add_column(
        "jokes",
        sa.Column("source", sa.String(length=40), nullable=False, server_default="ai_generated"),
    )
    op.create_index("ix_jokes_source", "jokes", ["source"])

    # session_key — links joke to the user session that triggered it
    op.add_column(
        "jokes",
        sa.Column("session_key", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_jokes_session_key", "jokes", ["session_key"])

    # Widen query column from 100 → 200 to accommodate longer composite keys
    op.alter_column("jokes", "query", type_=sa.String(length=200), existing_nullable=False)


def downgrade() -> None:
    op.alter_column("jokes", "query", type_=sa.String(length=100), existing_nullable=False)
    op.drop_index("ix_jokes_session_key", table_name="jokes")
    op.drop_column("jokes", "session_key")
    op.drop_index("ix_jokes_source", table_name="jokes")
    op.drop_column("jokes", "source")
