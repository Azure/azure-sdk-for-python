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
from typing import Iterator, AsyncIterator, TypeVar, Callable, Any, Optional, Type, Protocol

from typing_extensions import Self, runtime_checkable

from ..rest import HttpRequest, HttpResponse, AsyncHttpResponse
from ..runtime.pipeline import PipelineResponse
from ._decoders import JSONLDecoder, AsyncJSONLDecoder


ReturnType = TypeVar("ReturnType")


@runtime_checkable
class EventType(Protocol):
    """Protocol for event types."""

    data: str
    """The event data."""

    def json(self) -> Any:
        """Parse the event data as JSON.

        :return: The parsed JSON data.
        """
        ...


@runtime_checkable
class StreamDecoder(Protocol):
    """Protocol for stream decoders."""

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[EventType]:
        """Iterate over events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :return: An iterator of events.
        """
        ...

    def event(self) -> EventType:
        """Get the current event.

        :rtype: EventType
        :return: The current event.
        """
        ...

    def decode(self, line: bytes) -> None:
        """Decode a line of bytes.

        :param bytes line: A line of bytes to decode.
        """
        ...


@runtime_checkable
class AsyncStreamDecoder(Protocol):
    """Protocol for async stream decoders."""

    # Why this isn't async def: https://mypy.readthedocs.io/en/stable/more_types.html#asynchronous-iterators
    def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[EventType]:
        """Asynchronously iterate over events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :return: An asynchronous iterator of events.
        """
        ...

    def event(self) -> EventType:
        """Get the current event.

        :return: The current event.
        """
        ...

    def decode(self, line: bytes) -> None:
        """Decode a line of bytes.

        :param bytes line: A line of bytes to decode.
        """
        ...


class Stream(Iterator[ReturnType]):
    """Stream class for streaming JSONL or Server-Sent Events (SSE).

    :keyword response: The pipeline response object.
    :paramtype response: ~azure.core.pipeline.PipelineResponse
    :keyword deserialization_callback: A callback that takes HttpResponse and JSON and
        returns a deserialized object
    :paramtype deserialization_callback: Callable[[Any, Any], ReturnType]
    :keyword decoder: An optional decoder to use for the stream. If not provided, the content-type
        of the response will be used to determine the decoder.
    :paramtype decoder: Optional[StreamDecoder]
    :paramtype terminal_event: Optional[str]
    :keyword terminal_event: A terminal event that indicates the end of the SSE stream.
    :paramtype terminal_event: Optional[str]
    """

    def __init__(
        self,
        *,
        response: PipelineResponse[HttpRequest, HttpResponse],
        deserialization_callback: Callable[[Any, Any], ReturnType],
        decoder: Optional[StreamDecoder] = None,
        terminal_event: Optional[str] = None,
    ) -> None:
        self._pipeline_response = response
        self._response = response.http_response
        self._deserialization_callback = deserialization_callback
        self._terminal_event = terminal_event
        self._iterator = self._iter_results()

        if decoder is not None:
            self._decoder = decoder
        elif self._response.headers.get("Content-Type", "").lower() == "application/jsonl":
            self._decoder = JSONLDecoder()
        else:
            raise ValueError(
                f"Unsupported content-type "
                f"'{self._response.headers.get('Content-Type', '')}' "
                "for streaming. Provide a custom decoder."
            )

    def __next__(self) -> ReturnType:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[ReturnType]:
        yield from self._iterator

    def _iter_results(self) -> Iterator[ReturnType]:
        for event in self._decoder.iter_events(self._response.iter_bytes()):
            if event.data == self._terminal_event:
                break

            result = self._deserialization_callback(self._pipeline_response, event.json())
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


class AsyncStream(AsyncIterator[ReturnType]):
    """AsyncStream class for asynchronously streaming JSONL or Server-Sent Events (SSE).

    :keyword response: The pipeline response object.
    :paramtype response: ~azure.core.pipeline.PipelineResponse
    :keyword deserialization_callback: A callback that takes AsyncHttpResponse and JSON and
        returns a deserialized object
    :paramtype deserialization_callback: Callable[[Any, Any], ReturnType]
    :keyword decoder: An optional decoder to use for the stream. If not provided, the content-type
        of the response will be used to determine the decoder.
    :paramtype decoder: Optional[AsyncStreamDecoder]
    :paramtype terminal_event: Optional[str]
    :keyword terminal_event: A terminal event that indicates the end of the SSE stream.
    :paramtype terminal_event: Optional[str]
    """

    def __init__(
        self,
        *,
        response: PipelineResponse[HttpRequest, AsyncHttpResponse],
        deserialization_callback: Callable[[Any, Any], ReturnType],
        decoder: Optional[AsyncStreamDecoder] = None,
        terminal_event: Optional[str] = None,
    ) -> None:
        self._pipeline_response = response
        self._response = response.http_response
        self._deserialization_callback = deserialization_callback
        self._terminal_event = terminal_event
        self._iterator = self._iter_results()

        if decoder is not None:
            self._decoder = decoder
        elif self._response.headers.get("Content-Type", "").lower() == "application/jsonl":
            self._decoder = AsyncJSONLDecoder()
        else:
            raise ValueError(
                f"Unsupported content-type "
                f"'{self._response.headers.get('Content-Type', '')}' "
                "for streaming. Provide a custom decoder."
            )

    async def __anext__(self) -> ReturnType:
        return await self._iterator.__anext__()

    async def __aiter__(self) -> AsyncIterator[ReturnType]:  # pylint: disable=invalid-overridden-method
        async for item in self._iterator:
            yield item

    async def _iter_results(self) -> AsyncIterator[ReturnType]:
        async for event in self._decoder.aiter_events(self._response.iter_bytes()):
            if event.data == self._terminal_event:
                break

            result = self._deserialization_callback(self._pipeline_response, event.json())
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
