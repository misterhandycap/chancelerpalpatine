"""create_server_config_table

Revision ID: 8d13a31bb318
Revises: b574977c1728
Create Date: 2021-02-27 21:00:34.929353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d13a31bb318'
down_revision = 'b574977c1728'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'server_config',
        sa.Column('id', sa.BigInteger, primary_key=True, nullable=False),
        sa.Column('language', sa.String, default='en')
    )


def downgrade():
    op.drop_table('server_config')
