"""create planet table

Revision ID: b574977c1728
Revises: 6c157a54a570
Create Date: 2021-02-17 22:18:29.501892

"""
from alembic import op
import sqlalchemy as sa


from bot.models.guid import GUID
from uuid import uuid4
# revision identifiers, used by Alembic.
revision = 'b574977c1728'
down_revision = '6c157a54a570'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'planet',
        sa.Column('id', GUID(), primary_key=True, default=uuid4),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('happines_base', sa.Integer, nullable=False),
        sa.Column('importance_base', sa.Integer, nullable=False),
        sa.Column('price', sa.Integer, nullable=False),
        sa.Column('region', sa.String, nullable=False),
        sa.Column('climate', sa.String, nullable=False),
        sa.Column('circuference', sa.Integer, nullable=False),
        sa.Column('mass', sa.Integer, nullable=False),
    )

def downgrade():
    op.drop_table('planet')
