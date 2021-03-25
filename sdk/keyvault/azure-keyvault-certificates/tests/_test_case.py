# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.certificates import ApiVersion, CertificateClient
from azure.keyvault.certificates._shared import HttpChallengeCache
from parameterized import parameterized
import pytest

from _shared.test_case import KeyVaultTestCase


def suffixed_test_name(testcase_func, param_num, param):
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(param.kwargs.get("api_version")))


class CertificatesTestCase(KeyVaultTestCase):
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(CertificatesTestCase, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(CertificateClient)
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version):
        if self.is_live and api_version != ApiVersion.V7_1:
            pytest.skip("This test only uses the default API version for live tests")
