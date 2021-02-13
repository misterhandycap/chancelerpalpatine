"""create_profile_item_table

Revision ID: 43efe9eeddb5
Revises: e2101b941963
Create Date: 2021-02-12 23:36:23.167329

"""
from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID


# revision identifiers, used by Alembic.
revision = '43efe9eeddb5'
down_revision = 'e2101b941963'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profile_item',
        sa.Column('id', GUID, primary_key=True),
        sa.Column('type', sa.Enum('badge', 'wallpaper', name='profile_item_type'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('price', sa.Integer, nullable=False),
        sa.Column('file_path', sa.String, nullable=False)
    )


def downgrade():
    op.drop_table('profile_item')
