# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
import functools
from types import coroutine
from aiohttp import client

from azure.keyvault.secrets import ApiVersion
from azure.keyvault.secrets._shared import HttpChallengeCache
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, is_live
import pytest


KeyVaultSecretsPreparer = functools.partial(PowerShellPreparer, "keyvault", azure_keyvault_url="https://vaultname.vault.azure.net")


class AsyncSecretsTestCaseClientPrepaper(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.azure_keyvault_url = os.getenv("AZURE_KEYVAULT_URL", "https://vaultname.vault.azure.net")
        self.is_async = kwargs.pop("is_async", False)
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

    def __call__(self, fn):
        async def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({'logging_enable':False})
            client = self.create_client(self.azure_keyvault_url, api_version=api_version,**kwargs)
            await fn(test_class, client)
        return _preparer

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        #super(SecretsTestCaseClientPrepaper, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets.aio import SecretClient
        
        credential = self.get_credential(SecretClient, is_async=True)
        return self.create_client_from_credential(
            SecretClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
