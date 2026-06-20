# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os
import platform
import tempfile
from unittest.mock import patch

import pytest

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AuthenticationRecord, CredentialUnavailableError
from azure.identity._constants import AZURE_VSCODE_CLIENT_ID, KnownAuthorities
from azure.identity._credentials.vscode import VisualStudioCodeCredential, load_vscode_auth_record

# Skip all tests in this module when running on PyPy
pytestmark = pytest.mark.skipif(
    platform.python_implementation() == "PyPy", reason="Broker tests are not supported on PyPy"
)


class TestVisualStudioCodeCredential:
    """Test cases for VisualStudioCodeCredential"""

    def test_get_token_info(self):
        """Test getting a token from the credential."""
        valid_data = {
            "tenantId": "12345678-1234-1234-1234-123456789012",
            "clientId": AZURE_VSCODE_CLIENT_ID,
            "username": "user@example.com",
            "homeAccountId": "user.tenant",
            "authority": KnownAuthorities.AZURE_PUBLIC_CLOUD,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(valid_data, tmp_file)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with patch("msal.PublicClientApplication"):
                    with patch("msal.PublicClientApplication.acquire_token_interactive"):
                        credential = VisualStudioCodeCredential()
                        with pytest.raises(ClientAuthenticationError):
                            credential.get_token_info("https://management.azure.com/.default")
        finally:
            os.unlink(tmp_file.name)

    def test_invalid_auth_record(self):
        """Test that an error is raised if the auth record is nonexistent/invalid."""

        # Test with a nonexistent file
        with patch("os.path.expanduser", return_value="nonexistent_file.json"):
            with pytest.raises(CredentialUnavailableError):
                VisualStudioCodeCredential().get_token_info("https://management.azure.com/.default")

        # Test with invalid data (incorrect client ID)
        invalid_data = {
            "tenantId": "12345678-1234-1234-1234-123456789012",
            "clientId": "12345-123456",
            "username": "user@example.com",
            "homeAccountId": "user.tenant",
            "authority": KnownAuthorities.AZURE_PUBLIC_CLOUD,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(invalid_data, tmp_file)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with pytest.raises(CredentialUnavailableError):
                    VisualStudioCodeCredential().get_token_info("https://management.azure.com/.default")
        finally:
            os.unlink(tmp_file.name)

    def test_broker_credential_requirements_not_installed(self):
        """Test that the credential works without the broker installed."""

        with patch.dict("sys.modules", {"azure.identity.broker": None}):
            with pytest.raises(CredentialUnavailableError):
                # This should raise an error because the broker requirements are not installed.
                VisualStudioCodeCredential().get_token_info("https://management.azure.com/.default")


class TestLoadVSCodeAuthRecord:
    """Test cases for loading VS Code authentication records."""

    def test_load_nonexistent_file(self):
        """Test loading returns None when auth record file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            result = load_vscode_auth_record()
            assert result is None

    def test_load_valid_record(self):
        """Test loading a valid authentication record."""
        valid_data = {
            "tenantId": "12345678-1234-1234-1234-123456789012",
            "clientId": AZURE_VSCODE_CLIENT_ID,
            "username": "user@example.com",
            "homeAccountId": "user.tenant",
            "authority": KnownAuthorities.AZURE_PUBLIC_CLOUD,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(valid_data, tmp_file)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with patch("os.path.exists", return_value=True):
                    result = load_vscode_auth_record()

                    assert result is not None
                    assert isinstance(result, AuthenticationRecord)
                    assert result.tenant_id == valid_data["tenantId"]
                    assert result.client_id == valid_data["clientId"]
                    assert result.username == valid_data["username"]
                    assert result.home_account_id == valid_data["homeAccountId"]
                    assert result.authority == valid_data["authority"]
        finally:
            os.unlink(tmp_file.name)

    def test_load_malformed_json(self):
        """Test loading fails with malformed JSON."""
        malformed_json = '{"tenantId": "test", "clientId": '  # incomplete JSON

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            tmp_file.write(malformed_json)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with patch("os.path.exists", return_value=True):
                    with pytest.raises(ValueError):
                        load_vscode_auth_record()
        finally:
            os.unlink(tmp_file.name)

    def test_load_invalid_record(self):
        """Test loading fails with invalid authentication record data."""
        invalid_data = {
            "tenantId": "12345678-1234-1234-1234-123456789012",
            "clientId": "wrong-client-id",  # Invalid client ID
            "username": "user@example.com",
            "homeAccountId": "user.tenant",
            "authority": KnownAuthorities.AZURE_PUBLIC_CLOUD,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(invalid_data, tmp_file)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with patch("os.path.exists", return_value=True):
                    with pytest.raises(ValueError, match="Authentication record validation failed"):
                        load_vscode_auth_record()
        finally:
            os.unlink(tmp_file.name)

    def test_load_missing_required_fields(self):
        """Test loading fails when required fields are missing."""
        incomplete_data = {
            "tenantId": "12345678-1234-1234-1234-123456789012",
            "clientId": AZURE_VSCODE_CLIENT_ID,
            # Missing username, homeAccountId, authority
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(incomplete_data, tmp_file)
            tmp_file.flush()

        try:
            with patch("os.path.expanduser", return_value=tmp_file.name):
                with patch("os.path.exists", return_value=True):
                    with pytest.raises(ValueError) as exc_info:
                        load_vscode_auth_record()

                    error_message = str(exc_info.value)
                    assert "username field is missing" in error_message
                    assert "homeAccountId field is missing" in error_message
                    assert "authority field is missing" in error_message
        finally:
            os.unlink(tmp_file.name)
