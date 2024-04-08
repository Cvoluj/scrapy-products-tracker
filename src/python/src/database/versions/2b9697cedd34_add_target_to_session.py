"""add target to session

Revision ID: 2b9697cedd34
Revises: 54d23711de41
Create Date: 2024-04-01 17:38:33.607745

"""
import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision = '2b9697cedd34'
down_revision = '54d23711de41'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sessions', sa.Column('target', sa.String(255)),)

def downgrade():
    op.drop_column('sessions', 'target')
