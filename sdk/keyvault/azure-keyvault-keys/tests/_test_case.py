# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient
from azure.keyvault.keys._shared import HttpChallengeCache
from parameterized import parameterized
import pytest
from six.moves.urllib_parse import urlparse

from _shared.test_case import KeyVaultTestCase


def suffixed_test_name(testcase_func, param_num, param):
    suffix = "mhsm" if param.kwargs.get("is_hsm") else "vault"
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(suffix))


class KeysTestCase(KeyVaultTestCase):
    def setUp(self, *args, **kwargs):
        playback_url = "https://managedhsmname.managedhsm.azure.net"
        if self.is_live:
            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            if self.managed_hsm_url:
                real = urlparse(self.managed_hsm_url)
                playback = urlparse(playback_url)
                self.scrubber.register_name_pair(real.netloc, playback.netloc)
        else:
            self.managed_hsm_url = playback_url
        super(KeysTestCase, self).setUp(*args, **kwargs)
    
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeysTestCase, self).tearDown()

    def create_key_client(self, vault_uri, **kwargs):
        credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)
    
    def create_crypto_client(self, key, **kwargs):
        credential = self.get_credential(CryptographyClient)
        return self.create_client_from_credential(CryptographyClient, credential=credential, key=key, **kwargs)

    def _skip_if_not_configured(self, is_hsm):
        if self.is_live and is_hsm and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
