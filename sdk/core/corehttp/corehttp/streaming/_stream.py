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

from types import TracebackType
from typing import Any, Iterator, AsyncIterator, TypeVar, Callable, Optional, Type

from typing_extensions import Self

from ..rest import HttpResponse, AsyncHttpResponse
from ._decoders import StreamDecoder, AsyncStreamDecoder
from ._jsonl import JSONLDecoder, AsyncJSONLDecoder
from ._sse import SSEDecoder, AsyncSSEDecoder

DecodedType = TypeVar("DecodedType")
ReturnType_co = TypeVar("ReturnType_co", covariant=True)


class Stream(Iterator[ReturnType_co]):
    """Stream class for consuming a decoded event stream (e.g. JSONL or SSE).

    :keyword response: The response object.
    :paramtype response: ~corehttp.rest.HttpResponse
    :keyword decoder: A decoder to use for the stream. If omitted, the decoder is
        inferred from the response ``Content-Type`` header.
    :paramtype decoder: ~corehttp.streaming.StreamDecoder
    :keyword deserialization_callback: A callback that takes the response and the decoded event and
        returns a deserialized object.
    :paramtype deserialization_callback: Callable[[~corehttp.rest.HttpResponse, Any], ReturnType]
    """

    def __init__(
        self,
        *,
        response: HttpResponse,
        deserialization_callback: Callable[[HttpResponse, DecodedType], ReturnType_co],
        decoder: Optional[StreamDecoder[DecodedType]] = None,
    ) -> None:
        self._response = response
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        self._decoder: StreamDecoder[Any] = (
            decoder
            if decoder is not None
            else (SSEDecoder() if content_type == "text/event-stream" else JSONLDecoder())
        )
        self._deserialization_callback = deserialization_callback
        self._iterator = self._iter_results()

    def __next__(self) -> ReturnType_co:
        return self._iterator.__next__()

    def __iter__(self) -> Self:
        return self

    def _iter_results(self) -> Iterator[ReturnType_co]:
        for event in self._decoder.iter_events(self._response.iter_bytes()):

            result = self._deserialization_callback(self._response, event)
            yield result

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        self.close()

    def __enter__(self) -> Self:
        return self

    def close(self) -> None:
        self._response.close()


class AsyncStream(AsyncIterator[ReturnType_co]):
    """AsyncStream class for asynchronously consuming a decoded event stream (e.g. JSONL or SSE).

    :keyword response: The response object.
    :paramtype response: ~corehttp.rest.AsyncHttpResponse
    :keyword decoder: A decoder to use for the stream. If omitted, the decoder is
        inferred from the response ``Content-Type`` header.
    :paramtype decoder: ~corehttp.streaming.AsyncStreamDecoder
    :keyword deserialization_callback: A callback that takes the response and the decoded event and
        returns a deserialized object.
    :paramtype deserialization_callback: Callable[[~corehttp.rest.AsyncHttpResponse, Any], ReturnType]
    """

    def __init__(
        self,
        *,
        response: AsyncHttpResponse,
        deserialization_callback: Callable[[AsyncHttpResponse, DecodedType], ReturnType_co],
        decoder: Optional[AsyncStreamDecoder[DecodedType]] = None,
    ) -> None:
        self._response = response
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        self._decoder: AsyncStreamDecoder[Any] = (
            decoder
            if decoder is not None
            else (AsyncSSEDecoder() if content_type == "text/event-stream" else AsyncJSONLDecoder())
        )
        self._deserialization_callback = deserialization_callback
        self._iterator = self._iter_results()

    async def __anext__(self) -> ReturnType_co:
        return await self._iterator.__anext__()

    def __aiter__(self) -> Self:
        return self

    async def _iter_results(self) -> AsyncIterator[ReturnType_co]:
        async for event in self._decoder.aiter_events(self._response.iter_bytes()):

            result = self._deserialization_callback(self._response, event)
            yield result

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.close()

    async def __aenter__(self) -> Self:
        return self

    async def close(self) -> None:
        await self._response.close()
