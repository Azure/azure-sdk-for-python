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
"""Generic stream iterator for SSE and JSONL streaming."""
from typing import Iterator, TypeVar, Callable, Any, Optional, Union
from types import TracebackType
from typing_extensions import Self

from ..pipeline import PipelineResponse
from ._sse_decoder import SSEDecoder, ServerSentEvent
from ._jsonl_decoder import JSONLDecoder, JSONLEvent


ReturnType = TypeVar("ReturnType")


class Stream(Iterator[ReturnType]):
    """Generic stream iterator for SSE and JSONL streaming.

    Provides a unified interface for iterating over streaming responses,
    automatically detecting the content type and using the appropriate
    decoder (SSE or JSONL).

    :keyword response: The pipeline response containing the HTTP response.
    :paramtype response: ~azure.core.pipeline.PipelineResponse
    :keyword deserialization_callback: A callback that takes the HTTP response and
        parsed event data (dict), and returns a deserialized model object.
    :paramtype deserialization_callback: Callable[[Any, Any], ReturnType]
    :keyword terminal_event: Optional terminal event data that indicates the end
        of the stream. When this value is encountered in the event data, iteration stops.
    :paramtype terminal_event: Optional[str]
    """

    def __init__(
        self,
        *,
        response: PipelineResponse,
        deserialization_callback: Callable[[Any, Any], ReturnType],
        terminal_event: Optional[str] = None,
    ) -> None:
        self._response = response.http_response
        self._deserialization_callback = deserialization_callback
        self._terminal_event = terminal_event

        # Auto-detect content type and select appropriate decoder
        content_type = self._response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            self._decoder: Union[SSEDecoder, JSONLDecoder] = SSEDecoder()
        else:
            # Default to JSONL for application/jsonl, application/x-ndjson, or unknown types
            self._decoder = JSONLDecoder()

        self._iterator = self._iter_events()

    def __next__(self) -> ReturnType:
        """Get the next item from the stream.

        :return: The next deserialized item.
        :rtype: ReturnType
        :raises StopIteration: When the stream is exhausted.
        """
        return next(self._iterator)

    def __iter__(self) -> Iterator[ReturnType]:
        """Return the iterator.

        :return: The stream iterator.
        :rtype: Iterator[ReturnType]
        """
        return self

    def _iter_events(self) -> Iterator[ReturnType]:
        """Internal method to iterate over parsed events.

        :return: Iterator of deserialized events.
        :rtype: Iterator[ReturnType]
        """
        for line in self._parse_chunks(self._response.iter_bytes()):
            for data in line.splitlines():
                if data:
                    # Feed non-empty lines to the decoder
                    self._decoder.decode(data)
                else:
                    # Empty line signals end of event
                    event: Union[ServerSentEvent, JSONLEvent] = self._decoder.event()

                    # Check for terminal event
                    if self._terminal_event and event.data == self._terminal_event:
                        return

                    # Deserialize and yield the event
                    try:
                        event_json = event.json()
                        if event_json is not None:
                            event_model = self._deserialization_callback(self._response, event_json)
                            yield event_model
                    except Exception:
                        # Skip events that fail to deserialize
                        continue

    def _parse_chunks(self, iter_bytes: Iterator[bytes]) -> Iterator[str]:
        """Parse byte chunks into complete lines.

        Handles partial lines across chunk boundaries.

        :param iter_bytes: Iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :return: Iterator of complete lines.
        :rtype: Iterator[str]
        """
        data = b""
        for chunk in iter_bytes:
            for line in chunk.splitlines(keepends=True):
                data += line
                # Check if we have a complete event (double newline)
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data.decode("utf-8")
                    data = b""

        # Yield any remaining data
        if data:
            yield data.decode("utf-8")

    def __enter__(self) -> Self:
        """Enter the context manager.

        :return: The stream object.
        :rtype: Self
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the context manager and close the stream.

        :param exc_type: The exception type if an exception was raised.
        :type exc_type: Optional[type[BaseException]]
        :param exc: The exception instance if an exception was raised.
        :type exc: Optional[BaseException]
        :param exc_tb: The traceback if an exception was raised.
        :type exc_tb: Optional[TracebackType]
        """
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP response."""
        self._response.close()
