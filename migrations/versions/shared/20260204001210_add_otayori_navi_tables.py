"""add otayori-navi tables

Revision ID: 20260204001210
Revises: 20260120001103
Create Date: 2026-02-04 00:12:10
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260204001210"
down_revision = "20260120001103"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(index.get("name") == index_name for index in indexes)


def upgrade() -> None:
    if not _has_table("families"):
        op.create_table(
            "families",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )

    if not _has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("family_id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
            sa.UniqueConstraint("username", name="uq_users_username"),
        )
    if _has_table("users") and not _has_index("users", "ix_users_family_id"):
        op.create_index("ix_users_family_id", "users", ["family_id"])

    if not _has_table("family_invites"):
        op.create_table(
            "family_invites",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("family_id", sa.Integer(), nullable=False),
            sa.Column("created_by_user_id", sa.Integer(), nullable=False),
            sa.Column("used_by_user_id", sa.Integer(), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
            sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["used_by_user_id"], ["users.id"]),
            sa.UniqueConstraint("code", name="uq_family_invites_code"),
        )
    if _has_table("family_invites") and not _has_index(
        "family_invites", "ix_family_invites_family_id"
    ):
        op.create_index("ix_family_invites_family_id", "family_invites", ["family_id"])

    if not _has_table("documents"):
        op.create_table(
            "documents",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("family_id", sa.Integer(), nullable=False),
            sa.Column("doc_id", sa.String(length=32), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("issue_date", sa.String(length=32), nullable=True),
            sa.Column("category", sa.String(length=128), nullable=True),
            sa.Column("child", sa.JSON(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("need_action", sa.Boolean(), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("actions", sa.JSON(), nullable=False),
            sa.Column("due_dates", sa.JSON(), nullable=False),
            sa.Column("items", sa.JSON(), nullable=False),
            sa.Column("cost", sa.String(length=128), nullable=False),
            sa.Column("contacts", sa.JSON(), nullable=False),
            sa.Column("excerpts", sa.JSON(), nullable=False),
            sa.Column("source_filename", sa.String(length=255), nullable=False),
            sa.Column("source_hash", sa.String(length=64), nullable=False),
            sa.Column("source_mime_type", sa.String(length=128), nullable=False),
            sa.Column("pdf_s3_key", sa.String(length=512), nullable=False),
            sa.Column("md_s3_key", sa.String(length=512), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["family_id"], ["families.id"]),
            sa.UniqueConstraint("doc_id", name="uq_documents_doc_id"),
        )
    if _has_table("documents") and not _has_index("documents", "ix_documents_family_id"):
        op.create_index("ix_documents_family_id", "documents", ["family_id"])


def downgrade() -> None:
    if _has_table("documents") and _has_index("documents", "ix_documents_family_id"):
        op.drop_index("ix_documents_family_id", table_name="documents")
    if _has_table("documents"):
        op.drop_table("documents")

    if _has_table("family_invites") and _has_index(
        "family_invites", "ix_family_invites_family_id"
    ):
        op.drop_index("ix_family_invites_family_id", table_name="family_invites")
    if _has_table("family_invites"):
        op.drop_table("family_invites")

    if _has_table("users") and _has_index("users", "ix_users_family_id"):
        op.drop_index("ix_users_family_id", table_name="users")
    if _has_table("users"):
        op.drop_table("users")

    if _has_table("families"):
        op.drop_table("families")
