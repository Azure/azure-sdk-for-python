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
