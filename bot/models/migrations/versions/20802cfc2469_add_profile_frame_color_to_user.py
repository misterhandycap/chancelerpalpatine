"""add_profile_frame_color_to_user

Revision ID: 20802cfc2469
Revises: 52353283014a
Create Date: 2021-03-13 10:06:42.143471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20802cfc2469'
down_revision = '52353283014a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user',
        sa.Column('profile_frame_color', sa.String(length=7), nullable=True)
    )


def downgrade():
    op.drop_column('user', 'profile_frame_color')
