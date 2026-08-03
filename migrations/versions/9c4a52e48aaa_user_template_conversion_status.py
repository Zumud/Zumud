"""Track how far an uploaded template got through conversion

Converting a user's .tex into a template takes a model several attempts and a real
compile each time, so the row now exists before the template does: `status` says
whether it is still pending, ready to use, or failed, and `error` explains a failure
in language meant for the person who uploaded the file.

Revision ID: 9c4a52e48aaa
Revises: c1d7a3f89b42
Create Date: 2026-08-03 16:41:39.877549

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9c4a52e48aaa"
down_revision: Union[str, None] = "c1d7a3f89b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Every existing row predates uploading and already holds a working template, so
    # it is ready. The server default exists only to fill them in — adding a NOT NULL
    # column to a table that has rows fails without one — and is dropped again
    # immediately so the schema still matches the model, which sets this in Python.
    op.add_column(
        "user_templates",
        sa.Column("status", sa.String(), nullable=False, server_default="ready"),
    )
    op.alter_column("user_templates", "status", server_default=None)
    op.add_column("user_templates", sa.Column("error", sa.Text(), nullable=True))
    # A pending upload has no template yet, and a failed one never will.
    op.alter_column(
        "user_templates", "latex_content", existing_type=sa.TEXT(), nullable=True
    )
    # One conversion at a time per user, enforced where it cannot be raced: the
    # limit is there to bound what conversions cost, and two requests arriving
    # together would both pass a count read back in Python.
    op.create_index(
        "uq_user_templates_one_pending_per_user",
        "user_templates",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index("uq_user_templates_one_pending_per_user", table_name="user_templates")
    # Rows that never finished converting carry no template at all, so there is
    # nothing to make NOT NULL — and nothing lost by dropping them, since without
    # `status` they would be indistinguishable from working ones.
    op.execute("DELETE FROM user_templates WHERE latex_content IS NULL")
    op.alter_column(
        "user_templates", "latex_content", existing_type=sa.TEXT(), nullable=False
    )
    op.drop_column("user_templates", "error")
    op.drop_column("user_templates", "status")
