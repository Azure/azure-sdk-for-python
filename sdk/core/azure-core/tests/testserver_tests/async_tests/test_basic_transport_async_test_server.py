# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
import time

from azure.core.pipeline.transport import HttpRequest, AioHttpTransport
from azure.core.pipeline import AsyncPipeline

import pytest

@pytest.mark.asyncio
async def test_basic_options_aiohttp(port):

    request = HttpRequest("OPTIONS", "http://localhost:{}/basic/string".format(port))
    async with AsyncPipeline(AioHttpTransport(), policies=[]) as pipeline:
        response = await pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)
