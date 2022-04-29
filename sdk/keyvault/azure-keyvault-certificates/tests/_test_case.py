# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os

from azure.keyvault.certificates import ApiVersion
from azure.keyvault.certificates._shared import HttpChallengeCache
from azure.keyvault.certificates._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureMgmtRecordedTestCase, AzureRecordedTestCase, AzureTestCase, PowerShellPreparer, is_live
from parameterized import parameterized, param
import pytest


def client_setup(testcase_func):
    """decorator that creates a client to be passed in to a test method"""
    @PowerShellPreparer("keyvault", azure_keyvault_url="https://vaultname.vault.azure.net")
    @functools.wraps(testcase_func)
    def wrapper(test_class_instance, azure_keyvault_url, api_version, **kwargs):
        test_class_instance._skip_if_not_configured(api_version)
        client = test_class_instance.create_client(azure_keyvault_url, api_version=api_version, **kwargs)

        if kwargs.get("is_async"):
            import asyncio

            coroutine = testcase_func(test_class_instance, client)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(coroutine)
        else:
            testcase_func(test_class_instance, client)
    return wrapper


def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    versions = kwargs.pop("api_versions", None) or ApiVersion
    params = [pytest.param(api_version) for api_version in versions]
    return params


class CertificatesClientPreparer(AzureRecordedTestCase):
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

            #self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            client = self.create_client(self.azure_keyvault_url, api_version=api_version, **kwargs)

            with client:
                fn(test_class, client)
        return _preparer
        
    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.certificates import CertificateClient
        
        credential = self.get_credential(CertificateClient)
        
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
