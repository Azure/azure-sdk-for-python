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
from ._async_http_response import AsyncHttpResponse
from ._types import Content

class AioHttpTransportResponse(AsyncHttpResponse):

    @property
    def content(self) -> Content:
        """Return the whole body as bytes in memory.
        """
        if self._content is None:
            raise ValueError("Body is not available. Call async method load_body, or do your call with stream=False.")
        return self._content

    async def load_body(self) -> None:
        """Load in memory the body, so it could be accessible from sync methods."""
        self._content = await self._http_response.internal_response.read()

    @property
    def text(self) -> str:
        """Return the whole body as a string.

        If encoding is not provided, rely on aiohttp auto-detection.

        :param str encoding: The encoding to apply.
        """
        if not self.encoding:
            self.encoding = self._http_response.internal_response.get_encoding()

        return self._content.decode(self.encoding)
