"""create_table_product_targets

Revision ID: e34a43d11daf
Revises: dc60db9e1e47
Create Date: 2024-03-20 15:57:50.070676

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMINT, TIMESTAMP, TEXT
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e34a43d11daf'
down_revision = 'dc60db9e1e47'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product_targets',
        sa.Column('id', BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('url', sa.String(255), nullable=False, unique=True),
        sa.Column('external_id', sa.String(255), nullable=False, unique=True),
        sa.Column('category', sa.String(255)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(255)),
        sa.Column('image_url', sa.String(255)),
        sa.Column('image_file', sa.String(255)),
        sa.Column('additional_info', sa.JSON),
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', TIMESTAMP, nullable=False, index=True, unique=False,
                  server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.Column('status', MEDIUMINT(unsigned=True), nullable=False, server_default="0"),
        sa.Column('exception', TEXT(), nullable=True)
    )


def downgrade():
    op.drop_table('product_targets')
