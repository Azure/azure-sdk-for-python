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

from typing import cast, Iterator, Optional, AsyncIterator

from ..exceptions import ResponseNotReadError, StreamConsumedError, StreamClosedError
from ._rest import _HttpResponseBase, HttpResponse
from . import AsyncHttpResponse, HttpRequest
from ..pipeline.transport.httpx import HttpxStreamDownloadGenerator, AsyncHttpxStreamDownloadGenerator

def _has_content(response):
    try:
        response.content  # pylint: disable=pointless-statement
        return True
    except ResponseNotReadError:
        return False

def _stream_download_helper(decompress, response):
    if response.is_stream_consumed:
        raise StreamConsumedError(response)
    if response.is_closed:
        raise StreamClosedError(response)

    response.is_stream_consumed = True
    stream_download = HttpxStreamDownloadGenerator(
        pipeline=None,
        response=response,
        decompress=decompress,
    )
    for part in stream_download:
        yield part

def _stream_download_async_helper(decompress, response):
    if response.is_stream_consumed:
        raise StreamConsumedError(response)
    if response.is_closed:
        raise StreamClosedError(response)

    response.is_stream_consumed = True
    return AsyncHttpxStreamDownloadGenerator(
        pipeline=None,
        response=response,
        decompress=decompress,
    )

class RestHttpXTransportResponse(HttpResponse):
    def __init__(self, **kwargs):
        super(RestHttpXTransportResponse, self).__init__(**kwargs)
        self.status_code = self._internal_response.status_code
        self.headers = self._internal_response.headers
        self.reason = self._internal_response.reason_phrase
        self.content_type = self._internal_response.headers.get('content-type')
        self.stream_contextmanager = self._pipeline_response.stream_contextmanager

    @property
    def content(self):
        # type: () -> bytes
        try:
            return self._internal_response.content
        except RuntimeError:
            # requests throws a RuntimeError if the content for a response is already consumed
            raise ResponseNotReadError(self)

    @property
    def encoding(self) -> Optional[str]:
        retval = super(HttpResponse, self).encoding
        if not retval:
            # There is a few situation where "requests" magic doesn't fit us:
            # - https://github.com/psf/requests/issues/654
            # - https://github.com/psf/requests/issues/1737
            # - https://github.com/psf/requests/issues/2086
            from codecs import BOM_UTF8
            if _has_content(self) and self._internal_response.content[:3] == BOM_UTF8:
                retval = "utf-8-sig"
        if retval:
            if retval == "utf-8":
                retval = "utf-8-sig"
        return retval

    @encoding.setter  # type: ignore
    def encoding(self, value: str) -> None:
        # ignoring setter bc of known mypy issue https://github.com/python/mypy/issues/1465
        self._encoding = value
        self._internal_response.encoding = value

    @property
    def text(self):
        # this will trigger errors if response is not read in
        self.content  # pylint: disable=pointless-statement
        return self._internal_response.text

    def iter_bytes(self) -> Iterator[bytes]:
        """Iterates over the response's bytes. Will decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        if _has_content(self):
            chunk_size = cast(int, self._connection_data_block_size)
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i: i + chunk_size]
        else:
            for part in _stream_download_helper(
                    decompress=True,
                    response=self,
            ):
                yield part
        self.close()

    def iter_raw(self) -> Iterator[bytes]:
        """Iterates over the response's bytes. Will not decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        for part in _stream_download_helper(
                decompress=False,
                response=self,
        ):
            yield part
        self.close()

    def read(self) -> bytes:
        """Read the response's bytes.

        :return: The read in bytes
        :rtype: bytes
        """
        if not _has_content(self):
            self._internal_response._content = b"".join(self.iter_bytes())  # pylint: disable=protected-access
        return self.content

class RestAsyncHttpXTransportResponse(AsyncHttpResponse):
    def __init__(self, **kwargs):
        super(RestAsyncHttpXTransportResponse, self).__init__(**kwargs)
        self.status_code = self._internal_response.status_code
        self.headers = self._internal_response.headers
        self.reason = self._internal_response.reason_phrase
        self.content_type = self._internal_response.headers.get('content-type')
        self.stream_contextmanager = self._pipeline_response.stream_contextmanager

    @property
    def content(self):
        # type: () -> bytes
        try:
            return self._internal_response.content
        except RuntimeError:
            # requests throws a RuntimeError if the content for a response is already consumed
            raise ResponseNotReadError(self)

    @property
    def text(self):
        # this will trigger errors if response is not read in
        self.content  # pylint: disable=pointless-statement
        return self._internal_response.text

    async def iter_raw(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in _stream_download_async_helper(
                decompress=False,
                response=self
        ):
            yield part
        await self.close()

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        if _has_content(self):
            chunk_size = cast(int, self._connection_data_block_size)
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i: i + chunk_size]
        else:
            async for part in _stream_download_async_helper(
                    decompress=True,
                    response=self,
            ):
                yield part
        await self.close()

    async def read(self) -> bytes:
        """Read the response's bytes.

        :return: The read in bytes
        :rtype: bytes
        """
        if not _has_content(self):
            parts = []
            async for part in self.iter_bytes():  # type: ignore
                parts.append(part)
            self._internal_response._content = b"".join(parts)  # pylint: disable=protected-access
        return self.content

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self.is_closed = True
        await self._internal_response.aclose()

    async def __aexit__(self, *args) -> None:
        await self.close()
