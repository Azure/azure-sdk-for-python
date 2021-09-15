# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.communication.callingserver.aio._download_async import ContentStreamDownloader
@pytest.mark.asyncio
async def test_content_stream_downloader_setup():
    content_stream_downloader = ContentStreamDownloader(
        clients=None,
        config=None,
        start_range=None,
        end_range=None,
        max_concurrency=1,
        endpoint="https://localhost/documentId"
    )

    response = b"0123456789"

    content_stream_downloader._setup()

    assert content_stream_downloader.properties is not None
    assert content_stream_downloader.properties.size == 10