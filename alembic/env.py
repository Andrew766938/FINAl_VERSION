from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path

# Get the absolute path to the app directory
app_dir = str(Path(__file__).parent.parent / "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

try:
    from app.database.base import Base
    from app.config import settings
    print(f"✅ Loaded Base metadata and settings")
except ImportError as e:
    print(f"⚠️  Warning: Could not load app models: {e}")
    Base = None
    settings = None

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model's MetaData object for 'autogenerate' support
if Base is not None:
    target_metadata = Base.metadata
else:
    target_metadata = None

# Set the database URL from settings
if settings is not None:
    db_url = settings.get_db_url
else:
    # Fallback to SQLite
    db_url = "sqlite:///betony.db"

config.set_main_option('sqlalchemy.url', db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = db_url
    
    # For SQLite, use StaticPool to avoid threading issues
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.StaticPool,
        echo=False,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
