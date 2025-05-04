"""Add current schema with resume_file_path

Revision ID: e2069c42aa8e
Revises: 
Create Date: 2025-05-04 18:50:05.536062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2069c42aa8e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # We've already made this change manually
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # We've already made this change manually
    pass
