# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest

from azure.identity import DefaultAzureCredential

from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient
from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from utils import get_resource_name


@pytest.fixture(scope="module")
def account_url():
    account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    if account_name is None:
        raise ValueError(
            f'"STORAGE_ACCOUNT_NAME" environment variable must be set to run Error Code for Copy Blob tests.'
        )
    return f"https://{account_name}.blob.core.windows.net"


@pytest.fixture(scope="module")
def blob_service_client(account_url):
    blob_service_client = BlobServiceClient(
        account_url, credential=DefaultAzureCredential()
    )
    return blob_service_client


@pytest.fixture(scope="module")
def create_container(blob_service_client):
    def _create_container(container_name=None):
        if container_name is None:
            container_name = get_resource_name("utcontainer")
        container_client = blob_service_client.create_container(name=container_name)
        return container_client
    return _create_container


@pytest.fixture(scope="module")
def container_client(create_container):
    container = create_container()
    yield container
    container.delete_container()


@pytest.fixture(scope="function")
def create_append_blob_client(blob_service_client, container_client):
    def _create_append_blob(blob_prefix="blob"):
        append_blob = blob_service_client.get_blob_client(
            container_client.container_name,
            get_resource_name(blob_prefix)
        )
        append_blob.create_append_blob()
        yield append_blob
        append_blob.delete_blob()
    return _create_append_blob


@pytest.fixture(scope="function")
def src_append_blob(create_append_blob_client):
    yield from create_append_blob_client("src_blob")


@pytest.fixture(scope="function")
def dst_append_blob(create_append_blob_client):
    yield from create_append_blob_client("dst_blob")


def test_append_blob_copy_source_error(src_append_blob, dst_append_blob) -> None:
    with pytest.raises(HttpResponseError) as e:
        dst_append_blob.append_block_from_url(src_append_blob.url)

    assert e.value.response.headers["x-ms-copy-source-status-code"] == "409"
    assert e.value.response.headers["x-ms-copy-source-error-code"] == "PublicAccessNotPermitted"
