"""add_column

Revision ID: df5b98b1a15a
Revises: 3544ac14551c
Create Date: 2024-03-25 13:34:11.779001

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BOOLEAN
from alembic import op


# revision identifiers, used by Alembic.
revision = 'df5b98b1a15a'
down_revision = '3544ac14551c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("category_targets", sa.Column(
        "is_tracked", BOOLEAN, nullable=False, server_default=sa.text('True')
    ))
    op.add_column("product_targets", sa.Column(
        "is_tracked", BOOLEAN, nullable=False, server_default=sa.text('True')
    ))


def downgrade():
    op.drop_column("category_targets", "is_tracked")
    op.drop_column("product_targets", "is_tracked")
