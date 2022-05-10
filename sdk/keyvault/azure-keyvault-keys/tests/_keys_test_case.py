# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from devtools_testutils import AzureRecordedTestCase


class KeysTestCase(AzureRecordedTestCase):
    def _get_attestation_uri(self):
        playback_uri = "https://fakeattestation.azurewebsites.net"
        if self.is_live:
            real_uri = os.environ.get("AZURE_KEYVAULT_ATTESTATION_URL")
            real_uri = real_uri.rstrip('/')
            if real_uri is None:
                pytest.skip("No AZURE_KEYVAULT_ATTESTATION_URL environment variable")
            return real_uri
        return playback_uri

    def create_crypto_client(self, key, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.crypto.aio import CryptographyClient
            credential = self.get_credential(CryptographyClient,is_async=True)
        else:
            from azure.keyvault.keys.crypto import CryptographyClient
            credential = self.get_credential(CryptographyClient)

        return self.create_client_from_credential(CryptographyClient, credential=credential, key=key, **kwargs)
