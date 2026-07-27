"""migrate user preferences into user ai rules

Revision ID: b4c72e91d5af
Revises: 9f0b8d1c2a3e
Create Date: 2026-07-27 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4c72e91d5af"
down_revision: Union[str, None] = "9f0b8d1c2a3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Legacy preferences were one AI-formatted bullet list per user, so every
# non-empty line is already a standalone instruction: strip the bullet marker
# and the line becomes one AI rule.
BULLET_PREFIX = r"^\s*(•|‣|▪|●|\*|–|—|-|\d+[.)])\s*"

IMPORTED_TITLE = "Imported preference"

# Matches ck_user_ai_rules_instruction_max_length.
MAX_INSTRUCTION_LENGTH = 500


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO public.user_ai_rules
                (user_id, title, instruction, is_enabled, created_at, updated_at)
            SELECT
                up.user_id,
                :title,
                line.instruction,
                true,
                COALESCE(up.created_at AT TIME ZONE 'UTC', now()),
                COALESCE(up.updated_at AT TIME ZONE 'UTC', now())
            FROM public.user_preferences up
            CROSS JOIN LATERAL (
                SELECT
                    ordinality,
                    left(
                        btrim(regexp_replace(raw_line, :bullet_prefix, '')),
                        :max_length
                    ) AS instruction
                FROM unnest(
                    string_to_array(up.preferences_text, E'\\n')
                ) WITH ORDINALITY AS source(raw_line, ordinality)
            ) AS line
            WHERE up.user_id IS NOT NULL
              AND line.instruction <> ''
              AND NOT EXISTS (
                  -- Only an *enabled* rule counts as already covering this
                  -- instruction. Legacy preferences were always applied, so
                  -- matching a disabled rule and skipping the insert would
                  -- silently stop applying the instruction.
                  SELECT 1
                  FROM public.user_ai_rules existing
                  WHERE existing.user_id = up.user_id
                    AND existing.is_enabled
                    AND btrim(existing.instruction) = line.instruction
              )
            ORDER BY up.user_id, line.ordinality
            """
        ).bindparams(
            title=IMPORTED_TITLE,
            bullet_prefix=BULLET_PREFIX,
            max_length=MAX_INSTRUCTION_LENGTH,
        )
    )

    op.drop_index(op.f("ix_user_preferences_id"), table_name="user_preferences")
    op.drop_table("user_preferences")


def downgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("preferences_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_user_preferences_id"), "user_preferences", ["id"], unique=False
    )

    # Fold the rules back into one bullet list per user, so downgrading keeps
    # the content upgrade() moved (the preceding revision's downgrade drops the
    # AI-rules table).
    op.execute(
        sa.text(
            """
            INSERT INTO public.user_preferences
                (user_id, preferences_text, created_at, updated_at)
            SELECT
                r.user_id,
                string_agg('- ' || r.instruction, E'\\n' ORDER BY r.id),
                min(r.created_at),
                max(r.updated_at)
            FROM public.user_ai_rules r
            GROUP BY r.user_id
            """
        )
    )
