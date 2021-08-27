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
from ._rest_py3 import AsyncHttpResponse as _AsyncHttpResponse
from ._http_response_impl import _HttpResponseBaseImpl
from ._helpers import parse_lines_from_text

class AsyncHttpResponseImpl(_HttpResponseBaseImpl, _AsyncHttpResponse):
    """AsyncHttpResponseImpl built on top of our HttpResponse protocol class.

    Helper impl for creating our transport responses
    """

    async def read(self) -> bytes:
        """Read the response's bytes into memory.

        :return: The response's bytes
        :rtype: bytes
        """
        if self._content is None:
            parts = []
            async for part in self.iter_bytes():
                parts.append(part)
            self._content = b"".join(parts)
        self._is_stream_consumed = True
        return self._content

    async def iter_text(self) -> AsyncIterator[str]:
        """Asynchronously iterates over the text in the response.

        :return: An async iterator of string. Each string chunk will be a text from the response
        :rtype: AsyncIterator[str]
        """
        async for byte in self.iter_bytes():  # type: ignore
            text = byte.decode(self.encoding or "utf-8")
            yield text

    async def iter_lines(self) -> AsyncIterator[str]:
        """Asynchronously iterates over the lines in the response.

        :return: An async iterator of string. Each string chunk will be a line from the response
        :rtype: AsyncIterator[str]
        """
        async for text in self.iter_text():
            lines = parse_lines_from_text(text)
            for line in lines:
                yield line

    async def iter_raw(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        raise NotImplementedError()
        # getting around mypy behavior, see https://github.com/python/mypy/issues/10732
        yield  # pylint: disable=unreachable

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        raise NotImplementedError()
        # getting around mypy behavior, see https://github.com/python/mypy/issues/10732
        yield  # pylint: disable=unreachable

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self._is_closed = True
        await self._internal_response.close()

    async def __aexit__(self, *args) -> None:
        await self.close()

    def __repr__(self) -> str:
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<AsyncHttpResponse: {} {}{}>".format(
            self.status_code, self.reason, content_type_str
        )
