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
import collections
from inspect import isasyncgen
from typing import AsyncIterable, AsyncIterator, Dict, Iterable, Tuple, Union

from six import Iterator
from ._helpers import (
    ByteStream,
    RequestHelper,
    SyncByteStream,
    StreamConsumedError
)

########################### STREAM SECTION #################################
class AsyncByteStream:
    def __init__(self, stream):
        self._data = stream  # naming it data bc this is what requests / aiohttp are interested in

    async def __aiter__(self) -> AsyncIterator[bytes]:
        raise NotImplementedError("Implement __aiter__")

    async def aclose(self) -> None:
        """Close the stream"""

    async def aread(self) -> bytes:
        try:
            parts = []
            async for part in self:
                parts.append(part)
            return b"".join(parts)
        finally:
            await self.aclose()

class AsyncIteratorByteStream(AsyncByteStream):
    def __init__(self, stream: AsyncIterable[bytes]):
        super().__init__(stream)
        self._stream = stream
        self._is_stream_consumed = False
        self._is_generator = isasyncgen(stream)

    async def __aiter__(self) -> AsyncIterator[bytes]:
        if self._is_stream_consumed and self._is_generator:
            raise StreamConsumedError()

        self._is_stream_consumed = True
        async for part in self._stream:
            yield part

class ByteStreamPy3(ByteStream, AsyncByteStream):

    async def __aiter__(self) -> AsyncIterator[bytes]:
        # NOTE: idt this will pass py3.5
        yield self._stream


ContentType = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]

class RequestHelperPy3(RequestHelper):

    @property
    def byte_stream(self):
        return ByteStreamPy3

    def set_content_body(self, content: ContentType) -> Tuple[
        Dict[str, str], Union[SyncByteStream, AsyncByteStream]
    ]:
        headers, body = self._shared_set_content_body(content)
        if body:
            return headers, body
        if isinstance(content, collections.AsyncIterable):
            return {"Transfer-Encoding": "chunked"}, AsyncIteratorByteStream(content)
        raise TypeError(
            "Unexpected type for 'content': '{}'. ".format(type(content)) +
            "We expect 'content' to either be str, bytes, or an Iterable / AsyncIterable"
        )
