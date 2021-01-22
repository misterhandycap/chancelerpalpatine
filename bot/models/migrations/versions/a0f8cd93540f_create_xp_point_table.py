"""create_xp_point_table

Revision ID: a0f8cd93540f
Revises: 3b5080b68ec1
Create Date: 2021-01-14 21:56:10.308262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0f8cd93540f'
down_revision = '3b5080b68ec1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'xp_point',
        sa.Column('user_id', sa.BigInteger, sa.ForeignKey('user.id'), primary_key=True, nullable=False),
        sa.Column('server_id', sa.BigInteger, primary_key=True, nullable=True),
        sa.Column('points', sa.Integer, nullable=False),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )


def downgrade():
    op.drop_table('xp_point')