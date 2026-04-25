"""
Alembic Environment Configuration. 

This file configures how Alembic connects to the database
and runs migrations. It is automatically called by Alembic
when you run any migration command.

Key responsibilities:
    - Connects Alembic to the same database as FastAPI
    - Imports all models so Alembic can detect schema changes
    - Supports both offline and online migration modes

Usage:
    Generate new migration:
        alembic revision --autogenerate -m "describe change"

    Apply migrations:
        alembic upgrade head

    Rollback one migration:
        alembic downgrade -1

    View migration history:
        alembic history

Note:
    Alembic runs synchronously so we replace asyncpg with
    psycopg2 in the database URL. Make sure psycopg2-binary
    is installed:
        pip install psycopg2-binary
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# ─────────────────────────────────────────────
# Path Setup
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# ─────────────────────────────────────────────
# Alembic Config — must come before app imports
# ─────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ─────────────────────────────────────────────
# App Imports — must come after config
# ─────────────────────────────────────────────
from app.config import settings
from app.db.session import Base

# Import ALL models so Base.metadata knows about them
from app.models.user import User           # noqa: F401
from app.models.meal import Meal           # noqa: F401
from app.models.meal import ChatMessage    # noqa: F401

# ─────────────────────────────────────────────
# Override DB URL — must come after config
# ─────────────────────────────────────────────
sync_url = settings.DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2"
)
config.set_main_option("sqlalchemy.url", sync_url)

# ─────────────────────────────────────────────
# Target Metadata — must come after model imports
# ─────────────────────────────────────────────
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Offline mode generates SQL statements without needing
    an actual database connection. Useful for reviewing
    what SQL will be executed before running it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    Online mode connects directly to the database and
    applies migrations immediately. This is the default
    mode used when running:
        alembic upgrade head
        alembic downgrade -1
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()