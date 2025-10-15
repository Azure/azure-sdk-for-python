# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import pytest_asyncio

from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.remoterendering import RemoteRenderingClient
from azure.mixedreality.remoterendering.aio import RemoteRenderingClient as RemoteRenderingClientAsync
from devtools_testutils.sanitizers import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_remove_header_sanitizer,
    is_live,
    remove_batch_sanitizers,
)

# Environment variable keys
ENV_ARR_SERVICE_ENDPOINT = "REMOTERENDERING_ARR_SERVICE_ENDPOINT"
ENV_ARR_ACCOUNT_DOMAIN = "REMOTERENDERING_ARR_ACCOUNT_DOMAIN"
ENV_ARR_ACCOUNT_ID = "REMOTERENDERING_ARR_ACCOUNT_ID"
ENV_ARR_ACCOUNT_KEY = "REMOTERENDERING_ARR_ACCOUNT_KEY"
ENV_ARR_STORAGE_ACCOUNT_NAME = "REMOTERENDERING_ARR_STORAGE_ACCOUNT_NAME"
ENV_ARR_SAS_TOKEN = "REMOTERENDERING_ARR_SAS_TOKEN"
ENV_ARR_BLOB_CONTAINER_NAME = "REMOTERENDERING_ARR_BLOB_CONTAINER_NAME"
ENV_STORAGE_ENDPOINT_SUFFIX = "REMOTERENDERING_STORAGE_ENDPOINT_SUFFIX"

# Fake values
TEST_ARR_SERVICE_ENDPOINT = "https://remoterendering.eastus.mixedreality.azure.com"
TEST_ARR_ACCOUNT_DOMAIN = "eastus.mixedreality.azure.com"
TEST_ARR_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"
TEST_ARR_ACCOUNT_KEY = "fakekey"
TEST_ARR_STORAGE_ACCOUNT_NAME = "arrstorageaccount"
TEST_ARR_SAS_TOKEN = "sv=2015-04-05&sr=c&se=2122-03-10T16%3A13%3A40.0000000Z&sp=rwl&sig=fakeSig"
TEST_ARR_BLOB_CONTAINER_NAME = "test"
TEST_STORAGE_ENDPOINT_SUFFIX = "storage_endpoint_suffix"
TEST_ID_PLACEHOLDER = "rr-test-id"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_ARR_SERVICE_ENDPOINT: TEST_ARR_SERVICE_ENDPOINT,
        ENV_ARR_ACCOUNT_DOMAIN: TEST_ARR_ACCOUNT_DOMAIN,
        ENV_ARR_ACCOUNT_ID: TEST_ARR_ACCOUNT_ID,
        ENV_ARR_ACCOUNT_KEY: TEST_ARR_ACCOUNT_KEY,
        ENV_ARR_STORAGE_ACCOUNT_NAME: TEST_ARR_STORAGE_ACCOUNT_NAME,
        ENV_ARR_SAS_TOKEN: TEST_ARR_SAS_TOKEN,
        ENV_ARR_BLOB_CONTAINER_NAME: TEST_ARR_BLOB_CONTAINER_NAME,
        ENV_STORAGE_ENDPOINT_SUFFIX: TEST_STORAGE_ENDPOINT_SUFFIX
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_remove_header_sanitizer(headers="X-MRC-CV")
    add_body_key_sanitizer(json_path="AccessToken", value="fake.eyJleHAiOjIxNDc0ODM2NDd9.fake")
    add_general_regex_sanitizer(
        regex=f"{TEST_ID_PLACEHOLDER}[a-z0-9-]+",
        value=TEST_ID_PLACEHOLDER
    )

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3430"])


@pytest.fixture(scope="session")
def account_info(environment_variables):
    yield {
        "service_endpoint": environment_variables.get(ENV_ARR_SERVICE_ENDPOINT),
        "account_domain": environment_variables.get(ENV_ARR_ACCOUNT_DOMAIN),
        "account_id": environment_variables.get(ENV_ARR_ACCOUNT_ID),
        "account_key": environment_variables.get(ENV_ARR_ACCOUNT_KEY),
        "storage_account_name": environment_variables.get(ENV_ARR_STORAGE_ACCOUNT_NAME),
        "sas_token": environment_variables.get(ENV_ARR_SAS_TOKEN),
        "blob_container_name": environment_variables.get(ENV_ARR_BLOB_CONTAINER_NAME),
        "storage_endpoint_suffix": environment_variables.get(ENV_STORAGE_ENDPOINT_SUFFIX),
        "key_credential": AzureKeyCredential(environment_variables.get(ENV_ARR_ACCOUNT_KEY)),
        "id_placeholder": TEST_ID_PLACEHOLDER
    }


@pytest.fixture
def arr_client(account_info):
    # Give a small interval for playback tests to avoid
    # a race condition where a poller consumes more recorded requests
    # than expected.
    polling_interval = 10 if is_live() else 0.2
    client = RemoteRenderingClient(
        endpoint=account_info["service_endpoint"],
        account_id=account_info["account_id"],
        account_domain=account_info["account_domain"],
        credential=account_info["key_credential"],
        polling_interval=polling_interval
    )
    yield client
    client.close()


@pytest_asyncio.fixture
async def async_arr_client(account_info):
    polling_interval = 10 if is_live() else 0
    client = RemoteRenderingClientAsync(
        endpoint=account_info["service_endpoint"],
        account_id=account_info["account_id"],
        account_domain=account_info["account_domain"],
        credential=account_info["key_credential"],
        polling_interval=polling_interval
    )
    yield client
    await client.close()
