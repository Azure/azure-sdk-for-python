# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from azure.keyvault.secrets import ApiVersion
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, is_live


def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    return [(api_version) for api_version in ApiVersion]


class SecretsClientPreparer(AzureRecordedTestCase):
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
        def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            client = self.create_client(self.azure_keyvault_url, **kwargs, api_version=api_version)
            with client:
                fn(test_class, client)

        return _preparer

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets import SecretClient

        credential = self.get_credential(SecretClient)
        return self.create_client_from_credential(SecretClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
