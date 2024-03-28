"""drop_column

Revision ID: 0e2adccd0ede
Revises: 201a2a7b6c9e
Create Date: 2024-03-28 18:15:14.234070

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from alembic import op



# revision identifiers, used by Alembic.
revision = '0e2adccd0ede'
down_revision = '201a2a7b6c9e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('product_targets', 'session')
    op.drop_column('category_targets', 'session')
    op.drop_column('product_targets', 'category')


def downgrade():
    op.add_column('product_targets',
                  sa.Column('session', BIGINT(unsigned=True)))
    op.add_column('category_targets',
                  sa.Column('session', BIGINT(unsigned=True)))
    op.add_column('product_targets',
                  sa.Column('category', sa.String(255)))

