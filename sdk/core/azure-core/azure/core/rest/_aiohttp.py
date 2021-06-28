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
import codecs
from typing import AsyncIterator
from multidict import CIMultiDict
import aiohttp
from . import HttpRequest, AsyncHttpResponse
try:
    import cchardet as chardet
except ImportError:  # pragma: no cover
    import chardet  # type: ignore
from ._helpers_py3 import iter_raw_helper, iter_bytes_helper
from ..pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator


class RestAioHttpTransportResponse(AsyncHttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        internal_response,
    ):
        super().__init__(request=request, internal_response=internal_response)
        self.status_code = internal_response.status
        self.headers = CIMultiDict(internal_response.headers)  # type: ignore
        self.reason = internal_response.reason
        self.content_type = internal_response.headers.get('content-type')
        self._decompress = None
        self._decompressed_content = None

    def _get_content(self):
        if not self._decompress:
            return self._content
        enc = self.headers.get('Content-Encoding')
        if not enc:
            return self._content
        enc = enc.lower()
        if enc in ("gzip", "deflate"):
            if self._decompressed_content:
                return self._decompressed_content
            import zlib
            zlib_mode = 16 + zlib.MAX_WBITS if enc == "gzip" else zlib.MAX_WBITS
            decompressor = zlib.decompressobj(wbits=zlib_mode)
            self._decompressed_content = decompressor.decompress(self._content)
            return self._decompressed_content
        return self._content

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

    async def iter_raw(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process
        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in iter_raw_helper(AioHttpStreamDownloadGenerator, self):
            yield part
        await self.close()

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process
        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in iter_bytes_helper(AioHttpStreamDownloadGenerator, self):
            yield part
        await self.close()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state['internal_response'] = None  # aiohttp response are not pickable (see headers comments)
        state['headers'] = CIMultiDict(self.headers)  # MultiDictProxy is not pickable
        return state

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self.is_closed = True
        self.internal_response.close()
        await asyncio.sleep(0)
