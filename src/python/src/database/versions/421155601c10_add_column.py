"""add_column

Revision ID: 421155601c10
Revises: 07ea4a17dc5f
Create Date: 2024-03-28 14:37:21.904384

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from alembic import op


# revision identifiers, used by Alembic.
revision = '421155601c10'
down_revision = '07ea4a17dc5f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("product_history",
                  sa.Column('currency', sa.String(255)))
    op.add_column("product_history",
                  sa.Column('units', sa.String(255)))
    op.add_column("product_history",
                  sa.Column("session", BIGINT(unsigned=True), sa.ForeignKey('sessions.id')))


def downgrade():
    op.drop_column("product_history", "currency")
    op.drop_column("product_history", "units")
    op.drop_column("product_history", "session")
