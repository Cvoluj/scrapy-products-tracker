"""create_table_category_targets

Revision ID: dc60db9e1e47
Revises:
Create Date: 2024-03-20 15:56:03.211837

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMINT, TEXT
from alembic import op


# revision identifiers, used by Alembic.
revision = 'dc60db9e1e47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'category_targets',
        sa.Column('id', BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('url', sa.String(255), nullable=False, unique=True),
        sa.Column('status', MEDIUMINT(unsigned=True), nullable=False, server_default='0'),
        sa.Column('exception', TEXT(), nullable=True)
    )


def downgrade():
    op.drop_table('category_targets')
