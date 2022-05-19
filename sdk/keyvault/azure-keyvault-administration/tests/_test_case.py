# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from azure.keyvault.administration import ApiVersion
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase


class BaseClientPreparer(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        hsm_playback_url = "https://managedhsmvaultname.vault.azure.net"
        container_playback_uri = "https://storagename.blob.core.windows.net/container"
        playback_sas_token = "fake-sas"

        if self.is_live:
            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            storage_name = os.environ.get("BLOB_STORAGE_ACCOUNT_NAME")
            storage_endpoint_suffix = os.environ.get("KEYVAULT_STORAGE_ENDPOINT_SUFFIX")
            container_name = os.environ.get("BLOB_CONTAINER_NAME")
            self.container_uri = "https://{}.blob.{}/{}".format(storage_name, storage_endpoint_suffix, container_name)

            self.sas_token = os.environ.get("BLOB_STORAGE_SAS_TOKEN")
            
        else:
            self.managed_hsm_url = hsm_playback_url
            self.container_uri = container_playback_uri
            self.sas_token = playback_sas_token

        self._set_mgmt_settings_real_values()
    
    def _skip_if_not_configured(self, api_version, **kwargs):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
        if self.is_live and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.environ["KEYVAULT_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["KEYVAULT_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["KEYVAULT_CLIENT_SECRET"]



class KeyVaultBackupClientPreparer(BaseClientPreparer):
    def __init__(self, **kwargs) -> None:
       super().__init__(**kwargs)

    def __call__(self, fn):
        def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            kwargs["container_uri"] = self.container_uri
            kwargs["sas_token"] = self.sas_token
            kwargs["managed_hsm_url"] = self.managed_hsm_url
            client = self.create_backup_client(api_version=api_version, **kwargs)

            with client:
                fn(test_class, client, **kwargs)
        return _preparer

    def create_backup_client(self, **kwargs):
        from azure.keyvault.administration import KeyVaultBackupClient

        credential = self.get_credential(KeyVaultBackupClient)
        return self.create_client_from_credential(
            KeyVaultBackupClient, credential=credential, vault_url=self.managed_hsm_url, **kwargs
        )


class KeyVaultAccessControlClientPreparer(BaseClientPreparer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, fn):
        def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            client = self.create_access_control_client(api_version=api_version, **kwargs)

            with client:
                fn(test_class, client, **kwargs)
        return _preparer

    def create_access_control_client(self, **kwargs):
        from azure.keyvault.administration import KeyVaultAccessControlClient

        credential = self.get_credential(KeyVaultAccessControlClient)
        return self.create_client_from_credential(
            KeyVaultAccessControlClient, credential=credential, vault_url=self.managed_hsm_url, **kwargs
        )



def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    versions = kwargs.pop("api_versions", None) or ApiVersion
    params = [pytest.param(api_version) for api_version in versions]
    return params
