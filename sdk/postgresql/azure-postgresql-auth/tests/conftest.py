# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Fixtures for azure-postgresql-auth live tests."""

from __future__ import annotations

import asyncio
import os
import sys

import pytest

from devtools_testutils import get_credential


def _get_pg_config():
    """Read PostgreSQL connection config from environment variables."""
    host = os.environ.get("POSTGRESQL_HOST")
    if not host:
        pytest.skip("POSTGRESQL_HOST environment variable not set")
    database = os.environ.get("POSTGRESQL_DATABASE", "testdb")
    port = os.environ.get("POSTGRESQL_PORT", "5432")
    return host, database, port


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use SelectorEventLoop on Windows for psycopg async compatibility."""
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session")
def postgresql_database():
    """Get the PostgreSQL database from environment variables."""
    return os.environ.get("POSTGRESQL_DATABASE", "testdb")


@pytest.fixture(scope="session")
def credential():
    """Get a credential for live tests."""
    return get_credential()


@pytest.fixture(scope="session")
def async_credential():
    """Get an async credential for live tests."""
    return get_credential(is_async=True)


@pytest.fixture(scope="session")
def connection_dsn():
    """Get a psycopg2-style DSN connection string."""
    host, database, port = _get_pg_config()
    return f"host={host} port={port} dbname={database} sslmode=require"


@pytest.fixture(scope="session")
def connection_params():
    """Get psycopg3-style connection parameters as a dict."""
    host, database, port = _get_pg_config()
    return {
        "host": host,
        "port": port,
        "dbname": database,
        "sslmode": "require",
    }


@pytest.fixture(scope="session")
def connection_url():
    """Get a SQLAlchemy sync connection URL (psycopg2 driver)."""
    host, database, port = _get_pg_config()
    return f"postgresql+psycopg2://{host}:{port}/{database}?sslmode=require"


@pytest.fixture(scope="session")
def async_connection_url():
    """Get a SQLAlchemy async connection URL (psycopg driver)."""
    host, database, port = _get_pg_config()
    return f"postgresql+psycopg://{host}:{port}/{database}?sslmode=require"
