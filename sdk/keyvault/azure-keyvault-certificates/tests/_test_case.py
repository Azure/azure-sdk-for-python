# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.certificates import ApiVersion
from azure.keyvault.certificates._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, is_live
import pytest


def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    versions = kwargs.pop("api_versions", None) or ApiVersion
    params = [pytest.param(api_version) for api_version in versions]
    return params


class CertificatesClientPreparer(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.azure_keyvault_url = "https://vaultname.vault.azure.net"

        self.is_logging_enabled = kwargs.pop("logging_enable", True)

        if is_live():
            self.azure_keyvault_url = os.environ["AZURE_KEYVAULT_URL"]
            # Only set AZURE_* vars if the KEYVAULT_* counterpart is non-empty.
            # Setting them to empty strings causes EnvironmentCredential to attempt (and fail)
            # ClientSecretCredential construction. Removing them lets DefaultAzureCredential
            # fall through to AzureCliCredential for developer/interactive auth.
            for keyvault_var, azure_var in (
                ("KEYVAULT_TENANT_ID", "AZURE_TENANT_ID"),
                ("KEYVAULT_CLIENT_ID", "AZURE_CLIENT_ID"),
                ("KEYVAULT_CLIENT_SECRET", "AZURE_CLIENT_SECRET"),
            ):
                value = os.getenv(keyvault_var, "")
                if value:
                    os.environ[azure_var] = value
                else:
                    os.environ.pop(azure_var, None)

    def __call__(self, fn):
        def _preparer(test_class, api_version, **kwargs):

            self._skip_if_not_configured(api_version)
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
