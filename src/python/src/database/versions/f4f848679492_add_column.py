"""add_column

Revision ID: f4f848679492
Revises: 2b9697cedd34
Create Date: 2024-04-04 11:52:01.424987

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f4f848679492'
down_revision = '2b9697cedd34'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_targets', sa.Column('category', sa.String(768)))


def downgrade():
    op.drop_column('product_targets', 'category')
