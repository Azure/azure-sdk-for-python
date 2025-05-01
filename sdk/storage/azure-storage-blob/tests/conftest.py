# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest

from azure.storage.blob import BlobServiceClient
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    add_uri_regex_sanitizer,
    test_proxy
)
from utils import get_resource_name


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("STORAGE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_oauth_response_sanitizer()

    add_header_regex_sanitizer(key="x-ms-copy-source-authorization", value="Sanitized")
    add_header_regex_sanitizer(key="x-ms-encryption-key", value="Sanitized")
    add_general_regex_sanitizer(regex=r'"EncryptionLibrary": "Python .*?"', value='"EncryptionLibrary": "Python x.x.x"')

    add_uri_regex_sanitizer(regex=r"\.preprod\.", value=".")


# --------------------------------
#      Sync Blob Fixtures
# --------------------------------
@pytest.fixture(scope="package")
def account_name():
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    if storage_account_name is None:
        raise ValueError(
            f'"STORAGE_ACCOUNT_NAME" environment variable must be set to run tests.'
        )
    return storage_account_name


@pytest.fixture(scope="package")
def account_key():
    storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
    if storage_account_key is None:
        raise ValueError(
            f'"STORAGE_ACCOUNT_KEY" environment variable must be set to run tests.'
        )
    return storage_account_key


@pytest.fixture(scope="package")
def account_url(account_name):
    return f"https://{account_name}.blob.preprod.core.windows.net"


@pytest.fixture(scope="package")
def blob_service_client(account_url, account_key):
    return BlobServiceClient(account_url, credential=account_key)


@pytest.fixture(scope="package")
def create_container(blob_service_client):
    def _create_container(container_name=None):
        if container_name is None:
            container_name = get_resource_name("utcontainer")
        container_client = blob_service_client.create_container(name=container_name)
        return container_client
    return _create_container


@pytest.fixture(scope="package")
def container_client(create_container):
    container = create_container()
    yield container
    container.delete_container()


@pytest.fixture(scope="function")
def blob_client(blob_service_client, container_client):
    bc = blob_service_client.get_blob_client(
        container_client.container_name,
        get_resource_name("blob")
    )
    yield bc
    bc.delete_blob()


@pytest.fixture(scope="function")
def append_blob_client(blob_client):
    blob_client.create_append_blob()
    return blob_client


@pytest.fixture(scope="function")
def page_blob_client(blob_client):
    blob_client.create_page_blob(size=512)
    return blob_client


@pytest.fixture(scope="function")
def block_blob_client(blob_client):
    blob_client.upload_blob(data=b"", overwrite=True)
    return blob_client
