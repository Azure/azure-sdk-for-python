# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Async unit tests for psycopg3 AsyncEntraConnection."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError
from azure_postgresql_auth.psycopg3 import AsyncEntraConnection

from utils import (
    TEST_USERS,
    MockAsyncTokenCredential,
    create_valid_jwt_token,
)


class TestPsycopg3AsyncEntraConnection:
    """Tests for psycopg3 async AsyncEntraConnection."""

    @pytest.mark.asyncio
    async def test_missing_credential_raises_error(self):
        """Test that missing credential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            await AsyncEntraConnection.connect(host="localhost", dbname="test")

    @pytest.mark.asyncio
    async def test_invalid_credential_type_raises_error(self):
        """Test that non-AsyncTokenCredential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            await AsyncEntraConnection.connect(host="localhost", dbname="test", credential="invalid")

    @pytest.mark.asyncio
    @patch("azure_postgresql_auth.psycopg3.async_entra_connection.get_entra_conninfo_async")
    @patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock)
    async def test_entra_credentials_injected_async(self, mock_connect, mock_get_conninfo):
        """Test that Entra credentials are injected when user/password missing (async)."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        mock_connect.return_value = MagicMock()
        credential = MockAsyncTokenCredential(token)
        await AsyncEntraConnection.connect(host="localhost", dbname="test", credential=credential)
        mock_get_conninfo.assert_called_once_with(credential)

    @pytest.mark.asyncio
    @patch("azure_postgresql_auth.psycopg3.async_entra_connection.get_entra_conninfo_async")
    @patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock)
    async def test_existing_credentials_preserved_async(self, mock_connect, mock_get_conninfo):
        """Test that existing user/password are preserved (async)."""
        mock_connect.return_value = MagicMock()
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockAsyncTokenCredential(token)
        await AsyncEntraConnection.connect(
            host="localhost",
            dbname="test",
            user="existing",
            password="secret",
            credential=credential,
        )
        mock_get_conninfo.assert_not_called()

    @pytest.mark.asyncio
    @patch("azure_postgresql_auth.psycopg3.async_entra_connection.get_entra_conninfo_async")
    async def test_entra_credential_failure_raises_error_async(self, mock_get_conninfo):
        """Test that credential failure raises EntraConnectionValueError (async)."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockAsyncTokenCredential(token)

        with pytest.raises(EntraConnectionValueError):
            await AsyncEntraConnection.connect(host="localhost", dbname="test", credential=credential)


@pytest.mark.live_test_only
class TestPsycopg3AsyncEntraConnectionLive:
    """Live tests for psycopg3 async AsyncEntraConnection against deployed Azure PostgreSQL."""

    @pytest.mark.asyncio
    async def test_connect_with_entra_user_async(self, connection_params, async_credential, postgresql_database):
        """Test connecting with an Entra user using AsyncEntraConnection."""
        async with await AsyncEntraConnection.connect(**connection_params, credential=async_credential) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT current_user, current_database()")
                result = await cur.fetchone()
                current_user, current_db = result

                assert current_db == postgresql_database
                assert current_user is not None

    @pytest.mark.asyncio
    async def test_execute_query_async(self, connection_params, async_credential):
        """Test executing a basic query through AsyncEntraConnection."""
        async with await AsyncEntraConnection.connect(**connection_params, credential=async_credential) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                assert result[0] == 1

    @pytest.mark.asyncio
    async def test_multiple_sequential_connections_async(self, connection_params, async_credential):
        """Test that the same credential works across multiple sequential connections."""
        for _ in range(3):
            async with await AsyncEntraConnection.connect(**connection_params, credential=async_credential) as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    assert result[0] == 1

    @pytest.mark.asyncio
    async def test_concurrent_async_connections(self, connection_params, async_credential):
        """Test that multiple concurrent async connections work with the same credential."""

        async def query():
            async with await AsyncEntraConnection.connect(**connection_params, credential=async_credential) as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    return result[0]

        results = await asyncio.gather(query(), query(), query())
        assert results == [1, 1, 1]
