"""create_chess_game_table

Revision ID: 3b5080b68ec1
Revises: c22903c48314
Create Date: 2021-01-08 00:19:37.577169

"""
from alembic import op
import sqlalchemy as sa

from bot.models.guid import GUID


# revision identifiers, used by Alembic.
revision = '3b5080b68ec1'
down_revision = 'c22903c48314'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'chess_game',
        sa.Column('id', GUID, primary_key=True, nullable=False),
        sa.Column('player1_id', sa.BigInteger, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('player2_id', sa.BigInteger, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('pgn', sa.String),
        sa.Column('result', sa.SmallInteger, nullable=True),
        sa.Column('color_schema', sa.String, nullable=True),
        sa.Column('cpu_level', sa.SmallInteger, nullable=True),
    )


def downgrade():
    op.drop_table('chess_game')
