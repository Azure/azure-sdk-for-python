# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.keys._shared import HttpChallengeCache
from devtools_testutils import AzureTestCase
from parameterized import parameterized
import pytest
from six.moves.urllib_parse import urlparse


def suffixed_test_name(testcase_func, param_num, param):
    suffix = "mhsm" if param.kwargs.get("is_hsm") else "vault"
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(suffix))


class KeysTestCase(AzureTestCase):
    def setUp(self, *args, **kwargs):
        vault_playback_url = "https://vaultname.vault.azure.net"
        hsm_playback_url = "https://managedhsmname.managedhsm.azure.net"

        if self.is_live:
            self.vault_url = os.environ["AZURE_KEYVAULT_URL"]
            self._scrub_url(real_url=self.vault_url, playback_url=vault_playback_url)

            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            if self.managed_hsm_url:
                self._scrub_url(real_url=self.managed_hsm_url, playback_url=hsm_playback_url)
        else:
            self.vault_url = vault_playback_url
            self.managed_hsm_url = hsm_playback_url

        self._set_mgmt_settings_real_values()
        super(KeysTestCase, self).setUp(*args, **kwargs)
    
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeysTestCase, self).tearDown()

    def create_key_client(self, vault_uri, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.aio import KeyClient
            credential = self.get_credential(KeyClient, is_async=True)
        else:
            from azure.keyvault.keys import KeyClient
            credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)
    
    def create_crypto_client(self, key,**kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.crypto.aio import CryptographyClient
            credential = self.get_credential(CryptographyClient, is_async=True)
        else:
            from azure.keyvault.keys.crypto import CryptographyClient
            credential = self.get_credential(CryptographyClient)
        return self.create_client_from_credential(CryptographyClient, credential=credential, key=key, **kwargs)
    
    def _scrub_url(self, real_url, playback_url):
        real = urlparse(real_url)
        playback = urlparse(playback_url)
        self.scrubber.register_name_pair(real.netloc, playback.netloc)
    
    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.environ["KEYVAULT_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["KEYVAULT_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["KEYVAULT_CLIENT_SECRET"]

    def _skip_if_not_configured(self, is_hsm):
        if self.is_live and is_hsm and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
