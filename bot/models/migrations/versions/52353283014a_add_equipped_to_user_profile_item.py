"""add_equipped_to_user_profile_item

Revision ID: 52353283014a
Revises: 8d13a31bb318
Create Date: 2021-03-11 20:20:45.763713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52353283014a'
down_revision = '8d13a31bb318'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_profile_item',
        sa.Column('equipped', sa.Boolean, nullable=False, server_default='false')
    )


def downgrade():
    op.drop_column('user_profile_item', 'equipped')
