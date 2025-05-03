# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from devtools_testutils import AzureRecordedTestCase


class BaseClientPreparer(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        hsm_playback_url = "https://managedhsmvaultname.managedhsm.azure.net"
        secondary_hsm_playback_url = "https://managedhsmvaultname2.managedhsm.azure.net"

        if self.is_live:
            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            self.secondary_hsm_url = os.environ.get("SECONDARY_MANAGEDHSM_URL")

        else:
            self.managed_hsm_url = hsm_playback_url
            self.secondary_hsm_url = secondary_hsm_playback_url

        self.managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID")
        use_pwsh = os.environ.get("AZURE_TEST_USE_PWSH_AUTH", "false")
        use_cli = os.environ.get("AZURE_TEST_USE_CLI_AUTH", "false")
        use_vscode = os.environ.get("AZURE_TEST_USE_VSCODE_AUTH", "false")
        use_azd = os.environ.get("AZURE_TEST_USE_AZD_AUTH", "false")
        # Only set service principal credentials if user-based auth is not requested
        if use_pwsh == use_cli == use_vscode == use_azd == "false":
            self._set_mgmt_settings_real_values()

    def _skip_if_not_configured(self, **kwargs):
        if self.is_live and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.getenv("KEYVAULT_TENANT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_ID"] = os.getenv("KEYVAULT_CLIENT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_SECRET"] = os.getenv("KEYVAULT_CLIENT_SECRET", "")  # empty for user-based auth


class ClientPreparer(BaseClientPreparer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def __call__(self, fn):
        async def _preparer(test_class, **kwargs):
            self._skip_if_not_configured()
            kwargs["managed_hsm_url"] = self.managed_hsm_url
            client = self.create_client(self.managed_hsm_url, **kwargs)
            upload_client = self.create_client(self.secondary_hsm_url, **kwargs)

            async with client:
                async with upload_client:
                    await fn(test_class, client, upload_client, **kwargs)

        return _preparer

    def create_client(self, hsm_url, **kwargs):
        from azure.keyvault.securitydomain.aio import SecurityDomainClient

        credential = self.get_credential(SecurityDomainClient, is_async=True)
        return self.create_client_from_credential(
            SecurityDomainClient, credential=credential, vault_url=hsm_url, **kwargs
        )
