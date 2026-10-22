# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Async unit tests for SQLAlchemy Entra authentication integration."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError
from azure_postgresql_auth.sqlalchemy import create_asyncpg_engine, enable_entra_authentication_async
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from utils import (
    TEST_USERS,
    MockAsyncTokenCredential,
    MockTokenCredential,
    capture_event_handler,
    create_valid_jwt_token,
)

ASYNC_MODULE = "azure_postgresql_auth.sqlalchemy.async_entra_connection"
ASYNCPG_MODULE = "azure_postgresql_auth.sqlalchemy.asyncpg"


class TestSqlalchemyAsyncEntraAuthentication:
    """Tests for enable_entra_authentication_async function."""

    @patch(f"{ASYNC_MODULE}.get_entra_conninfo")
    def test_provides_entra_credentials_async(self, mock_get_conninfo):
        """Test that the event handler provides Entra credentials (async engine)."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }

        handler, mock_listens_for, mock_engine = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)
        # Async variant must register on the underlying sync_engine
        mock_listens_for.assert_called_once_with(mock_engine.sync_engine, "do_connect")

        credential = MockTokenCredential(token)
        cparams = {"credential": credential}
        dialect = MagicMock()
        dbapi_connection = MagicMock()
        dialect.connect.return_value = dbapi_connection
        assert handler(dialect, MagicMock(), [], cparams) is dbapi_connection
        mock_get_conninfo.assert_called_once_with(credential)
        dialect.connect.assert_called_once_with(user=TEST_USERS["ENTRA_USER"], password=token)
        assert cparams == {"credential": credential}

    def test_missing_credential_raises_error_async(self):
        """Test that the event handler raises CredentialValueError when no credential."""
        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)
        with pytest.raises(CredentialValueError):
            handler(MagicMock(), MagicMock(), [], {})

    @pytest.mark.parametrize(
        "credential_value",
        [None, "not-a-credential", 12345],
        ids=["none", "string", "int"],
    )
    def test_invalid_credential_raises_error_async(self, credential_value):
        """Test that non-TokenCredential values raise CredentialValueError."""
        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)
        with pytest.raises(CredentialValueError):
            handler(MagicMock(), MagicMock(), [], {"credential": credential_value})

    @patch(f"{ASYNC_MODULE}.get_entra_conninfo")
    def test_credential_is_preserved_for_subsequent_connections_async(self, mock_get_conninfo):
        """Test that pooled connections can reuse the credential configuration."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)
        cparams = {"credential": credential}

        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)
        dialect = MagicMock()
        handler(dialect, MagicMock(), [], cparams)
        handler(dialect, MagicMock(), [], cparams)

        assert cparams == {"credential": credential}
        assert mock_get_conninfo.call_count == 2
        assert dialect.connect.call_count == 2

    @patch(f"{ASYNC_MODULE}.get_entra_conninfo")
    def test_existing_credentials_preserved_async(self, mock_get_conninfo):
        """Test that existing user/password in cparams are preserved (async)."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)

        cparams = {"credential": credential, "user": "existing", "password": "secret"}
        dialect = MagicMock()
        handler(dialect, MagicMock(), [], cparams)

        mock_get_conninfo.assert_not_called()
        dialect.connect.assert_called_once_with(user="existing", password="secret")
        assert cparams == {"credential": credential, "user": "existing", "password": "secret"}

    @pytest.mark.parametrize(
        "cparams_extra,should_call",
        [
            ({}, True),
            ({"user": "existing"}, True),
            ({"password": "secret"}, True),
            ({"user": "existing", "password": "secret"}, False),
        ],
        ids=["neither", "user-only", "password-only", "both"],
    )
    @patch(f"{ASYNC_MODULE}.get_entra_conninfo")
    def test_partial_credentials_trigger_entra_lookup_async(self, mock_get_conninfo, cparams_extra, should_call):
        """Test that get_entra_conninfo is called when user or password is missing."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)

        cparams = {"credential": credential, **cparams_extra}
        handler(MagicMock(), MagicMock(), [], cparams)

        if should_call:
            mock_get_conninfo.assert_called_once_with(credential)
        else:
            mock_get_conninfo.assert_not_called()

    @patch(f"{ASYNC_MODULE}.get_entra_conninfo")
    def test_entra_credential_failure_raises_error_async(self, mock_get_conninfo):
        """Test that credential retrieval failure raises EntraConnectionValueError (async)."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication_async, ASYNC_MODULE)

        with pytest.raises(EntraConnectionValueError, match="Could not retrieve Entra credentials"):
            handler(MagicMock(), MagicMock(), [], {"credential": credential})


class TestSqlalchemyAsyncpgEntraAuthentication:
    """Tests for asyncpg SQLAlchemy Entra authentication integration."""

    @patch(f"{ASYNCPG_MODULE}.create_async_engine")
    @patch(f"{ASYNCPG_MODULE}.get_entra_conninfo_async", new_callable=AsyncMock)
    @patch("asyncpg.connect", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_creates_asyncpg_connection_with_entra_credentials(
        self, mock_connect, mock_get_conninfo, mock_create_engine
    ):
        """Test that the async creator injects Entra credentials into asyncpg."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockAsyncTokenCredential(token)
        mock_get_conninfo.return_value = {"user": TEST_USERS["ENTRA_USER"], "password": token}

        create_asyncpg_engine(
            "postgresql+asyncpg://server.example:5432/database?sslmode=require",
            credential,
        )

        async_creator = mock_create_engine.call_args.kwargs["async_creator"]
        await async_creator()

        mock_get_conninfo.assert_awaited_once_with(credential)
        mock_connect.assert_awaited_once_with(
            host="server.example",
            port=5432,
            database="database",
            user=TEST_USERS["ENTRA_USER"],
            password=token,
            ssl="require",
        )

    def test_invalid_asyncpg_credential_raises_error(self):
        """Test that a synchronous credential is rejected before creating an engine."""
        with pytest.raises(CredentialValueError, match="AsyncTokenCredential"):
            create_asyncpg_engine("postgresql+asyncpg://server.example/database", MagicMock())

    @patch(f"{ASYNCPG_MODULE}.create_async_engine")
    @patch(f"{ASYNCPG_MODULE}.get_entra_conninfo_async", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_asyncpg_credential_failure_raises_connection_error(self, mock_get_conninfo, mock_create_engine):
        """Test that async credential failures are surfaced as Entra connection errors."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        credential = MockAsyncTokenCredential(create_valid_jwt_token(TEST_USERS["ENTRA_USER"]))

        create_asyncpg_engine("postgresql+asyncpg://server.example/database", credential)

        async_creator = mock_create_engine.call_args.kwargs["async_creator"]
        with pytest.raises(EntraConnectionValueError, match="Could not retrieve Entra credentials"):
            await async_creator()


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
    async def test_multiple_sequential_connections_async(self, async_connection_url, credential):
        """Test that the same credential works across multiple sequential connections."""
        engine = create_async_engine(async_connection_url, connect_args={"credential": credential})
        enable_entra_authentication_async(engine)

        for _ in range(3):
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_concurrent_async_connections(self, async_connection_url, credential):
        """Test that multiple concurrent async connections work with the same credential."""
        engine = create_async_engine(async_connection_url, connect_args={"credential": credential})
        enable_entra_authentication_async(engine)

        async def query():
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.fetchone()[0]

        results = await asyncio.gather(query(), query(), query())
        assert results == [1, 1, 1]

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_connection_pool_reuse_async(self, async_connection_url, credential):
        """Test that a pooled connection still works after being returned and reacquired."""
        engine = create_async_engine(
            async_connection_url, connect_args={"credential": credential}, pool_size=1, max_overflow=0
        )
        enable_entra_authentication_async(engine)

        # First connection: use and return to pool
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        # Second connection: reuse the pooled connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT current_user"))
            assert result.fetchone()[0] is not None

        await engine.dispose()
