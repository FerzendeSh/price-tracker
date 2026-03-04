"""add target_price to products

Revision ID: a1b2c3d4e5f6
Revises: 0d3934cff25e
Create Date: 2026-03-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "0d3934cff25e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("target_price", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "target_price")
