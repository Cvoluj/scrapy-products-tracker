"""create_table_sessions

Revision ID: 59f68e67454f
Revises: bb986a7334be
Create Date: 2024-03-27 12:29:08.545445

"""
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, TIMESTAMP
from alembic import op


# revision identifiers, used by Alembic.
revision = '59f68e67454f'
down_revision = 'bb986a7334be'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sessions',
        sa.Column('id', BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('csv_file', sa.String(255)),
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
    )


def downgrade():
    op.drop_table('sessions')
