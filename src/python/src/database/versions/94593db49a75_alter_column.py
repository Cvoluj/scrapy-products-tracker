"""alter_column

Revision ID: 94593db49a75
Revises: f4f848679492
Create Date: 2024-04-08 20:01:58.334561

"""
import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision = '94593db49a75'
down_revision = 'f4f848679492'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'product_targets', 'image_url',
        existing_type=sa.String(255), type_=sa.String(768)
    )


def downgrade():
    op.alter_column(
        'product_targets', 'image_url',
        existing_type=sa.String(768), type_=sa.String(255)
    )
