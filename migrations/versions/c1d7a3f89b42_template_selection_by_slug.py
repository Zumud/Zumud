"""select resume templates by slug instead of a postgres enum

Revision ID: c1d7a3f89b42
Revises: b4c72e91d5af
Create Date: 2026-08-03 10:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d7a3f89b42"
down_revision: Union[str, None] = "b4c72e91d5af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_TEMPLATE = "builtin:mteck"

# What TailoringOptionsBase() yields today. Users with no tailoring_options row are
# served that default, so rows created here must use it rather than the column
# default (gpt_4_1_nano) or those users would silently drop to a weaker model.
CURRENT_EFFECTIVE_MODEL = "gpt_4_1_mini"


def upgrade() -> None:
    # Production's tailoring_options was converted to varchar by hand before this
    # repo had migrations, and both columns were given CHECK constraints listing
    # model and template *values* — while the app persists enum *names*. No model
    # declares either constraint, and both contradict this migration: one enumerates
    # three retired display names for the column that is becoming a free-form slug,
    # the other rejects every model name the code writes, which is why that table is
    # still empty. A database built from the baseline never had them, hence IF EXISTS.
    op.execute(
        sa.text(
            "ALTER TABLE public.tailoring_options "
            "DROP CONSTRAINT IF EXISTS tailoring_options_resume_template_check"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE public.tailoring_options "
            "DROP CONSTRAINT IF EXISTS tailoring_options_ai_model_check"
        )
    )

    # Selection becomes a plain string so that adding a built-in template is a file
    # drop rather than an ALTER TYPE. Every pre-existing value collapses to the
    # default: of the three enum members only MTeck_resume was a real template, the
    # other two being static sample documents that rendered a resume for "John Doe"
    # regardless of the user's data.
    op.execute(
        sa.text(
            """
            ALTER TABLE public.tailoring_options
                ALTER COLUMN resume_template TYPE varchar
                USING :default
            """
        ).bindparams(default=DEFAULT_TEMPLATE)
    )
    op.execute(sa.text("DROP TYPE IF EXISTS resumetemplate"))

    # Selection used to be split across two places: this column and
    # user_templates.is_active. Collapsing it into the column alone would silently
    # revert everyone whose template came from the is_active flag, because none of
    # them has a tailoring_options row. Give each of them one that names the
    # template they are already getting.
    op.execute(
        sa.text(
            """
            INSERT INTO public.tailoring_options (user_id, ai_model, resume_template)
            SELECT DISTINCT ON (ut.user_id)
                ut.user_id,
                CAST(:model AS aimodel),
                'user:' || ut.id
            FROM public.user_templates ut
            WHERE ut.is_active
              AND ut.user_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM public.tailoring_options t
                  WHERE t.user_id = ut.user_id
              )
            ORDER BY ut.user_id, ut.id
            """
        ).bindparams(model=CURRENT_EFFECTIVE_MODEL)
    )

    # Keeps the uploaded .tex so a template can be regenerated later — e.g. with an
    # improved templatizer prompt — without asking the user for the file again.
    op.add_column("user_templates", sa.Column("source_tex", sa.Text(), nullable=True))


def downgrade() -> None:
    # The two legacy CHECK constraints dropped above are not recreated: they were
    # hand-made artifacts that no model declares and that reject what the code
    # writes, so putting them back would leave a database the app cannot write to.
    op.drop_column("user_templates", "source_tex")

    # Drop only the rows upgrade() created; a row naming a user template cannot be
    # expressed by the enum, and it did not exist before this migration.
    op.execute(
        sa.text(
            """
            DELETE FROM public.tailoring_options
            WHERE resume_template LIKE 'user:%'
            """
        )
    )

    resumetemplate = sa.Enum(
        "Blue_Modern_Resume",
        "One_page_Simple_Resume",
        "MTeck_resume",
        name="resumetemplate",
    )
    resumetemplate.create(op.get_bind(), checkfirst=True)
    op.execute(
        sa.text(
            """
            ALTER TABLE public.tailoring_options
                ALTER COLUMN resume_template TYPE resumetemplate
                USING 'MTeck_resume'::resumetemplate
            """
        )
    )
