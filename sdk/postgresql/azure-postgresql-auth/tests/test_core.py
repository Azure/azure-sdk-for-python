# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for the core authentication module."""

from __future__ import annotations

import pytest

from azure_postgresql_auth.core import (
    AZURE_DB_FOR_POSTGRES_SCOPE,
    AZURE_MANAGEMENT_SCOPE,
    decode_jwt,
    get_entra_conninfo,
    parse_principal_name,
)
from azure_postgresql_auth.errors import TokenDecodeError

from utils import (
    TEST_USERS,
    MockTokenCredential,
    create_jwt_token_with_preferred_username,
    create_jwt_token_with_unique_name,
    create_jwt_token_with_xms_mirid,
    create_valid_jwt_token,
)


class TestDecodeJwt:
    """Tests for decode_jwt function."""

    def test_decode_valid_jwt(self):
        """Test decoding a valid JWT token extracts payload claims."""
        token = create_valid_jwt_token("user@example.com")
        claims = decode_jwt(token)
        assert claims["upn"] == "user@example.com"
        assert claims["iat"] == 1234567890
        assert claims["exp"] == 9999999999

    def test_decode_jwt_with_xms_mirid(self):
        """Test decoding a JWT with xms_mirid claim."""
        xms_mirid = TEST_USERS["MANAGED_IDENTITY_PATH"]
        token = create_jwt_token_with_xms_mirid(xms_mirid)
        claims = decode_jwt(token)
        assert claims["xms_mirid"] == xms_mirid

    def test_decode_jwt_with_preferred_username(self):
        """Test decoding a JWT with preferred_username claim."""
        token = create_jwt_token_with_preferred_username("user@example.com")
        claims = decode_jwt(token)
        assert claims["preferred_username"] == "user@example.com"

    def test_decode_jwt_with_unique_name(self):
        """Test decoding a JWT with unique_name claim."""
        token = create_jwt_token_with_unique_name("user@example.com")
        claims = decode_jwt(token)
        assert claims["unique_name"] == "user@example.com"

    def test_decode_invalid_jwt_raises_error(self):
        """Test that an invalid JWT token raises TokenDecodeError."""
        with pytest.raises(TokenDecodeError, match="Invalid JWT token format"):
            decode_jwt("invalid-token")

    def test_decode_empty_string_raises_error(self):
        """Test that an empty string raises TokenDecodeError."""
        with pytest.raises(TokenDecodeError):
            decode_jwt("")


class TestParsePrincipalName:
    """Tests for parse_principal_name function."""

    def test_parse_valid_managed_identity_path(self):
        """Test extracting principal name from a valid managed identity resource path."""
        xms_mirid = TEST_USERS["MANAGED_IDENTITY_PATH"]
        result = parse_principal_name(xms_mirid)
        assert result == TEST_USERS["MANAGED_IDENTITY_NAME"]

    def test_parse_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert parse_principal_name("") is None

    def test_parse_no_slash_returns_none(self):
        """Test that string with no slashes returns None."""
        assert parse_principal_name("no-slash-here") is None

    def test_parse_wrong_provider_returns_none(self):
        """Test that wrong provider path returns None."""
        assert (
            parse_principal_name("/subscriptions/123/resourcegroups/rg/providers/Microsoft.Wrong/identities/name")
            is None
        )

    def test_parse_trailing_slash_returns_none(self):
        """Test that a path ending with a slash returns None."""
        assert (
            parse_principal_name(
                "/subscriptions/123/resourcegroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/"
            )
            is None
        )


class TestGetEntraConninfo:
    """Tests for get_entra_conninfo function."""

    def test_conninfo_with_upn_claim(self):
        """Test that UPN claim is extracted as username."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        result = get_entra_conninfo(credential)
        assert result["user"] == TEST_USERS["ENTRA_USER"]
        assert result["password"] == token

    def test_conninfo_with_preferred_username(self):
        """Test that preferred_username claim is extracted as username."""
        token = create_jwt_token_with_preferred_username(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        result = get_entra_conninfo(credential)
        assert result["user"] == TEST_USERS["ENTRA_USER"]

    def test_conninfo_with_unique_name(self):
        """Test that unique_name claim is extracted as username."""
        token = create_jwt_token_with_unique_name(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        result = get_entra_conninfo(credential)
        assert result["user"] == TEST_USERS["ENTRA_USER"]

    def test_conninfo_with_managed_identity(self):
        """Test that managed identity xms_mirid claim is parsed for username."""
        token = create_jwt_token_with_xms_mirid(TEST_USERS["MANAGED_IDENTITY_PATH"])
        credential = MockTokenCredential(token)
        result = get_entra_conninfo(credential)
        assert result["user"] == TEST_USERS["MANAGED_IDENTITY_NAME"]

    def test_conninfo_invalid_token_raises_error(self):
        """Test that invalid token raises TokenDecodeError."""
        credential = MockTokenCredential("invalid-token")
        with pytest.raises(TokenDecodeError):
            get_entra_conninfo(credential)

    def test_credential_called_once_for_db_scope(self):
        """Test that credential is called once when UPN found in DB token."""
        token = create_valid_jwt_token(TEST_USERS["ENTRA_USER"])
        credential = MockTokenCredential(token)
        get_entra_conninfo(credential)
        assert credential.get_call_count() == 1

    def test_scope_constants_defined(self):
        """Test that scope constants are defined correctly."""
        assert AZURE_DB_FOR_POSTGRES_SCOPE == "https://ossrdbms-aad.database.windows.net/.default"
        assert AZURE_MANAGEMENT_SCOPE == "https://management.azure.com/.default"
