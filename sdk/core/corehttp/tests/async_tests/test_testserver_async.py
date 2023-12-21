# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.rest import HttpRequest
from corehttp.transport.aiohttp import AioHttpTransport

"""This file does a simple call to the testserver to make sure we can use the testserver"""


@pytest.mark.asyncio
async def test_smoke(port):
    request = HttpRequest(method="GET", url="http://localhost:{}/basic/string".format(port))
    async with AioHttpTransport() as sender:
        response = await sender.send(request)
        response.raise_for_status()
        await response.read()
        assert response.text() == "Hello, world!"
