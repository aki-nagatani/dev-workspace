"""fishtrack rod tables

Revision ID: a43ff432f78e
Revises: 20250912_game_title_and_game_ids
Create Date: 2025-09-17 07:28:03.699371+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a43ff432f78e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'manufacturer',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False, unique=True),
        sa.Column('name_kana', sa.String(length=128), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('website_url', sa.String(length=255), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
    )

    op.create_table(
        'rod',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('manufacturer_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=128), nullable=False),
        sa.Column('length_ft', sa.Integer(), nullable=False),
        sa.Column('length_in', sa.Integer(), nullable=False),
        sa.Column('power', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('genre', sa.String(length=16), nullable=False),
        sa.Column('weight_g', sa.Integer(), nullable=True),
        sa.Column('lure_weight_min_oz', sa.Numeric(5, 2), nullable=True),
        sa.Column('lure_weight_max_oz', sa.Numeric(5, 2), nullable=True),
        sa.Column('line_min_lb', sa.Numeric(5, 2), nullable=True),
        sa.Column('line_max_lb', sa.Numeric(5, 2), nullable=True),
        sa.Column('pieces', sa.Integer(), nullable=True),
        sa.Column('blank_material', sa.String(length=128), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('custom_note', sa.Text(), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.ForeignKeyConstraint(
            ['manufacturer_id'],
            ['manufacturer.id'],
            name='fk_rod_manufacturer_id',
            ondelete='RESTRICT',
        ),
        sa.CheckConstraint('length_in BETWEEN 0 AND 11', name='ck_rod_length_in_range'),
        sa.CheckConstraint("genre IN ('bait','spinning')", name='ck_rod_genre'),
    )

    op.create_table(
        'rod_inventory',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('rod_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='own'),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_shop', sa.String(length=128), nullable=True),
        sa.Column('purchase_price', sa.Integer(), nullable=True),
        sa.Column('condition', sa.String(length=16), nullable=False, server_default='new'),
        sa.Column('list_price', sa.Integer(), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.ForeignKeyConstraint(
            ['rod_id'],
            ['rod.id'],
            name='fk_rod_inventory_rod_id',
            ondelete='RESTRICT',
        ),
        sa.CheckConstraint("status IN ('own','unowned')", name='ck_rod_inventory_status'),
        sa.CheckConstraint("condition IN ('new','used')", name='ck_rod_inventory_condition'),
    )

    op.create_index(
        'ix_rod_inventory_status_updated_at',
        'rod_inventory',
        ['status', 'updated_at'],
    )


def downgrade():
    op.drop_index('ix_rod_inventory_status_updated_at', table_name='rod_inventory')
    op.drop_table('rod_inventory')
    op.drop_table('rod')
    op.drop_table('manufacturer')
