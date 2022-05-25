# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta
import functools
import os

from azure.keyvault.administration import ApiVersion
from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION
from azure.storage.blob import AccountSasPermissions, generate_account_sas, ResourceTypes
from devtools_testutils import AzureTestCase
from parameterized import parameterized, param
import pytest
from six.moves.urllib_parse import urlparse


def access_control_client_setup(testcase_func):
    """decorator that creates a KeyVaultAccessControlClient to be passed in to a test method"""

    @functools.wraps(testcase_func)
    def wrapper(test_class_instance, api_version, **kwargs):
        test_class_instance._skip_if_not_configured(api_version)
        client = test_class_instance.create_access_control_client(api_version=api_version, **kwargs)

        if kwargs.get("is_async"):
            import asyncio

            coroutine = testcase_func(test_class_instance, client)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(coroutine)
        else:
            testcase_func(test_class_instance, client)

    return wrapper


def backup_client_setup(testcase_func):
    """decorator that creates a KeyVaultBackupClient to be passed in to a test method"""

    @functools.wraps(testcase_func)
    def wrapper(test_class_instance, api_version, **kwargs):
        test_class_instance._skip_if_not_configured(api_version)
        client = test_class_instance.create_backup_client(api_version=api_version, **kwargs)

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
    params = [param(api_version=api_version, **kwargs) for api_version in versions]
    return functools.partial(parameterized.expand, params, name_func=suffixed_test_name)


def suffixed_test_name(testcase_func, param_num, param):
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(param.kwargs.get("api_version")))


class AdministrationTestCase(AzureTestCase):
    def setUp(self, *args, **kwargs):
        hsm_playback_url = "https://managedhsmname.managedhsm.azure.net"
        container_playback_uri = "https://storagename.blob.core.windows.net/container"
        playback_sas_token = "fake-sas"

        if self.is_live:
            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            if self.managed_hsm_url:
                self._scrub_url(real_url=self.managed_hsm_url, playback_url=hsm_playback_url)

            storage_name = os.environ.get("BLOB_STORAGE_ACCOUNT_NAME")
            storage_endpoint_suffix = os.environ.get("KEYVAULT_STORAGE_ENDPOINT_SUFFIX")
            container_name = os.environ.get("BLOB_CONTAINER_NAME")
            self.container_uri = "https://{}.blob.{}/{}".format(storage_name, storage_endpoint_suffix, container_name)
            self._scrub_url(real_url=self.container_uri, playback_url=container_playback_uri)

            self.sas_token = os.environ.get("BLOB_STORAGE_SAS_TOKEN")
            if self.sas_token:
                self.scrubber.register_name_pair(self.sas_token, playback_sas_token)
        else:
            self.managed_hsm_url = hsm_playback_url
            self.container_uri = container_playback_uri
            self.sas_token = playback_sas_token

        self._set_mgmt_settings_real_values()
        super(AdministrationTestCase, self).setUp(*args, **kwargs)

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(AdministrationTestCase, self).tearDown()

    def create_access_control_client(self, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.administration.aio import KeyVaultAccessControlClient

            credential = self.get_credential(KeyVaultAccessControlClient, is_async=True)
        else:
            from azure.keyvault.administration import KeyVaultAccessControlClient

            credential = self.get_credential(KeyVaultAccessControlClient)
        return self.create_client_from_credential(
            KeyVaultAccessControlClient, credential=credential, vault_url=self.managed_hsm_url, **kwargs
        )

    def create_backup_client(self, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.administration.aio import KeyVaultBackupClient

            credential = self.get_credential(KeyVaultBackupClient, is_async=True)
        else:
            from azure.keyvault.administration import KeyVaultBackupClient

            credential = self.get_credential(KeyVaultBackupClient)
        return self.create_client_from_credential(
            KeyVaultBackupClient, credential=credential, vault_url=self.managed_hsm_url, **kwargs
        )

    def create_key_client(self, vault_uri, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.aio import KeyClient

            credential = self.get_credential(KeyClient, is_async=True)
        else:
            from azure.keyvault.keys import KeyClient

            credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _scrub_url(self, real_url, playback_url):
        real = urlparse(real_url)
        playback = urlparse(playback_url)
        self.scrubber.register_name_pair(real.netloc, playback.netloc)

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.environ["KEYVAULT_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["KEYVAULT_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["KEYVAULT_CLIENT_SECRET"]

    def _skip_if_not_configured(self, api_version, **kwargs):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
        if self.is_live and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
