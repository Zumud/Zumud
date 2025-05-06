"""Allow empty resume content

Revision ID: 5a2b9f6a2b7c
Revises: 
Create Date: 2023-12-05 14:22:33.789000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a2b9f6a2b7c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make resume_content column nullable
    op.alter_column('resumes', 'resume_content',
               existing_type=sa.TEXT(),
               nullable=True)


def downgrade() -> None:
    # Revert back to non-nullable
    # This might fail if there are null values in the column
    op.alter_column('resumes', 'resume_content',
               existing_type=sa.TEXT(),
               nullable=False) 