"""drop_constraint

Revision ID: 5c2f399a6bc0
Revises: 0e2adccd0ede
Create Date: 2024-03-29 13:21:30.489410

"""
import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision = '5c2f399a6bc0'
down_revision = '0e2adccd0ede'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('product_history_ibfk_1', 'product_history', type_='foreignkey')


def downgrade():
    op.create_foreign_key(
        'product_history_ibfk_1', 'product_history', 'product_targets', ['product_external_id'], ['external_id'])
