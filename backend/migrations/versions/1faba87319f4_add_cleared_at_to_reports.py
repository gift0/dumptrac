"""Add cleared_at to reports

Revision ID: 1faba87319f4
Revises: 
Create Date: 2025-09-29 23:39:36.631006
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1faba87319f4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add cleared_at column to reports table
    op.add_column('reports', sa.Column('cleared_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove cleared_at column
    op.drop_column('reports', 'cleared_at')
