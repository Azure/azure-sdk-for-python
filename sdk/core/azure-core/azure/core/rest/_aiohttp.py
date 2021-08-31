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

import asyncio
from multidict import CIMultiDict
from ._http_response_impl_async import AsyncHttpResponseImpl
from ..pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

class RestAioHttpTransportResponse(AsyncHttpResponseImpl):
    def __init__(
        self,
        *,
        internal_response,
        decompress: bool = False,
        **kwargs
    ):
        super().__init__(
            internal_response=internal_response,
            status_code=internal_response.status,
            headers=CIMultiDict(internal_response.headers),
            content_type=internal_response.headers.get('content-type'),
            reason=internal_response.reason,
            stream_download_generator=AioHttpStreamDownloadGenerator,
            content=None,
            **kwargs
        )
        self._decompress = decompress

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state['_internal_response'] = None  # aiohttp response are not pickable (see headers comments)
        state['headers'] = CIMultiDict(self.headers)  # MultiDictProxy is not pickable
        return state

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        if not self.is_closed:
            self._is_closed = True
            self._internal_response.close()
            await asyncio.sleep(0)
