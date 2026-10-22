# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Common utility functions and test credentials for unit tests."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

# Test user constants
TEST_USERS = {
    "ENTRA_USER": "test@example.com",
    "MANAGED_IDENTITY_PATH": "/subscriptions/12345/resourcegroups/group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/managed-identity",
    "MANAGED_IDENTITY_NAME": "managed-identity",
    "FALLBACK_USER": "fallback@example.com",
}


def create_base64_url_string(input_str: str) -> str:
    """Create a base64url encoded string."""
    encoded = base64.urlsafe_b64encode(input_str.encode()).decode()
    return encoded.rstrip("=")


def create_valid_jwt_token(username: str) -> str:
    """Create a fake JWT token with a UPN claim."""
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"upn": username, "iat": 1234567890, "exp": 9999999999}
    header_encoded = create_base64_url_string(json.dumps(header))
    payload_encoded = create_base64_url_string(json.dumps(payload))
    return f"{header_encoded}.{payload_encoded}.fake-signature"


def create_jwt_token_with_xms_mirid(xms_mirid: str) -> str:
    """Create a fake JWT token with an xms_mirid claim for managed identity."""
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"xms_mirid": xms_mirid, "iat": 1234567890, "exp": 9999999999}
    header_encoded = create_base64_url_string(json.dumps(header))
    payload_encoded = create_base64_url_string(json.dumps(payload))
    return f"{header_encoded}.{payload_encoded}.fake-signature"


def create_jwt_token_with_preferred_username(username: str) -> str:
    """Create a fake JWT token with a preferred_username claim."""
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"preferred_username": username, "iat": 1234567890, "exp": 9999999999}
    header_encoded = create_base64_url_string(json.dumps(header))
    payload_encoded = create_base64_url_string(json.dumps(payload))
    return f"{header_encoded}.{payload_encoded}.fake-signature"


def create_jwt_token_with_unique_name(username: str) -> str:
    """Create a fake JWT token with a unique_name claim."""
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {"unique_name": username, "iat": 1234567890, "exp": 9999999999}
    header_encoded = create_base64_url_string(json.dumps(header))
    payload_encoded = create_base64_url_string(json.dumps(payload))
    return f"{header_encoded}.{payload_encoded}.fake-signature"


def capture_event_handler(enable_fn, mock_module_path):
    """Patch event.listens_for, call enable_fn, and return the captured handler.

    :param enable_fn: The enable_entra_authentication[_async] function to call.
    :param mock_module_path: The module path prefix to patch (e.g.
        "azure_postgresql_auth.sqlalchemy.entra_connection").
    :returns: A tuple of (handler, mock_listens_for) where handler is the
        captured event handler function and mock_listens_for is the mock
        for asserting registration arguments.
    """
    registered_handlers = []
    mock_listens_for = MagicMock()

    def capture_decorator(*args, **kwargs):
        mock_listens_for(*args, **kwargs)

        def decorator(fn):
            registered_handlers.append(fn)
            return fn

        return decorator

    with patch(f"{mock_module_path}.event.listens_for", side_effect=capture_decorator):
        mock_engine = MagicMock()
        enable_fn(mock_engine)

    assert len(registered_handlers) == 1, "Expected exactly one event handler to be registered"
    return registered_handlers[0], mock_listens_for, mock_engine


class MockTokenCredential(TokenCredential):
    """Mock token credential for synchronous operations."""

    def __init__(self, token: str):
        self._token = token
        self._call_count = 0

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        """Return a fake access token."""
        self._call_count += 1
        expires_on = datetime.now(timezone.utc) + timedelta(hours=1)
        return AccessToken(self._token, int(expires_on.timestamp()))

    def get_call_count(self) -> int:
        """Return the number of times get_token was called."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset the call count."""
        self._call_count = 0


class MockAsyncTokenCredential(AsyncTokenCredential):
    """Mock token credential for asynchronous operations."""

    def __init__(self, token: str):
        self._token = token
        self._call_count = 0

    async def get_token(self, *scopes, **kwargs) -> AccessToken:
        """Return a fake access token asynchronously."""
        self._call_count += 1
        expires_on = datetime.now(timezone.utc) + timedelta(hours=1)
        return AccessToken(self._token, int(expires_on.timestamp()))

    async def close(self) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def get_call_count(self) -> int:
        """Return the number of times get_token was called."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset the call count."""
        self._call_count = 0
