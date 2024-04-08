"""alter_column

Revision ID: 3544ac14551c
Revises: f503750defe4
Create Date: 2024-03-21 19:43:30.223189

"""
import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision = '3544ac14551c'
down_revision = 'f503750defe4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'product_targets', 'title',
        existing_type=sa.String(255), existing_nullable=False, nullable=True
    )


def downgrade():
    op.alter_column(
        'product_targets', 'title',
        existing_type=sa.String(255), existing_nullable=True, nullable=False
    )
