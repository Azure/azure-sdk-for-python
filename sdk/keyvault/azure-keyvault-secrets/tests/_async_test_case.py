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
            keyvault_tenant_id = os.getenv("KEYVAULT_TENANT_ID")
            keyvault_client_id = os.getenv("KEYVAULT_CLIENT_ID")
            keyvault_client_secret = os.getenv("KEYVAULT_CLIENT_SECRET")

            if keyvault_tenant_id:
                os.environ["AZURE_TENANT_ID"] = keyvault_tenant_id
            else:
                os.environ.pop("AZURE_TENANT_ID", None)

            if keyvault_client_id:
                os.environ["AZURE_CLIENT_ID"] = keyvault_client_id
            else:
                os.environ.pop("AZURE_CLIENT_ID", None)

            if keyvault_client_secret:
                os.environ["AZURE_CLIENT_SECRET"] = keyvault_client_secret
            else:
                os.environ.pop("AZURE_CLIENT_SECRET", None)

    def __call__(self, fn):
        async def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            client = self.create_client(self.azure_keyvault_url, api_version=api_version, **kwargs)
            await fn(test_class, client)

        return _preparer

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets.aio import SecretClient

        credential = self.get_credential(SecretClient, is_async=True)
        return self.create_client_from_credential(SecretClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
