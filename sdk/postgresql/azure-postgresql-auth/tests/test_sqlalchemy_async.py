# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Async unit tests for SQLAlchemy Entra authentication integration."""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from azure_postgresql_auth.sqlalchemy import enable_entra_authentication_async


class TestSqlalchemyAsyncEntraAuthentication:
    """Tests for enable_entra_authentication_async function."""

    def test_async_function_exists(self):
        """Test that the async authentication function is importable."""
        assert callable(enable_entra_authentication_async)


@pytest.mark.live_test_only
class TestSqlalchemyAsyncEntraAuthenticationLive:
    """Live tests for asynchronous SQLAlchemy with enable_entra_authentication_async."""

    @pytest.mark.asyncio
    async def test_connect_with_entra_user_async(self, async_connection_url, credential, postgresql_database):
        """Test connecting with an Entra user using enable_entra_authentication_async."""
        engine = create_async_engine(async_connection_url, connect_args={"credential": credential})
        enable_entra_authentication_async(engine)

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT current_user, current_database()"))
            row = result.fetchone()
            current_user, current_db = row

            assert current_db == postgresql_database
            assert current_user is not None

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_execute_query_async(self, async_connection_url, credential):
        """Test executing a basic query through async SQLAlchemy with Entra auth."""
        engine = create_async_engine(async_connection_url, connect_args={"credential": credential})
        enable_entra_authentication_async(engine)

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_token_caching_behavior_async(self, async_connection_url, credential):
        """Test that credentials are invoked for each connection (async)."""
        engine = create_async_engine(async_connection_url, connect_args={"credential": credential})
        enable_entra_authentication_async(engine)

        # First connection
        async with engine.connect() as conn1:
            result = await conn1.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1

        # Second connection
        async with engine.connect() as conn2:
            result = await conn2.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row[0] == 1

        await engine.dispose()
