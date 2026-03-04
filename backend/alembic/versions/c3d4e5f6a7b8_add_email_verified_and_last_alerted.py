"""add email_verified to users and last_alerted_price to products

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-04 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users: email_verified boolean column (default False)
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # Products: last_alerted_price to track smart alerts
    op.add_column(
        "products",
        sa.Column("last_alerted_price", sa.Numeric(precision=10, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("products", "last_alerted_price")
    op.drop_column("users", "email_verified")
