"""alter_column

Revision ID: 87b26d4e3fd4
Revises: fd28d3489400
Create Date: 2024-03-21 12:42:13.089333

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '87b26d4e3fd4'
down_revision = 'fd28d3489400'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('category_targets', 'url', existing_type=sa.String(255), type_=sa.String(768))

    op.alter_column('product_targets', 'url', existing_type=sa.String(255), type_=sa.String(768))
    op.alter_column('product_targets', 'external_id', existing_type=sa.String(255), type_=sa.String(768))

    op.alter_column('product_history', 'product_external_id', existing_type=sa.String(255), type_=sa.String(768))


def downgrade():
    op.alter_column('category_targets', 'url', existing_type=sa.String(768), type_=sa.String(255))

    op.alter_column('product_targets', 'url', existing_type=sa.String(768), type_=sa.String(255))
    op.alter_column('product_targets', 'external_id', existing_type=sa.String(768), type_=sa.String(255))

    op.alter_column('product_history', 'product_external_id', existing_type=sa.String(768), type_=sa.String(255))
