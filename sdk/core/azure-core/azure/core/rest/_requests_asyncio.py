# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import AsyncIterator
import asyncio
from ._helpers_py3 import iter_bytes_helper, iter_raw_helper
from . import AsyncHttpResponse
from ._requests_basic import _RestRequestsTransportResponseBase
from ..pipeline.transport._requests_asyncio import AsyncioStreamDownloadGenerator

class RestAsyncioRequestsTransportResponse(AsyncHttpResponse, _RestRequestsTransportResponseBase): # type: ignore
    """Asynchronous streaming of data from the response.
    """

    async def iter_raw(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """

        async for part in iter_raw_helper(AsyncioStreamDownloadGenerator, self):
            yield part
        await self.close()

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in iter_bytes_helper(AsyncioStreamDownloadGenerator, self):
            yield part
        await self.close()

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self.is_closed = True
        self.internal_response.close()
        await asyncio.sleep(0)
