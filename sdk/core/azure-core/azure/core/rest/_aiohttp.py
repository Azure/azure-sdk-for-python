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
import codecs
from typing import AsyncIterator

import chardet
import aiohttp
from multidict import CIMultiDict

from ._rest_py3 import AsyncHttpResponse, HttpRequest
from ._helpers import StreamConsumedError, ResponseClosedError
from ..pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator


class AioHttpTransportResponse(AsyncHttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        internal_response,
        **kwargs
    ):
        super().__init__(request=request, internal_response=internal_response, **kwargs)
        self.status_code = internal_response.status
        self.headers = CIMultiDict(internal_response.headers)
        self.reason = internal_response.reason
        self.content_type = internal_response.headers.get('content-type')

    @property
    def text(self) -> str:
        content = self.content
        encoding = self.encoding
        ctype = self.headers.get(aiohttp.hdrs.CONTENT_TYPE, "").lower()
        mimetype = aiohttp.helpers.parse_mimetype(ctype)

        encoding = mimetype.parameters.get("charset")
        if encoding:
            try:
                codecs.lookup(encoding)
            except LookupError:
                encoding = None
        if not encoding:
            if mimetype.type == "application" and (
                    mimetype.subtype == "json" or mimetype.subtype == "rdap"
            ):
                # RFC 7159 states that the default encoding is UTF-8.
                # RFC 7483 defines application/rdap+json
                encoding = "utf-8"
            elif content is None:
                raise RuntimeError(
                    "Cannot guess the encoding of a not yet read content"
                )
            else:
                encoding = chardet.detect(content)["encoding"]
        if not encoding:
            encoding = "utf-8-sig"

        return content.decode(encoding)

    async def _stream_download_helper(self, decompress, chunk_size=None):
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise ResponseClosedError()

        self.is_stream_consumed = True
        stream_download = AioHttpStreamDownloadGenerator(
            pipeline=None,
            response=self,
            chunk_size=chunk_size,
            decompress=decompress,
        )
        async for part in stream_download:
            self._num_bytes_downloaded += len(part)
            yield part

    async def iter_raw(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the raw response bytes
        """
        async for raw_bytes in self._stream_download_helper(decompress=False, chunk_size=chunk_size):
            yield raw_bytes
        self.close()

    async def iter_bytes(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the bytes in the response stream
        """
        if self._read_content:
            if chunk_size is None:
                chunk_size = len(self._content)
            async for i in range(0, len(self._content), chunk_size):
                yield self._content[i: i + chunk_size]
        else:
            if self.is_stream_consumed:
                raise StreamConsumedError()
            if self.is_closed:
                raise ResponseClosedError()

            self.is_stream_consumed = True
            stream_download = AioHttpStreamDownloadGenerator(
                pipeline=None,
                response=self,
                chunk_size=chunk_size,
                decompress=True,
            )
            async for part in stream_download:
                self._num_bytes_downloaded += len(part)
                yield part
        await self.close()
