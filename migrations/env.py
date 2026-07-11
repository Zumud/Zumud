import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Require an explicit target. backend.config.envs falls back to .env via
# python-dotenv, which for migrations is a footgun (a casual `alembic upgrade`
# must never silently hit whatever database .env points at). Setting the var
# first also means the dotenv load below cannot override it.
if not os.environ.get("DATABASE_URL"):
    raise SystemExit(
        "DATABASE_URL must be set explicitly for migrations "
        "(e.g. the local stack's DB_URL, or the prod URL on the deploy host)."
    )

from backend.models import db_models  # noqa: E402,F401  registers all tables
from backend.models.db import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
