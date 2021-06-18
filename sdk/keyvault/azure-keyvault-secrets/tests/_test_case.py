# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.keyvault.secrets import ApiVersion
from azure.keyvault.secrets._shared import HttpChallengeCache
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureTestCase, PowerShellPreparer
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
    params = [param(api_version=api_version, **kwargs) for api_version in ApiVersion]
    return functools.partial(parameterized.expand, params, name_func=suffixed_test_name)


def suffixed_test_name(testcase_func, param_num, param):
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(param.kwargs.get("api_version")))


class SecretsTestCase(AzureTestCase):
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(SecretsTestCase, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.secrets.aio import SecretClient
            credential = self.get_credential(SecretClient, is_async=True)
        else:
            from azure.keyvault.secrets import SecretClient
            credential = self.get_credential(SecretClient)
        return self.create_client_from_credential(
            SecretClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
