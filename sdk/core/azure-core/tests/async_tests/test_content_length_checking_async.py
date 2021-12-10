# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import (
    HttpRequest,
)
from azure.core import AsyncPipelineClient
from azure.core.exceptions import IncompleteReadError
import pytest


@pytest.mark.asyncio
async def test_aio_transport_short_read_download_stream(port):
    url = "http://localhost:{}/errors/short-data".format(port)
    client = AsyncPipelineClient(url)
    with pytest.raises(IncompleteReadError):
        async with client:
            request = HttpRequest("GET", url)
            pipeline_response = await client._pipeline.run(request, stream=True)
            response = pipeline_response.http_response
            data = response.stream_download(client._pipeline)
            content = b""
            async for d in data:
                content += d
