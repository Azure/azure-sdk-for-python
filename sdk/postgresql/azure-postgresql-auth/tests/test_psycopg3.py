# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for psycopg3 EntraConnection."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError
from azure_postgresql_auth.psycopg3 import EntraConnection

from utils import (
    TEST_USERS,
    MockTokenCredential,
    create_valid_jwt_token,
)


class TestPsycopg3EntraConnection:
    """Tests for psycopg3 sync EntraConnection."""

    def test_missing_credential_raises_error(self):
        """Test that missing credential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            EntraConnection.connect(host="localhost", dbname="test")

    def test_invalid_credential_type_raises_error(self):
        """Test that non-TokenCredential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            EntraConnection.connect(host="localhost", dbname="test", credential="invalid")

    @patch("azure_postgresql_auth.psycopg3.entra_connection.get_entra_conninfo")
    @patch("psycopg.Connection.connect")
    def test_entra_credentials_injected(self, mock_connect, mock_get_conninfo):
        """Test that Entra credentials are injected when user/password missing."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        mock_connect.return_value = MagicMock()
        credential = MockTokenCredential(token)
        EntraConnection.connect(host="localhost", dbname="test", credential=credential)
        mock_get_conninfo.assert_called_once_with(credential)

    @patch("azure_postgresql_auth.psycopg3.entra_connection.get_entra_conninfo")
    @patch("psycopg.Connection.connect")
    def test_existing_credentials_preserved(self, mock_connect, mock_get_conninfo):
        """Test that existing user/password are preserved."""
        mock_connect.return_value = MagicMock()
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        EntraConnection.connect(
            host="localhost",
            dbname="test",
            user="existing",
            password="secret",
            credential=credential,
        )
        mock_get_conninfo.assert_not_called()

    @patch("azure_postgresql_auth.psycopg3.entra_connection.get_entra_conninfo")
    def test_entra_credential_failure_raises_error(self, mock_get_conninfo):
        """Test that credential failure raises EntraConnectionValueError."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        with pytest.raises(EntraConnectionValueError):
            EntraConnection.connect(host="localhost", dbname="test", credential=credential)


@pytest.mark.live_test_only
class TestPsycopg3EntraConnectionLive:
    """Live tests for psycopg3 sync EntraConnection against deployed Azure PostgreSQL."""

    def test_connect_with_entra_user(self, connection_params, credential, postgresql_database):
        """Test connecting with an Entra user using EntraConnection."""
        with EntraConnection.connect(**connection_params, credential=credential) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_user, current_database()")
                current_user, current_db = cur.fetchone()

                assert current_db == postgresql_database
                assert current_user is not None

    def test_execute_query(self, connection_params, credential):
        """Test executing a basic query through EntraConnection."""
        with EntraConnection.connect(**connection_params, credential=credential) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                assert result[0] == 1

    def test_multiple_sequential_connections(self, connection_params, credential):
        """Test that the same credential works across multiple sequential connections."""
        for _ in range(3):
            with EntraConnection.connect(**connection_params, credential=credential) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    assert cur.fetchone()[0] == 1
