# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, is_live


class AsyncSecretsClientPreparer(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.azure_keyvault_url = "https://vaultname.vault.azure.net"

        if is_live():
            self.azure_keyvault_url = os.environ["AZURE_KEYVAULT_URL"]

        self.is_logging_enabled = kwargs.pop("logging_enable", True)
        if is_live():
            os.environ["AZURE_TENANT_ID"] = os.environ["KEYVAULT_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["KEYVAULT_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["KEYVAULT_CLIENT_SECRET"]

    def __call__(self, fn):
        async def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            client = self.create_client(self.azure_keyvault_url, api_version=api_version, **kwargs)
            await fn(test_class, client=client)

        return _preparer

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets.aio import SecretClient

        credential = self.get_credential(SecretClient, is_async=True)
        return self.create_client_from_credential(SecretClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
