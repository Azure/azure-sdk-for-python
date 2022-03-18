# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import functools
from aiohttp import client

from azure.keyvault.secrets import ApiVersion
from azure.keyvault.secrets._shared import HttpChallengeCache
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, is_live
import pytest
from typing import ContextManager, Iterator, Optional



def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    return [(api_version) for api_version in ApiVersion]


class SecretsTestCaseClientPrepaper(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.azure_keyvault_url = os.getenv("AZURE_KEYVAULT_URL", "https://vaultname.vault.azure.net") if is_live() else "https://vaultname.vault.azure.net"
        self.is_async = kwargs.pop("is_async", False)
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

    def __call__(self, fn):
        def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({'logging_enable':False})
            client = self.create_client(self.azure_keyvault_url, **kwargs, api_version=api_version)
            with client:
                fn(test_class, client)
        return _preparer

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets import SecretClient
        credential = self.get_credential(SecretClient)
        return self.create_client_from_credential(
            SecretClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")