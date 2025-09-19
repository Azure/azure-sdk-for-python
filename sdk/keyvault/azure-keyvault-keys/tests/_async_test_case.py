# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

import pytest
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AioHttpTransport, HttpRequest
from devtools_testutils import AzureRecordedTestCase


async def get_attestation_token(attestation_uri):
    request = HttpRequest("GET", f"{attestation_uri}/generate-test-token")
    async with AsyncPipeline(transport=AioHttpTransport()) as pipeline:
        response = await pipeline.run(request)
        return json.loads(response.http_response.text())["token"]


class AsyncKeysClientPreparer(AzureRecordedTestCase):
    def __init__(self, *args, **kwargs):
        vault_playback_url = "https://vaultname.vault.azure.net"
        hsm_playback_url = "https://managedhsmvaultname.managedhsm.azure.net"
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

        if self.is_live:
            self.vault_url = os.environ["AZURE_KEYVAULT_URL"]
            hsm = os.environ.get("AZURE_MANAGEDHSM_URL")
            self.managed_hsm_url = hsm if hsm else None
        else:
            self.vault_url = vault_playback_url
            self.managed_hsm_url = hsm_playback_url

        self._set_mgmt_settings_real_values()

    def __call__(self, fn):
        async def _preparer(test_class, api_version, is_hsm, **kwargs):

            self._skip_if_not_configured(is_hsm)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            endpoint_url = self.managed_hsm_url if is_hsm else self.vault_url
            client = self.create_key_client(endpoint_url, api_version=api_version, **kwargs)
            async with client:
                await fn(
                    test_class, client, is_hsm=is_hsm, managed_hsm_url=self.managed_hsm_url, vault_url=self.vault_url
                )

        return _preparer

    def create_key_client(self, vault_uri, **kwargs):

        from azure.keyvault.keys.aio import KeyClient

        credential = self.get_credential(KeyClient, is_async=True)

        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.getenv("KEYVAULT_TENANT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_ID"] = os.getenv("KEYVAULT_CLIENT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_SECRET"] = os.getenv("KEYVAULT_CLIENT_SECRET", "")  # empty for user-based auth

    def _skip_if_not_configured(self, is_hsm):
        if self.is_live and is_hsm and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
