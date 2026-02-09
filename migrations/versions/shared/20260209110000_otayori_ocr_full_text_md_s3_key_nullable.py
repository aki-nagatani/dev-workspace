"""otayori-navi: add ocr_full_text, md_s3_key nullable (S3 MD廃止・DB一本化)

on_documents に ocr_full_text (TEXT NULL) を追加し、md_s3_key を NULL 許容に変更する。
既にカラムがある場合はスキップする。

Revision ID: 20260209110000
Revises: 20260209100000
Create Date: 2026-02-09 11:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260209110000"
down_revision = "20260209100000"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False
    return column_name in [c["name"] for c in inspector.get_columns(table_name)]


def upgrade() -> None:
    if not _has_table("on_documents"):
        return

    if not _has_column("on_documents", "ocr_full_text"):
        op.add_column(
            "on_documents",
            sa.Column("ocr_full_text", sa.Text(), nullable=True),
        )

    # md_s3_key を NULL 許容に変更
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    if dialect_name == "postgresql":
        op.alter_column(
            "on_documents",
            "md_s3_key",
            existing_type=sa.String(512),
            nullable=True,
        )
    else:
        # SQLite 等
        op.alter_column(
            "on_documents",
            "md_s3_key",
            existing_type=sa.String(512),
            nullable=True,
        )


def downgrade() -> None:
    if not _has_table("on_documents"):
        return

    if _has_column("on_documents", "ocr_full_text"):
        op.drop_column("on_documents", "ocr_full_text")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "on_documents",
            "md_s3_key",
            existing_type=sa.String(512),
            nullable=False,
        )
    # SQLite は ALTER COLUMN で NOT NULL 復元が困難なためスキップ
