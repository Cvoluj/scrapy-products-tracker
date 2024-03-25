"""alter_column

Revision ID: bb986a7334be
Revises: df5b98b1a15a
Create Date: 2024-03-25 14:04:12.198571

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BOOLEAN
from alembic import op


# revision identifiers, used by Alembic.
revision = 'bb986a7334be'
down_revision = 'df5b98b1a15a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("product_history", "in_stock",
                    new_column_name="is_in_stock", existing_type=BOOLEAN)


def downgrade():
    op.alter_column("product_history", "is_in_stock",
                    new_column_name="in_stock", existing_type=BOOLEAN)
