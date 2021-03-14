"""merchants and stealing

Revision ID: a510b0fee90e
Revises: 20802cfc2469
Create Date: 2021-03-14 01:00:17.634777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a510b0fee90e'
down_revision = '20802cfc2469'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'merchant',
        sa.Column('id', GUID, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('merchat_amount_reset', sa.DateTime, nullable=False)
    )


def downgrade():
    op.drop_table('merchant')