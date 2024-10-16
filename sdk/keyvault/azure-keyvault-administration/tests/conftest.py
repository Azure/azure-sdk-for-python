# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from unittest import mock


import pytest
from devtools_testutils import (
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
    add_uri_regex_sanitizer,
    is_live,
    remove_batch_sanitizers,
)

os.environ['PYTHONHASHSEED'] = '0'

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    azure_keyvault_url = os.getenv("AZURE_KEYVAULT_URL", "https://Sanitized.vault.azure.net")
    azure_keyvault_url = azure_keyvault_url.rstrip("/")
    keyvault_tenant_id = os.getenv("KEYVAULT_TENANT_ID", "keyvault_tenant_id")
    keyvault_subscription_id = os.getenv("KEYVAULT_SUBSCRIPTION_ID", "keyvault_subscription_id")
    azure_managedhsm_url = os.environ.get("AZURE_MANAGEDHSM_URL","https://Sanitized.managedhsm.azure.net")
    azure_managedhsm_url = azure_managedhsm_url.rstrip("/")
    azure_attestation_uri = os.environ.get("AZURE_KEYVAULT_ATTESTATION_URL","https://Sanitized.azurewebsites.net")
    azure_attestation_uri = azure_attestation_uri.rstrip('/')
    storage_url = os.environ.get("BLOB_STORAGE_URL", "https://Sanitized.blob.core.windows.net")
    client_id = os.environ.get("KEYVAULT_CLIENT_ID", "service-principal-id")
    sas_token = os.environ.get("BLOB_STORAGE_SAS_TOKEN","fake-sas")

    add_general_string_sanitizer(target=azure_keyvault_url, value="https://Sanitized.vault.azure.net")
    add_general_string_sanitizer(target=keyvault_tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=keyvault_subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_string_sanitizer(target=azure_managedhsm_url,value="https://Sanitized.managedhsm.azure.net")
    add_general_string_sanitizer(target=azure_attestation_uri,value="https://Sanitized.azurewebsites.net")
    add_general_string_sanitizer(target=storage_url, value="https://Sanitized.blob.core.windows.net")
    add_general_string_sanitizer(target=sas_token, value="fake-sas")
    add_general_string_sanitizer(target=client_id, value = "service-principal-id")
    # Sanitize API versions of `azure-keyvault-keys` requests
    add_uri_regex_sanitizer(
        regex="keys/([^/]*)/create\\?api-version=(\\S*)", value="keys/$1/create?api-version=sanitized"
    )
    add_uri_regex_sanitizer(regex="keys/([^/]*)\\?api-version=(\\S*)", value="keys/$1?api-version=sanitized")
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493"])


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
