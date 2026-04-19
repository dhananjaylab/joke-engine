"""add app_logs table

Revision ID: add_app_logs_table
Revises: 9feabdec811e
Create Date: 2026-04-19 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_app_logs_table"
down_revision: Union[str, None] = "9feabdec811e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("level", sa.String(length=10), nullable=False),
        sa.Column("logger_name", sa.String(length=120), nullable=False),
        sa.Column("event", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("session_key", sa.String(length=64), nullable=True),
        sa.Column("joke_id", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Individual column indexes
    op.create_index("ix_app_logs_level",       "app_logs", ["level"])
    op.create_index("ix_app_logs_logger_name", "app_logs", ["logger_name"])
    op.create_index("ix_app_logs_event",       "app_logs", ["event"])
    op.create_index("ix_app_logs_session_key", "app_logs", ["session_key"])
    op.create_index("ix_app_logs_joke_id",     "app_logs", ["joke_id"])
    op.create_index("ix_app_logs_created_at",  "app_logs", ["created_at"])
    # Composite indexes for analytics queries
    op.create_index("ix_app_logs_level_created", "app_logs", ["level", "created_at"])
    op.create_index("ix_app_logs_event_created", "app_logs", ["event", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_app_logs_event_created", table_name="app_logs")
    op.drop_index("ix_app_logs_level_created", table_name="app_logs")
    op.drop_index("ix_app_logs_created_at",    table_name="app_logs")
    op.drop_index("ix_app_logs_joke_id",       table_name="app_logs")
    op.drop_index("ix_app_logs_session_key",   table_name="app_logs")
    op.drop_index("ix_app_logs_event",         table_name="app_logs")
    op.drop_index("ix_app_logs_logger_name",   table_name="app_logs")
    op.drop_index("ix_app_logs_level",         table_name="app_logs")
    op.drop_table("app_logs")
