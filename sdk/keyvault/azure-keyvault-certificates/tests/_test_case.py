# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.keyvault.certificates._shared import HttpChallengeCache
from azure.keyvault.certificates._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureTestCase
from parameterized import parameterized
import pytest


def suffixed_test_name(testcase_func, param_num, param):
    return "{}_{}".format(testcase_func.__name__, parameterized.to_safe_name(param.kwargs.get("api_version")))


class CertificatesTestCase(AzureTestCase):
    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(CertificatesTestCase, self).tearDown()

    def create_client(self, vault_uri, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.certificates.aio import CertificateClient
            credential = self.get_credential(CertificateClient, is_async=True)
        else:
            from azure.keyvault.certificates import CertificateClient
            credential = self.get_credential(CertificateClient)
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
