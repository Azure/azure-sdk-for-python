# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for psycopg2 EntraConnection."""

from __future__ import annotations
import sys

from unittest.mock import patch

import pytest

from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError

from utils import TEST_USERS, MockTokenCredential, create_valid_jwt_token

if sys.implementation.name != "pypy":
    import psycopg2
    from azure_postgresql_auth.psycopg2 import EntraConnection
else:
    pytest.skip("psycopg2 not supported on PyPy", allow_module_level=True)


class TestPsycopg2EntraConnection:
    """Tests for psycopg2 EntraConnection class."""

    def test_missing_credential_raises_error(self):
        """Test that missing credential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            EntraConnection("host=localhost dbname=test")

    def test_invalid_credential_type_raises_error(self):
        """Test that non-TokenCredential raises CredentialValueError."""
        with pytest.raises(CredentialValueError, match="credential is required"):
            EntraConnection("host=localhost dbname=test", credential="not-a-credential")

    @patch("azure_postgresql_auth.psycopg2.entra_connection.get_entra_conninfo")
    def test_entra_credentials_injected(self, mock_get_conninfo):
        """Test that Entra credentials are injected when user/password missing."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)
        # super().__init__ will raise OperationalError (no real DB), but
        # credential logic runs before the connection attempt.
        with pytest.raises(psycopg2.OperationalError):
            EntraConnection("host=localhost dbname=test", credential=credential)
        mock_get_conninfo.assert_called_once_with(credential)

    @patch("azure_postgresql_auth.psycopg2.entra_connection.get_entra_conninfo")
    def test_existing_credentials_preserved(self, mock_get_conninfo):
        """Test that existing user/password in DSN are preserved."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        with pytest.raises(psycopg2.OperationalError):
            EntraConnection(
                "host=localhost dbname=test user=existing password=secret",
                credential=credential,
            )
        mock_get_conninfo.assert_not_called()


class TestPsycopg2EntraConnectionErrors:
    """Tests for error handling in psycopg2 EntraConnection."""

    @patch("azure_postgresql_auth.psycopg2.entra_connection.get_entra_conninfo")
    def test_entra_credential_failure_raises_error(self, mock_get_conninfo):
        """Test that credential retrieval failure raises EntraConnectionValueError."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        with pytest.raises(EntraConnectionValueError, match="Could not retrieve Entra credentials"):
            EntraConnection("host=localhost dbname=test", credential=credential)


@pytest.mark.live_test_only
class TestPsycopg2EntraConnectionLive:
    """Live tests for psycopg2 EntraConnection against deployed Azure PostgreSQL."""

    def test_connect_with_entra_user(self, connection_dsn, credential, postgresql_database):
        """Test connecting with an Entra user using EntraConnection."""
        with EntraConnection(connection_dsn, credential=credential) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_user, current_database()")
                row = cur.fetchone()
                assert row is not None
                current_user, current_db = row

                assert current_db == postgresql_database
                assert current_user is not None

    def test_execute_query(self, connection_dsn, credential):
        """Test executing a basic query through EntraConnection."""
        with EntraConnection(connection_dsn, credential=credential) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()
                assert row is not None
                assert row[0] == 1

    def test_multiple_sequential_connections(self, connection_dsn, credential):
        """Test that the same credential works across multiple sequential connections."""
        for _ in range(3):
            with EntraConnection(connection_dsn, credential=credential) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    assert cur.fetchone()[0] == 1
