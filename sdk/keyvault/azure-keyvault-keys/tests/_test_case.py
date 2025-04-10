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
from azure.keyvault.keys._shared.client_base import ApiVersion
from devtools_testutils import AzureRecordedTestCase


HSM_SUPPORTED_VERSIONS = {ApiVersion.V7_2, ApiVersion.V7_3, ApiVersion.V7_4, ApiVersion.V7_5, ApiVersion.V7_6_PREVIEW_2}


def get_attestation_token(attestation_uri):
    request = HttpRequest("GET", f"{attestation_uri}/generate-test-token")
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
    versions = api_versions or pytest.api_version  # pytest.api_version -> [DEFAULT_VERSION] if live, ApiVersion if not

    for api_version in versions:
        if not only_vault and api_version in HSM_SUPPORTED_VERSIONS:
            combinations.append([api_version, True])
        if not only_hsm:
            combinations.append([api_version, False])
    return combinations


def is_public_cloud():
    return ".microsoftonline.com" in os.getenv("AZURE_AUTHORITY_HOST", "https://login.microsoftonline.com/")


class KeysClientPreparer(AzureRecordedTestCase):
    def __init__(self, *args, **kwargs):
        vault_playback_url = "https://vaultname.vault.azure.net"
        hsm_playback_url = "https://managedhsmvaultname.managedhsm.azure.net"
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

        if self.is_live:
            self.vault_url = os.environ["AZURE_KEYVAULT_URL"]
            self.vault_url = self.vault_url.rstrip("/")
            hsm = os.environ.get("AZURE_MANAGEDHSM_URL")
            self.managed_hsm_url = hsm if hsm else None
            if self.managed_hsm_url:
                self.managed_hsm_url = self.managed_hsm_url.rstrip("/")
        else:
            self.vault_url = vault_playback_url
            self.managed_hsm_url = hsm_playback_url

        self._set_mgmt_settings_real_values()

    def __call__(self, fn):
        def _preparer(test_class, api_version, is_hsm, **kwargs):

            self._skip_if_not_configured(is_hsm)
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
            os.environ["AZURE_TENANT_ID"] = os.getenv("KEYVAULT_TENANT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_ID"] = os.getenv("KEYVAULT_CLIENT_ID", "")  # empty in pipelines
            os.environ["AZURE_CLIENT_SECRET"] = os.getenv("KEYVAULT_CLIENT_SECRET", "")  # empty for user-based auth

    def _skip_if_not_configured(self, is_hsm):
        if self.is_live and is_hsm and self.managed_hsm_url is None:
            pytest.skip("No HSM endpoint for live testing")
