"""create_astrology_chart_table

Revision ID: a2b4bbf696cb
Revises: a0f8cd93540f
Create Date: 2021-01-15 21:26:36.114597

"""
from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID


# revision identifiers, used by Alembic.
revision = 'a2b4bbf696cb'
down_revision = 'a0f8cd93540f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'astrology_chart',
        sa.Column('id', GUID, primary_key=True, nullable=False),
        sa.Column('user_id', sa.BigInteger, sa.ForeignKey('user.id'), nullable=False),
        sa.Column('datetime', sa.DateTime, nullable=False),
        sa.Column('timezone', sa.String(9), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False)
    )


def downgrade():
    op.drop_table('astrology_chart')
