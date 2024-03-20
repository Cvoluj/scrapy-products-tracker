"""product_history_init

Revision ID: fd28d3489400
Revises: e34a43d11daf
Create Date: 2024-03-20 16:01:04.070970

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, DECIMAL, BOOLEAN, MEDIUMINT, INTEGER, TIMESTAMP
from alembic import op


# revision identifiers, used by Alembic.
revision = 'fd28d3489400'
down_revision = 'e34a43d11daf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product_history',
        sa.Column('id', BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('product_external_id', sa.String(255), sa.ForeignKey('product_targets.external_id'), nullable=False),
        sa.Column('regular_price', DECIMAL(precision=20, scale=2)),
        sa.Column('current_price', DECIMAL(precision=20, scale=2)),
        sa.Column('in_stock', BOOLEAN),
        sa.Column('stock', MEDIUMINT(unsigned=True)),
        sa.Column('position', INTEGER(unsigned=True)),
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
    )


def downgrade():
    op.drop_table('product_history')
