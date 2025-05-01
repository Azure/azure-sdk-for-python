# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError
from devtools_testutils import recorded_by_proxy


def test_append_block_copy_source_error(append_blob_client) -> None:
    src_append_blob = append_blob_client
    dst_append_blob = append_blob_client

    with pytest.raises(HttpResponseError) as e:
        dst_append_blob.append_block_from_url(src_append_blob.url)

    assert e.value.response.headers["x-ms-copy-source-status-code"] == "401"
    assert e.value.response.headers["x-ms-copy-source-error-code"] == "NoAuthenticationInformation"


def test_upload_blob_copy_source_error(block_blob_client):
    src_block_blob = block_blob_client
    dst_block_blob = block_blob_client

    with pytest.raises(HttpResponseError) as e:
        dst_block_blob.upload_blob_from_url(src_block_blob.url)

    assert e.value.response.headers["x-ms-copy-source-status-code"] == "401"
    assert e.value.response.headers["x-ms-copy-source-error-code"] == "NoAuthenticationInformation"


def test_stage_block_copy_source_error(block_blob_client):
    src_block_blob = block_blob_client
    dst_block_blob = block_blob_client

    with pytest.raises(HttpResponseError) as e:
        dst_block_blob.stage_block_from_url(
            block_id=1,
            source_url=src_block_blob.url,
            source_offset=0,
            source_length=4*1024
        )

    assert e.value.response.headers["x-ms-copy-source-status-code"] == "401"
    assert e.value.response.headers["x-ms-copy-source-error-code"] == "NoAuthenticationInformation"


def test_upload_pages_copy_source_error(page_blob_client):
    src_page_blob = page_blob_client
    dst_page_blob = page_blob_client

    with pytest.raises(HttpResponseError) as e:
        dst_page_blob.upload_pages_from_url(src_page_blob.url, 0, 0, 0)

    assert e.value.response.headers["x-ms-copy-source-status-code"] == "401"
    assert e.value.response.headers["x-ms-copy-source-error-code"] == "NoAuthenticationInformation"
