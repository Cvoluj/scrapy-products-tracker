"""drop_constraint

Revision ID: 201a2a7b6c9e
Revises: 421155601c10
Create Date: 2024-03-28 17:20:38.449382

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from alembic import op


# revision identifiers, used by Alembic.
revision = '201a2a7b6c9e'
down_revision = '421155601c10'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('product_targets_ibfk_1', 'product_targets', type_='foreignkey')
    op.drop_constraint('category_targets_ibfk_1', 'category_targets', type_='foreignkey')


def downgrade():

    op.create_foreign_key(
        'product_targets_ibfk_1', 'product_targets', 'sessions', ['session'], ['id'])
    op.create_foreign_key(
        'category_targets_ibfk_1', 'category_targets', 'sessions', ['session'], ['id'])
