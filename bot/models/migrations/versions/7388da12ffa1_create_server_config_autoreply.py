"""create_server_config_autoreply

Revision ID: 7388da12ffa1
Revises: 20802cfc2469
Create Date: 2021-03-15 20:00:16.055199

"""
from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID


# revision identifiers, used by Alembic.
revision = '7388da12ffa1'
down_revision = '20802cfc2469'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'server_config_autoreply',
        sa.Column('id', GUID, primary_key=True),
        sa.Column('server_config_id', sa.BigInteger, sa.ForeignKey('server_config.id'), nullable=False),
        sa.Column('message_regex', sa.String, nullable=False),
        sa.Column('reply', sa.String, nullable=True),
        sa.Column('reaction', sa.String, nullable=True),
        sa.Column('image_url', sa.String, nullable=True)
    )


def downgrade():
    op.drop_table('server_config_autoreply')

