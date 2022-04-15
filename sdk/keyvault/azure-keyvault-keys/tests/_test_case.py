# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import json
import os

from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest, RequestsTransport
from azure.keyvault.keys import KeyReleasePolicy
from azure.keyvault.keys._shared import HttpChallengeCache
from azure.keyvault.keys._shared.client_base import ApiVersion, DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase
from six.moves.urllib_parse import urlparse
import pytest


# def client_setup(testcase_func):
#     """decorator that creates a client to be passed in to a test method"""

#     @functools.wraps(testcase_func)
#     def wrapper(test_class_instance, api_version, is_hsm=False, **kwargs):
#         test_class_instance._skip_if_not_configured(api_version, is_hsm)
#         endpoint_url = test_class_instance.managed_hsm_url if is_hsm else test_class_instance.vault_url
#         client = test_class_instance.create_key_client(endpoint_url, api_version=api_version, **kwargs)

#         if kwargs.get("is_async"):
#             import asyncio

#             coroutine = testcase_func(test_class_instance, client, is_hsm=is_hsm)
#             loop = asyncio.get_event_loop()
#             loop.run_until_complete(coroutine)
#         else:
#             testcase_func(test_class_instance, client, is_hsm=is_hsm)

#     return wrapper


def get_attestation_token(attestation_uri):
    request = HttpRequest("GET", "{}/generate-test-token".format(attestation_uri))
    with Pipeline(transport=RequestsTransport()) as pipeline:
        response = pipeline.run(request)
        return json.loads(response.http_response.text())["token"]


def get_decorator(only_hsm=False, only_vault=False, api_versions=None, **kwargs):
    """returns a test decorator for test parameterization"""
    # params = [
    #     param(api_version=p[0], is_hsm=p[1], **kwargs)
    #     for p in get_test_parameters(only_hsm, only_vault, api_versions=api_versions)
    # ]
    # return functools.partial(parameterized.expand, params, name_func=suffixed_test_name)

    params = [
        pytest.param(p[0],p[1], id=p[0] + ("_mhsm" if p[1] else "_vault" ))
        for p in get_test_parameters(only_hsm, only_vault, api_versions=api_versions)
    ]
    return params


def get_release_policy(attestation_uri, **kwargs):
    release_policy_json = {
        "anyOf": [
            {
                "anyOf": [
                    {
                        "claim": "sdk-test",
                        "equals": True
                    }
                ],
                "authority": attestation_uri.rstrip("/") + "/"
            }
        ],
        "version": "1.0.0"
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


# def suffixed_test_name(testcase_func, param_num, param):
#     api_version = param.kwargs.get("api_version")
#     suffix = "mhsm" if param.kwargs.get("is_hsm") else "vault"
#     return "{}_{}_{}".format(
#         testcase_func.__name__, parameterized.to_safe_name(api_version), parameterized.to_safe_name(suffix)
#     )


def is_public_cloud():
    return (".microsoftonline.com" in os.getenv('AZURE_AUTHORITY_HOST', ''))

    
class KeysClientPreparer(AzureRecordedTestCase):
    def __init__(self, *args, **kwargs):
        vault_playback_url = "https://vaultname.vault.azure.net"
        hsm_playback_url = "https://managedhsmname.managedhsm.azure.net"

        if self.is_live:
            self.vault_url = os.environ["AZURE_KEYVAULT_URL"]
            # self._scrub_url(real_url=self.vault_url, playback_url=vault_playback_url)

            self.managed_hsm_url = os.environ.get("AZURE_MANAGEDHSM_URL")
            # if self.managed_hsm_url:
            #     self._scrub_url(real_url=self.managed_hsm_url, playback_url=hsm_playback_url)
        else:
            self.vault_url = vault_playback_url
            self.managed_hsm_url = hsm_playback_url

        self._set_mgmt_settings_real_values()

    def __call__(self, fn):
        def _preparer(test_class, api_version, is_hsm, **kwargs):
            if not is_hsm:
                is_hsm = False
            #self._skip_if_not_configured(api_version, is_hsm)
            endpoint_url = self.managed_hsm_url if is_hsm else self.vault_url
            client = self.create_key_client(endpoint_url, api_version=api_version, **kwargs)

            with client:
                fn(test_class, client, is_hsm=is_hsm, managed_hsm_url = self.managed_hsm_url, vault_url = self.vault_url)

            # if kwargs.get("is_async"):
            #     import asyncio

            #     coroutine = testcase_func(test_class_instance, client, is_hsm=is_hsm)
            #     loop = asyncio.get_event_loop()
            #     loop.run_until_complete(coroutine)
            # else:
            

        return _preparer
        


    def create_key_client(self, vault_uri, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.aio import KeyClient

            credential = self.get_credential(KeyClient, is_async=True)
        else:
            from azure.keyvault.keys import KeyClient

            credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs)

    def create_crypto_client(self, key, **kwargs):
        if kwargs.pop("is_async", False):
            from azure.keyvault.keys.crypto.aio import CryptographyClient

            credential = self.get_credential(CryptographyClient, is_async=True)
        else:
            from azure.keyvault.keys.crypto import CryptographyClient

            credential = self.get_credential(CryptographyClient)
        return self.create_client_from_credential(CryptographyClient, credential=credential, key=key, **kwargs)

    def _get_attestation_uri(self):
        playback_uri = "https://fakeattestation.azurewebsites.net"
        if self.is_live:
            real_uri = os.environ.get("AZURE_KEYVAULT_ATTESTATION_URL")
            if real_uri is None:
                pytest.skip("No AZURE_KEYVAULT_ATTESTATION_URL environment variable")
            self._scrub_url(real_uri, playback_uri)
            return real_uri
        return playback_uri

    # def _scrub_url(self, real_url, playback_url):
    #     real = urlparse(real_url)
    #     playback = urlparse(playback_url)
    #     super.scrubber.register_name_pair(real.netloc, playback.netloc)

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
