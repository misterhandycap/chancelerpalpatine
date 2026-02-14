"""create_icp_metric_table

Revision ID: cd357e720fae
Revises: 7388da12ffa1
Create Date: 2026-02-13 14:49:22.281175

"""

from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID

# revision identifiers, used by Alembic.
revision = 'cd357e720fae'
down_revision = '7388da12ffa1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'icp_metric',
        sa.Column('id', GUID, primary_key=True, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('data', sa.JSON, nullable=False),
    )


def downgrade():
    op.drop_table('icp_metric')
