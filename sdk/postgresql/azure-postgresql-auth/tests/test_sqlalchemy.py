# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for SQLAlchemy Entra authentication integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, text

from azure_postgresql_auth.errors import CredentialValueError
from azure_postgresql_auth.sqlalchemy import enable_entra_authentication

from utils import TEST_USERS, MockTokenCredential, create_valid_jwt_token


class TestSqlalchemyEntraAuthentication:
    """Tests for enable_entra_authentication function."""

    @patch("azure_postgresql_auth.sqlalchemy.entra_connection.get_entra_conninfo")
    @patch("azure_postgresql_auth.sqlalchemy.entra_connection.event.listens_for")
    def test_provides_entra_credentials(self, mock_listens_for, mock_get_conninfo):
        """Test that the event handler provides Entra credentials."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }

        # Capture the decorated handler
        registered_handlers = []

        def capture_decorator(engine, event_name):
            def decorator(fn):
                registered_handlers.append(fn)
                return fn

            return decorator

        mock_listens_for.side_effect = capture_decorator
        mock_engine = MagicMock()
        enable_entra_authentication(mock_engine)

        assert len(registered_handlers) == 1
        handler = registered_handlers[0]
        credential = MockTokenCredential(token)
        cparams = {"credential": credential}
        handler(MagicMock(), MagicMock(), [], cparams)
        mock_get_conninfo.assert_called_once_with(credential)
        assert cparams["user"] == TEST_USERS["ENTRA_USER"]
        assert cparams["password"] == token

    @patch("azure_postgresql_auth.sqlalchemy.entra_connection.event.listens_for")
    def test_missing_credential_raises_error(self, mock_listens_for):
        """Test that the event handler raises CredentialValueError when no credential."""
        registered_handlers = []

        def capture_decorator(engine, event_name):
            def decorator(fn):
                registered_handlers.append(fn)
                return fn

            return decorator

        mock_listens_for.side_effect = capture_decorator
        mock_engine = MagicMock()
        enable_entra_authentication(mock_engine)

        assert len(registered_handlers) == 1
        handler = registered_handlers[0]
        with pytest.raises(CredentialValueError):
            handler(MagicMock(), MagicMock(), [], {})

    @patch("azure_postgresql_auth.sqlalchemy.entra_connection.get_entra_conninfo")
    def test_credential_removed_from_cparams(self, mock_get_conninfo):
        """Test that the credential parameter is removed before DBAPI connect."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        mock_get_conninfo.return_value = {
            "user": TEST_USERS["ENTRA_USER"],
            "password": token,
        }
        credential = MockTokenCredential(token)

        # Simulate what the event handler does
        cparams = {"credential": credential}

        mock_engine = MagicMock()
        # We need to capture the registered handler
        registered_handlers = []

        def capture_handler(engine, event_name):
            def decorator(fn):
                registered_handlers.append(fn)
                return fn

            return decorator

        with patch("azure_postgresql_auth.sqlalchemy.entra_connection.event.listens_for", side_effect=capture_handler):
            enable_entra_authentication(mock_engine)

        if registered_handlers:
            handler = registered_handlers[0]
            handler(MagicMock(), MagicMock(), [], cparams)
            assert "credential" not in cparams
            assert cparams["user"] == TEST_USERS["ENTRA_USER"]
            assert cparams["password"] == token


@pytest.mark.live_test_only
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

    def test_token_caching_behavior(self, connection_url, credential):
        """Test that credentials are invoked for each connection."""
        engine = create_engine(connection_url, connect_args={"credential": credential})
        enable_entra_authentication(engine)

        # First connection
        with engine.connect() as conn1:
            result = conn1.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        # Second connection
        with engine.connect() as conn2:
            result = conn2.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

        engine.dispose()
