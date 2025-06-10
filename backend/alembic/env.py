import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from backend.app.core.base import Base
from backend.app.core.config import settings

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    db_url_str = str(settings.database_url)

    context.configure(
        url=db_url_str,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    current_context = context.get_context()
    alembic_version_table = current_context.version_table
    alembic_version_table_schema = current_context.version_table_schema

    if type_ == "table":
        if (
            name == alembic_version_table
            and object.schema == alembic_version_table_schema
        ):
            return True
        if object.schema != target_metadata.schema:
            return False
        return name in target_metadata.tables
    elif type_ == "index":
        if object.table is None:
            return False
        if (
            object.table.schema == target_metadata.schema
            and object.table.name in target_metadata.tables
        ):
            return True
        return False
    else:
        return True


def do_run_migrations(connection: Connection) -> None:
    """Helper function to run migrations within a transaction for online mode."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    db_config_section = config.get_section(config.config_ini_section, {})

    db_config_section["sqlalchemy.url"] = str(settings.database_url)

    connectable = async_engine_from_config(
        db_config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
