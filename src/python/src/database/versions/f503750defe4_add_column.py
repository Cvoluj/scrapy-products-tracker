"""add_column

Revision ID: f503750defe4
Revises: 87b26d4e3fd4
Create Date: 2024-03-21 13:18:07.123400

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import TIMESTAMP, TEXT
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f503750defe4'
down_revision = '87b26d4e3fd4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'category_targets',
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
    )
    op.add_column(
        'category_targets',
        sa.Column('updated_at', TIMESTAMP, nullable=False, index=True, unique=False,
                  server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    )
    op.add_column('category_targets', sa.Column('domain', sa.String(255), index=True))

    op.add_column('product_targets', sa.Column('domain', sa.String(255), index=True))
    op.add_column('product_targets', sa.Column('description', TEXT))


def downgrade():
    op.drop_column('category_targets', 'created_at')
    op.drop_column('category_targets', 'updated_at')
    op.drop_column('category_targets', 'domain')

    op.drop_column('product_targets', 'domain')
    op.drop_column('product_targets',  'description')
