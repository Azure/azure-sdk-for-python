# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.rest import HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.exceptions import IncompleteReadError

from utils import ASYNC_TRANSPORTS


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_aio_transport_short_read_download_stream(port, transport):
    url = "http://localhost:{}/errors/short-data".format(port)
    client = AsyncPipelineClient(url, transport=transport())
    with pytest.raises(IncompleteReadError):
        async with client:
            request = HttpRequest("GET", url)
            pipeline_response = await client.pipeline.run(request, stream=True)
            response = pipeline_response.http_response
            data = response.iter_bytes()
            content = b""
            async for d in data:
                content += d
