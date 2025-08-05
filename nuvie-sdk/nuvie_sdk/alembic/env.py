"""Alembic environment script."""

import alembic_postgresql_enum

import os
import dotenv

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import constants as c
from models import SQLModel  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Configuring alembic_postgresql_enum
alembic_postgresql_enum.set_configuration(
    alembic_postgresql_enum.Config(
        add_type_ignore=True,
        drop_unused_enums=True,
        detect_enum_values_changes=True,
        ignore_enum_values_order=False,
    )
)


# Printing some info on the DB we're connecting to
ENV_FILE = os.getenv("ENV_FILE", ".env")
loaded_env_vars = dotenv.load_dotenv(ENV_FILE)

print(f'Alembic | Loaded env vars from "{ENV_FILE}"? {loaded_env_vars}')
print(f"Alembic | POSTGRES_SERVER={c.POSTGRES_SERVER}")
print(f"Alembic | POSTGRES_PORT={c.POSTGRES_PORT}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """

    url = c.get_postgres_uri()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Get the database URL from our constants
    url = c.get_postgres_uri()

    # Create configuration for the engine
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
