"""aler_column_drop_column

Revision ID: 9de3733062d8
Revises: 5c2f399a6bc0
Create Date: 2024-03-29 13:27:58.232672

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT
from alembic import op



# revision identifiers, used by Alembic.
revision = '9de3733062d8'
down_revision = '5c2f399a6bc0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('product_history',
                    'product_external_id',
                    new_column_name='product_id',
                    existing_type=sa.String(768),
                    type_=BIGINT(unsigned=True))

    op.drop_column('product_targets', 'external_id')


def downgrade():
    op.alter_column('product_history',
                    'product_id',
                    new_column_name='product_external_id',
                    existing_type=BIGINT(unsigned=True),
                    type_=sa.String(768))

    op.add_column('product_targets', sa.Column('external_id', sa.String(768)))
