# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import os
from unittest import mock


import pytest
from devtools_testutils import (add_general_regex_sanitizer,
                                add_oauth_response_sanitizer, is_live,
                                test_proxy)

os.environ['PYTHONHASHSEED'] = '0'

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    azure_keyvault_url = os.getenv("azure_keyvault_url", "https://vaultname.vault.azure.net")
    azure_keyvault_url = azure_keyvault_url.rstrip("/")
    keyvault_tenant_id = os.getenv("keyvault_tenant_id", "keyvault_tenant_id")
    keyvault_subscription_id = os.getenv("keyvault_subscription_id", "keyvault_subscription_id")
    azure_managedhsm_url = os.environ.get("azure_managedhsm_url","https://managedhsmvaultname.vault.azure.net")
    azure_managedhsm_url = azure_managedhsm_url.rstrip("/")
    azure_attestation_uri = os.environ.get("azure_keyvault_attestation_url","https://fakeattestation.azurewebsites.net")
    azure_attestation_uri = azure_attestation_uri.rstrip('/')
    storage_name = os.environ.get("BLOB_STORAGE_ACCOUNT_NAME", "blob_storage_account_name")
    storage_endpoint_suffix = os.environ.get("KEYVAULT_STORAGE_ENDPOINT_SUFFIX", "keyvault_endpoint_suffix")
    client_id = os.environ.get("KEYVAULT_CLIENT_ID", "service-principal-id")
    sas_token = os.environ.get("BLOB_STORAGE_SAS_TOKEN","fake-sas")

    add_general_regex_sanitizer(regex=azure_keyvault_url, value="https://vaultname.vault.azure.net")
    add_general_regex_sanitizer(regex=keyvault_tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=keyvault_subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=azure_managedhsm_url,value="https://managedhsmvaultname.vault.azure.net")
    add_general_regex_sanitizer(regex=azure_attestation_uri,value="https://fakeattestation.azurewebsites.net")
    add_general_regex_sanitizer(regex=storage_name, value = "blob_storage_account_name")
    add_general_regex_sanitizer(regex=storage_endpoint_suffix, value = "keyvault_endpoint_suffix")
    add_general_regex_sanitizer(regex=sas_token, value="fake-sas")
    add_general_regex_sanitizer(regex=client_id, value = "service-principal-id")
    add_oauth_response_sanitizer()


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