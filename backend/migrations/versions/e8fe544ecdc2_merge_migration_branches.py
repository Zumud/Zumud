"""merge_migration_branches

Revision ID: e8fe544ecdc2
Revises: 5a2b9f6a2b7c, e2069c42aa8e
Create Date: 2025-05-24 12:10:24.916613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8fe544ecdc2'
down_revision: Union[str, None] = ('5a2b9f6a2b7c', 'e2069c42aa8e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
