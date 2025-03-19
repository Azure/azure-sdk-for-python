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
from typing import Iterator, AsyncIterator, TypeVar, Callable, Optional, Type

from typing_extensions import Self

from ..rest import HttpResponse, AsyncHttpResponse
from ._decoders import StreamDecoder, AsyncStreamDecoder

DecodedType = TypeVar("DecodedType")
ReturnType_co = TypeVar("ReturnType_co", covariant=True)


class Stream(Iterator[ReturnType_co]):
    """Stream class for streaming JSONL.

    :keyword response: The response object.
    :paramtype response: ~corehttp.rest.HttpResponse
    :keyword decoder: A decoder to use for the stream.
    :paramtype decoder: ~corehttp.streaming.decoders.StreamDecoder
    :keyword deserialization_callback: A callback that takes JSON and returns a deserialized object.
    :paramtype deserialization_callback: Callable[[Any], ReturnType]
    """

    def __init__(
        self,
        *,
        response: HttpResponse,
        decoder: StreamDecoder[DecodedType],
        deserialization_callback: Callable[[DecodedType], ReturnType_co],
    ) -> None:
        self._response = response
        self._decoder = decoder
        self._deserialization_callback = deserialization_callback
        self._iterator = self._iter_results()

    def __next__(self) -> ReturnType_co:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[ReturnType_co]:
        yield from self._iterator

    def _iter_results(self) -> Iterator[ReturnType_co]:
        for event in self._decoder.iter_events(self._response.iter_bytes()):

            result = self._deserialization_callback(event)
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
    """AsyncStream class for asynchronously streaming JSONL.

    :keyword response: The response object.
    :paramtype response: ~corehttp.rest.AsyncHttpResponse
    :keyword decoder: A decoder to use for the stream.
    :paramtype decoder: ~corehttp.streaming.decoders.AsyncStreamDecoder
    :keyword deserialization_callback: A callback that takes JSON and returns a deserialized object.
    :paramtype deserialization_callback: Callable[[Any], ReturnType]
    """

    def __init__(
        self,
        *,
        response: AsyncHttpResponse,
        decoder: AsyncStreamDecoder[DecodedType],
        deserialization_callback: Callable[[DecodedType], ReturnType_co],
    ) -> None:
        self._response = response
        self._decoder = decoder
        self._deserialization_callback = deserialization_callback
        self._iterator = self._iter_results()

    async def __anext__(self) -> ReturnType_co:
        return await self._iterator.__anext__()

    async def __aiter__(self) -> AsyncIterator[ReturnType_co]:  # pylint: disable=invalid-overridden-method
        async for item in self._iterator:
            yield item

    async def _iter_results(self) -> AsyncIterator[ReturnType_co]:
        async for event in self._decoder.aiter_events(self._response.iter_bytes()):

            result = self._deserialization_callback(event)
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
