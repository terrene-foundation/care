# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Alembic environment configuration for PACT migrations.

Reads the database URL from the DATABASE_URL environment variable
(consistent with pact.config.env). Supports both offline
(SQL script generation) and online (direct database connection) modes.
"""

from __future__ import annotations

import os
import logging
from alembic import context
from sqlalchemy import create_engine, pool

# Alembic Config object — provides access to alembic.ini values
config = context.config

logger = logging.getLogger("alembic.env")


def _get_database_url() -> str:
    """Get database URL from DATABASE_URL environment variable.

    Raises:
        RuntimeError: If DATABASE_URL is not set.
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Alembic requires a database URL to run migrations. "
            "Example: DATABASE_URL=postgresql://user:pass@localhost:5432/care"
        )
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    This is useful for generating migration SQL that can be
    reviewed and applied manually.
    """
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations directly.
    Uses a non-pooled connection to avoid issues with migration
    transactions.
    """
    url = _get_database_url()
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
