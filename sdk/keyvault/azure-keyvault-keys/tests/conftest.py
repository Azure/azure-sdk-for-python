# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import os
from unittest import mock

import pytest
from devtools_testutils import (
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
    is_live,
    remove_batch_sanitizers
)
from azure.keyvault.keys._shared.client_base import DEFAULT_VERSION, ApiVersion

os.environ['PYTHONHASHSEED'] = '0'
ALL_API_VERSIONS = "--all-api-versions"

def pytest_addoption(parser):
    parser.addoption(ALL_API_VERSIONS, action="store_true", default=False,
                     help="Test all api version in live mode. Not applicable in playback mode.")

def pytest_configure(config):
    if is_live() and not config.getoption(ALL_API_VERSIONS):
        pytest.api_version = [DEFAULT_VERSION]
    else:
        pytest.api_version = ApiVersion

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    azure_keyvault_url = os.getenv("AZURE_KEYVAULT_URL", "https://vaultname.vault.azure.net")
    azure_keyvault_url = azure_keyvault_url.rstrip("/")
    keyvault_tenant_id = os.getenv("KEYVAULT_TENANT_ID", "keyvault_tenant_id")
    keyvault_subscription_id = os.getenv("KEYVAULT_SUBSCRIPTION_ID", "keyvault_subscription_id")
    azure_managedhsm_url = os.environ.get("AZURE_MANAGEDHSM_URL","https://managedhsmvaultname.managedhsm.azure.net")
    azure_managedhsm_url = azure_managedhsm_url.rstrip("/")
    azure_attestation_uri = os.environ.get("AZURE_KEYVAULT_ATTESTATION_URL","https://fakeattestation.azurewebsites.net")
    azure_attestation_uri = azure_attestation_uri.rstrip('/')

    add_general_string_sanitizer(target=azure_keyvault_url, value="https://vaultname.vault.azure.net")
    add_general_string_sanitizer(target=keyvault_tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=keyvault_subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=azure_managedhsm_url, value="https://managedhsmvaultname.managedhsm.azure.net")
    add_general_string_sanitizer(target=azure_attestation_uri, value="https://fakeattestation.azurewebsites.net")
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3447: $.key
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3447",])


@pytest.fixture(scope="session", autouse=True)
def patch_async_sleep():
    async def immediate_return(_):
        return

    if not is_live():
        with mock.patch("asyncio.sleep", immediate_return):
            yield

    else:
        yield


@pytest.fixture(scope="session", autouse=True)
def patch_sleep():
    def immediate_return(_):
        return

    if not is_live():
        with mock.patch("time.sleep", immediate_return):
            yield

    else:
        yield

@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
