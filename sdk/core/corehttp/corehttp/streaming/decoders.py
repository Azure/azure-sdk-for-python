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


from typing import Iterator, AsyncIterator, Tuple, Protocol

from typing_extensions import runtime_checkable

from .events import JSONLEvent, EventType


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


class JSONLDecoder:
    """Decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    def __init__(self) -> None:
        self._data: str = ""
        self._line_separators: Tuple[bytes, ...] = (b"\n", b"\r\n")

    def decode(self, line: bytes) -> None:
        """Decode a line of bytes into a string.

        :param bytes line: A line of bytes to decode.
        :rtype: None
        """
        self._data = line.decode("utf-8")

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[JSONLEvent]:
        """Iterate over JSONL events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :rtype: Iterator[JSONLEvent]
        :return: An iterator of JSONLEvent objects.
        """
        data = b""
        for chunk in iter_bytes:
            for line in chunk.splitlines(keepends=True):
                data += line
                if data.endswith(self._line_separators):
                    self.decode(data.splitlines()[0])
                    event = self.event()
                    yield event
                    data = b""

        if data:
            # the last line did not end with a line separator
            # ok per JSONL spec
            self.decode(data)
            event = self.event()
            yield event

    def event(self) -> JSONLEvent:
        """Get the current event.

        :rtype: JSONLEvent
        :return: The current event.
        """
        jsonl = JSONLEvent(data=self._data)
        self._data = ""
        return jsonl


class AsyncJSONLDecoder:
    """Asynchronous decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    def __init__(self) -> None:
        self._data: str = ""
        self._line_separators: Tuple[bytes, ...] = (b"\n", b"\r\n")

    def decode(self, line: bytes) -> None:
        """Decode a line of bytes into a string.

        :param bytes line: A line of bytes to decode.
        :rtype: None
        """
        self._data = line.decode("utf-8")

    async def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[JSONLEvent]:
        """Asynchronously iterate over JSONL events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :rtype: AsyncIterator[JSONLEvent]
        :return: An asynchronous iterator of JSONLEvent objects.
        """
        data = b""
        async for chunk in iter_bytes:
            for line in chunk.splitlines(keepends=True):
                data += line
                if data.endswith(self._line_separators):
                    self.decode(data.splitlines()[0])
                    event = self.event()
                    yield event
                    data = b""

        if data:
            # the last line did not end with a line separator
            # ok per JSONL spec
            self.decode(data)
            event = self.event()
            yield event

    def event(self) -> JSONLEvent:
        """Get the current event.

        :rtype: JSONLEvent
        :return: The current event.
        """
        jsonl = JSONLEvent(data=self._data)
        self._data = ""
        return jsonl
