"""alter user collumn to currency

Revision ID: e2101b941963
Revises: a2b4bbf696cb
Create Date: 2021-01-17 18:47:09.914371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2101b941963'
down_revision = 'a2b4bbf696cb'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'xp_points', nullable=False, new_column_name='currency')
    op.add_column('user', sa.Column('daily_last_collected_at', sa.DateTime, nullable=True))


def downgrade():
    op.alter_column('user', 'currency', nullable=False, new_column_name='xp_points')
    op.drop_column('user', 'daily_last_collected_at')
