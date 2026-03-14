# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for SQLAlchemy Entra authentication integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, text

from azure_postgresql_auth.errors import CredentialValueError, EntraConnectionValueError
from azure_postgresql_auth.sqlalchemy import enable_entra_authentication

from utils import TEST_USERS, MockTokenCredential, capture_event_handler, create_valid_jwt_token

SYNC_MODULE = "azure_postgresql_auth.sqlalchemy.entra_connection"


class TestSqlalchemyEntraAuthentication:
    """Tests for enable_entra_authentication function."""

    @patch(f"{SYNC_MODULE}.get_entra_conninfo")
    def test_provides_entra_credentials(self, mock_get_conninfo):
        """Test that the event handler provides Entra credentials."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }

        handler, mock_listens_for, mock_engine = capture_event_handler(enable_entra_authentication, SYNC_MODULE)
        mock_listens_for.assert_called_once_with(mock_engine, "do_connect")

        credential = MockTokenCredential(token)
        cparams = {"credential": credential}
        handler(MagicMock(), MagicMock(), [], cparams)
        mock_get_conninfo.assert_called_once_with(credential)
        assert cparams["user"] == TEST_USERS["ENTRA_USER"]
        assert cparams["password"] == token

    def test_missing_credential_raises_error(self):
        """Test that the event handler raises CredentialValueError when no credential."""
        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)
        with pytest.raises(CredentialValueError):
            handler(MagicMock(), MagicMock(), [], {})

    @pytest.mark.parametrize(
        "credential_value",
        [None, "not-a-credential", 12345],
        ids=["none", "string", "int"],
    )
    def test_invalid_credential_raises_error(self, credential_value):
        """Test that non-TokenCredential values raise CredentialValueError."""
        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)
        with pytest.raises(CredentialValueError):
            handler(MagicMock(), MagicMock(), [], {"credential": credential_value})

    @patch(f"{SYNC_MODULE}.get_entra_conninfo")
    def test_credential_removed_from_cparams(self, mock_get_conninfo):
        """Test that the credential parameter is removed before DBAPI connect."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)
        cparams = {"credential": credential}

        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)
        handler(MagicMock(), MagicMock(), [], cparams)
        assert "credential" not in cparams
        assert cparams["user"] == TEST_USERS["ENTRA_USER"]
        assert cparams["password"] == token

    @patch(f"{SYNC_MODULE}.get_entra_conninfo")
    def test_existing_credentials_preserved(self, mock_get_conninfo):
        """Test that existing user/password in cparams are preserved."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)

        cparams = {"credential": credential, "user": "existing", "password": "secret"}
        handler(MagicMock(), MagicMock(), [], cparams)

        mock_get_conninfo.assert_not_called()
        assert cparams["user"] == "existing"
        assert cparams["password"] == "secret"
        assert "credential" not in cparams

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
    @patch(f"{SYNC_MODULE}.get_entra_conninfo")
    def test_partial_credentials_trigger_entra_lookup(self, mock_get_conninfo, cparams_extra, should_call):
        """Test that get_entra_conninfo is called when user or password is missing."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)

        cparams = {"credential": credential, **cparams_extra}
        handler(MagicMock(), MagicMock(), [], cparams)

        if should_call:
            mock_get_conninfo.assert_called_once_with(credential)
        else:
            mock_get_conninfo.assert_not_called()

    @patch(f"{SYNC_MODULE}.get_entra_conninfo")
    def test_entra_credential_failure_raises_error(self, mock_get_conninfo):
        """Test that credential retrieval failure raises EntraConnectionValueError."""
        mock_get_conninfo.side_effect = Exception("auth failed")
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)

        handler, _, _ = capture_event_handler(enable_entra_authentication, SYNC_MODULE)

        with pytest.raises(EntraConnectionValueError, match="Could not retrieve Entra credentials"):
            handler(MagicMock(), MagicMock(), [], {"credential": credential})


@pytest.mark.live_test_only
@pytest.mark.skipif(sys.implementation.name == "pypy", reason="psycopg2 not supported on PyPy")
class TestSqlalchemyEntraAuthenticationLive:
    """Live tests for synchronous SQLAlchemy with enable_entra_authentication."""

    def test_connect_with_entra_user(self, connection_url, credential, postgresql_database):
        """Test connecting with an Entra user using enable_entra_authentication."""
        engine = create_engine(connection_url, connect_args={"credential": credential})
        enable_entra_authentication(engine)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_user, current_database()"))
            current_user, current_db = result.fetchone()

            assert current_db == postgresql_database
            assert current_user is not None

        engine.dispose()

    def test_execute_query(self, connection_url, credential):
        """Test executing a basic query through SQLAlchemy with Entra auth."""
        engine = create_engine(connection_url, connect_args={"credential": credential})
        enable_entra_authentication(engine)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        engine.dispose()

    def test_multiple_sequential_connections(self, connection_url, credential):
        """Test that the same credential works across multiple sequential connections."""
        engine = create_engine(connection_url, connect_args={"credential": credential})
        enable_entra_authentication(engine)

        for _ in range(3):
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1

        engine.dispose()

    def test_connection_pool_reuse(self, connection_url, credential):
        """Test that a pooled connection still works after being returned and reacquired."""
        engine = create_engine(connection_url, connect_args={"credential": credential}, pool_size=1, max_overflow=0)
        enable_entra_authentication(engine)

        # First connection: use and return to pool
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        # Second connection: reuse the pooled connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_user"))
            assert result.fetchone()[0] is not None

        engine.dispose()
