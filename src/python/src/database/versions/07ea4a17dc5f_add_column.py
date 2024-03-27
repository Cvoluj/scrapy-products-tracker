"""add_column

Revision ID: 07ea4a17dc5f
Revises: 59f68e67454f
Create Date: 2024-03-27 13:00:03.757637

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import INTEGER, BIGINT
from alembic import op


# revision identifiers, used by Alembic.
revision = '07ea4a17dc5f'
down_revision = '59f68e67454f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_targets',
                  sa.Column('position', INTEGER(unsigned=True)))
    op.add_column('product_targets',
                  sa.Column('session', BIGINT(unsigned=True), sa.ForeignKey('sessions.id')))
    op.add_column('category_targets',
                  sa.Column('session', BIGINT(unsigned=True), sa.ForeignKey('sessions.id')))


def downgrade():
    op.drop_column('product_targets', 'position')
    op.drop_column('product_targets', 'session')
    op.drop_column('category_targets', 'session')
