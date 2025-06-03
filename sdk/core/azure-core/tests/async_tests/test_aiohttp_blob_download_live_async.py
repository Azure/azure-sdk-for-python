# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
import pytest
import logging
from azure.storage.blob.aio import BlobServiceClient


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="ssl_shutdown_timeout in aiohttp only takes effect on Python 3.11+"
)
@pytest.mark.asyncio
async def test_download_blob_aiohttp(caplog):
    logger = logging.getLogger(__name__)
    AZURE_STORAGE_CONTAINER_NAME = "aiotests"
    account_url = "https://aiotests.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url=account_url)
    read_path = "aiotest.txt"

    with caplog.at_level(logging.INFO):
        async with blob_service_client:
            blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=read_path)

            async with blob_client:
                stream = await blob_client.download_blob()
                data = await stream.readall()
                logger.info(f"Blob size: {len(data)}")

        assert all("Error" not in message for message in caplog.messages)
