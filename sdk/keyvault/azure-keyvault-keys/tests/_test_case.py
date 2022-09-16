# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

import pytest
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest, RequestsTransport
from azure.keyvault.keys import KeyReleasePolicy
from azure.keyvault.keys._shared.client_base import DEFAULT_VERSION, ApiVersion
from devtools_testutils import AzureRecordedTestCase


def get_attestation_token(attestation_uri):
    request = HttpRequest("GET", "{}/generate-test-token".format(attestation_uri))
    with Pipeline(transport=RequestsTransport()) as pipeline:
        response = pipeline.run(request)
        return json.loads(response.http_response.text())["token"]


def get_decorator(only_hsm=False, only_vault=False, api_versions=None, **kwargs):
    """returns a test decorator for test parameterization"""
    params = [
        pytest.param(p[0], p[1], id=p[0] + ("_mhsm" if p[1] else "_vault"))
        for p in get_test_parameters(only_hsm, only_vault, api_versions=api_versions)
    ]
    return params


def get_release_policy(attestation_uri, **kwargs):
    release_policy_json = {
        "anyOf": [{"anyOf": [{"claim": "sdk-test", "equals": True}], "authority": attestation_uri.rstrip("/") + "/"}],
        "version": "1.0.0",
    }
    policy_string = json.dumps(release_policy_json).encode()
    return KeyReleasePolicy(policy_string, **kwargs)


def get_test_parameters(only_hsm=False, only_vault=False, api_versions=None):
    """generates a list of parameter pairs for test case parameterization, where [x, y] = [api_version, is_hsm]"""
    combinations = []
    versions = api_versions or ApiVersion
    hsm_supported_versions = {ApiVersion.V7_2, ApiVersion.V7_3}

    for api_version in versions:
        if not only_vault and api_version in hsm_supported_versions:
            combinations.append([api_version, True])
        if not only_hsm:
            combinations.append([api_version, False])
    return combinations


def is_public_cloud():
    return ".microsoftonline.com" in os.getenv("AZURE_AUTHORITY_HOST", "")


class KeysClientPreparer(AzureRecordedTestCase):
    def __init__(self, *args, **kwargs):
        vault_playback_url = "https://vaultname.vault.azure.net"
        hsm_playback_url = "https://managedhsmvaultname.vault.azure.net"
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

        if self.is_live:
            self.vault_url = os.environ["AZURE_KEYVAULT_URL"]
            self.vault_url = self.vault_url.rstrip("/")
            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL", None)
            if self.managed_hsm_url:
                self.managed_hsm_url = self.managed_hsm_url.rstrip("/")
        else:
            self.vault_url = vault_playback_url
            self.managed_hsm_url = hsm_playback_url

        self._set_mgmt_settings_real_values()

    def __call__(self, fn):
        def _preparer(test_class, api_version, is_hsm, **kwargs):

            self._skip_if_not_configured(api_version, is_hsm)
            if not self.is_logging_enabled:
                kwargs.update({"logging_enable": False})
            endpoint_url = self.managed_hsm_url if is_hsm else self.vault_url
            client = self.create_key_client(endpoint_url, api_version=api_version, **kwargs)

            with client:
                fn(test_class, client, is_hsm=is_hsm, managed_hsm_url=self.managed_hsm_url, vault_url=self.vault_url)

        return _preparer

    def create_key_client(self, vault_uri, **kwargs):

        from azure.keyvault.keys import KeyClient

        credential = self.get_credential(KeyClient)

        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def _set_mgmt_settings_real_values(self):
        if self.is_live:
            os.environ["AZURE_TENANT_ID"] = os.environ["KEYVAULT_TENANT_ID"]
            os.environ["AZURE_CLIENT_ID"] = os.environ["KEYVAULT_CLIENT_ID"]
            os.environ["AZURE_CLIENT_SECRET"] = os.environ["KEYVAULT_CLIENT_SECRET"]

    def _skip_if_not_configured(self, api_version, is_hsm):
        if self.is_live and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")
        if self.is_live and is_hsm and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
