"""create_foreign_key

Revision ID: 54d23711de41
Revises: 9de3733062d8
Create Date: 2024-03-29 13:36:22.435889

"""
import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision = '54d23711de41'
down_revision = '9de3733062d8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        'product_history_ibfk_1', 'product_history', 'product_targets', ['product_id'], ['id'])


def downgrade():
    op.drop_constraint('product_history_ibfk_1', 'product_history', type_='foreignkey')
