"""create_user_table

Revision ID: c22903c48314
Revises: 
Create Date: 2021-01-08 00:18:28.672350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c22903c48314'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.BigInteger, primary_key=True, nullable=False),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('xp_points', sa.Integer, default=0),
    )


def downgrade():
    op.drop_table('user')
