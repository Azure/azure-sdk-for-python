# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys
import pytest

from azure.identity import ManagedIdentityCredential
from azure.identity._credentials.imds import ImdsCredential

from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
from azure.identity.aio._credentials.imds import ImdsCredential as AsyncImdsCredential


class TestAzureVirtualMachinesIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Test resource deployment only works on Linux.")
    def test_azure_virtual_machine_integration_sync(self):
        """Test using the Azure Virtual Machine that the CI provisions."""

        credential = ManagedIdentityCredential()
        token = credential.get_token("https://management.azure.com/.default")
        assert isinstance(credential._credential, ImdsCredential)
        assert token.token

    @pytest.mark.live_test_only
    @pytest.mark.asyncio
    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Test resource deployment only works on Linux.")
    async def test_azure_virtual_machine_integration_async(self):
        """Test using the Azure Virtual Machine that the CI provisions."""

        credential = AsyncManagedIdentityCredential()
        token = await credential.get_token("https://management.azure.com/.default")
        assert isinstance(credential._credential, AsyncImdsCredential)
        assert token.token
