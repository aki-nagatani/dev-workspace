"""Add operations monitoring and logging specs"""

from __future__ import annotations

from typing import Iterable, Mapping

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "f3c86ad5df8c"
down_revision = "b84f8d8f4ef1"
branch_labels = None
depends_on = None

TABLES = {
    "ops_monitoring": {
        "desc": "High level monitoring events (aggregated counters)",
        "columns": [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("scope", sa.String(length=128), nullable=True),
            sa.Column("occurrences", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("first_seen_at", sa.DateTime(), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(), nullable=False),
            sa.Column("last_payload", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        ],
        "indexes": [
            ("idx_ops_monitoring_event", ("event_type", "status", "last_seen_at")),
            ("idx_ops_monitoring_scope", ("scope", "status")),
        ],
        "check": sa.CheckConstraint("status IN ('OPEN', 'ACK', 'CLOSED')", name="ck_ops_monitoring_status"),
    },
    "ops_job_log": {
        "desc": "Per job execution log for background jobs",
        "columns": [
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("job_name", sa.String(length=64), nullable=False),
            sa.Column("entity_type", sa.String(length=64), nullable=True),
            sa.Column("entity_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.Column("error_code", sa.String(length=128), nullable=True),
            sa.Column("error_detail", sa.Text(), nullable=True),
            sa.Column("payload", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        ],
        "indexes": [
            ("idx_ops_job_log_job", ("job_name", "started_at")),
            ("idx_ops_job_log_entity", ("entity_type", "entity_id")),
            ("idx_ops_job_log_status", ("status", "started_at")),
        ],
        "check": sa.CheckConstraint("status IN ('SUCCESS', 'FAILURE', 'TIMEOUT', 'SKIPPED')", name="ck_ops_job_log_status"),
    },
}


# -- helpers --

def _has_table(inspector: sa.inspect, table_name: str) -> bool:
    try:
        return inspector.has_table(table_name)
    except Exception:  # pragma: no cover
        return False


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if _has_table(inspector, "ops_monitoring"):
        return  # already present

    op.create_table(
        "ops_monitoring",
        *TABLES["ops_monitoring"]["columns"],
        TABLES["ops_monitoring"]["check"],
    )
    for idx_name, columns in TABLES["ops_monitoring"]["indexes"]:
        op.create_index(idx_name, "ops_monitoring", list(columns))

    op.create_table(
        "ops_job_log",
        *TABLES["ops_job_log"]["columns"],
        TABLES["ops_job_log"]["check"],
    )
    for idx_name, columns in TABLES["ops_job_log"]["indexes"]:
        op.create_index(idx_name, "ops_job_log", list(columns))



def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if _has_table(inspector, "ops_job_log"):
        for idx_name, _ in TABLES["ops_job_log"]["indexes"]:
            op.drop_index(idx_name, table_name="ops_job_log")
        op.drop_table("ops_job_log")
    if _has_table(inspector, "ops_monitoring"):
        for idx_name, _ in TABLES["ops_monitoring"]["indexes"]:
            op.drop_index(idx_name, table_name="ops_monitoring")
        op.drop_table("ops_monitoring")
