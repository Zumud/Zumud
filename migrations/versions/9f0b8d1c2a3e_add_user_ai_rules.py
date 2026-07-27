"""add user ai rules

Revision ID: 9f0b8d1c2a3e
Revises: 23ef185de22c
Create Date: 2026-07-26 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9f0b8d1c2a3e"
down_revision: Union[str, None] = "23ef185de22c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_policy_if_supabase_auth_exists(policy_sql: str) -> None:
    escaped_policy_sql = policy_sql.replace("'", "''")
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'auth'
                  AND p.proname = 'uid'
                  AND pg_get_function_identity_arguments(p.oid) = ''
            ) THEN
                EXECUTE '{escaped_policy_sql}';
            END IF;
        END
        $$;
        """
    )


def upgrade() -> None:
    op.create_table(
        "user_ai_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=True),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column(
            "is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "length(trim(instruction)) > 0",
            name="ck_user_ai_rules_instruction_not_empty",
        ),
        sa.CheckConstraint(
            "length(instruction) <= 500",
            name="ck_user_ai_rules_instruction_max_length",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_ai_rules_id"), "user_ai_rules", ["id"], unique=False)
    op.create_index(
        "ix_user_ai_rules_user_id_updated_at",
        "user_ai_rules",
        ["user_id", "updated_at"],
        unique=False,
    )
    op.create_index(
        "ix_user_ai_rules_enabled",
        "user_ai_rules",
        ["user_id", "is_enabled"],
        unique=False,
    )

    op.execute("ALTER TABLE public.user_ai_rules ENABLE ROW LEVEL SECURITY")
    _create_policy_if_supabase_auth_exists(
        """
        CREATE POLICY user_ai_rules_select_own
        ON public.user_ai_rules
        FOR SELECT
        USING (
            EXISTS (
                SELECT 1
                FROM public.users
                WHERE users.id = user_ai_rules.user_id
                  AND users.supabase_uid = auth.uid()
            )
        )
        """
    )
    _create_policy_if_supabase_auth_exists(
        """
        CREATE POLICY user_ai_rules_insert_own
        ON public.user_ai_rules
        FOR INSERT
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM public.users
                WHERE users.id = user_ai_rules.user_id
                  AND users.supabase_uid = auth.uid()
            )
        )
        """
    )
    _create_policy_if_supabase_auth_exists(
        """
        CREATE POLICY user_ai_rules_update_own
        ON public.user_ai_rules
        FOR UPDATE
        USING (
            EXISTS (
                SELECT 1
                FROM public.users
                WHERE users.id = user_ai_rules.user_id
                  AND users.supabase_uid = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM public.users
                WHERE users.id = user_ai_rules.user_id
                  AND users.supabase_uid = auth.uid()
            )
        )
        """
    )
    _create_policy_if_supabase_auth_exists(
        """
        CREATE POLICY user_ai_rules_delete_own
        ON public.user_ai_rules
        FOR DELETE
        USING (
            EXISTS (
                SELECT 1
                FROM public.users
                WHERE users.id = user_ai_rules.user_id
                  AND users.supabase_uid = auth.uid()
            )
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS user_ai_rules_delete_own ON public.user_ai_rules")
    op.execute("DROP POLICY IF EXISTS user_ai_rules_update_own ON public.user_ai_rules")
    op.execute("DROP POLICY IF EXISTS user_ai_rules_insert_own ON public.user_ai_rules")
    op.execute("DROP POLICY IF EXISTS user_ai_rules_select_own ON public.user_ai_rules")
    op.drop_index("ix_user_ai_rules_enabled", table_name="user_ai_rules")
    op.drop_index("ix_user_ai_rules_user_id_updated_at", table_name="user_ai_rules")
    op.drop_index(op.f("ix_user_ai_rules_id"), table_name="user_ai_rules")
    op.drop_table("user_ai_rules")
