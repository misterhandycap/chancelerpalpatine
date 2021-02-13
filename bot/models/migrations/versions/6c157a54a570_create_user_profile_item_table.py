"""create_user_profile_item_table

Revision ID: 6c157a54a570
Revises: 43efe9eeddb5
Create Date: 2021-02-12 23:52:55.375868

"""
from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID


# revision identifiers, used by Alembic.
revision = '6c157a54a570'
down_revision = '43efe9eeddb5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_profile_item',
        sa.Column('user_id', sa.BigInteger, sa.ForeignKey('user.id'), primary_key=True, nullable=False),
        sa.Column('profile_item_id', GUID, sa.ForeignKey('profile_item.id'), primary_key=True, nullable=False)
    )


def downgrade():
    op.drop_table('user_profile_item')
