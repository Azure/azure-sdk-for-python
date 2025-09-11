# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import patch

import pytest
from azure.identity._credentials.vscode import VisualStudioCodeCredential as SyncVisualStudioCodeCredential
from azure.identity.aio._credentials.vscode import VisualStudioCodeCredential
from azure.identity import CredentialUnavailableError


class TestVisualStudioCodeCredentialAsync:
    """Test cases for the asynchronous VisualStudioCodeCredential"""

    @pytest.mark.asyncio
    async def test_credential_uses_sync_credential(self):
        """Test that the async credential uses the sync version."""
        credential = VisualStudioCodeCredential()
        assert isinstance(credential._sync_credential, SyncVisualStudioCodeCredential)

    @pytest.mark.asyncio
    async def test_invalid_auth_record(self):
        """Test that an error is raised if the auth record is nonexistent."""
        # Test with a nonexistent file
        with patch("os.path.expanduser", return_value="nonexistent_file.json"):
            with pytest.raises(CredentialUnavailableError):
                await VisualStudioCodeCredential().get_token_info("https://management.azure.com/.default")
