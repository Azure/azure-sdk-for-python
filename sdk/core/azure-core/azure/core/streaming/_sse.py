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
from contextlib import aclosing
from typing import Iterator, AsyncIterator, List, Optional, Tuple


class ServerSentEvent:
    """A single Server-Sent Event (SSE).

    https://html.spec.whatwg.org/multipage/server-sent-events.html

    :ivar event: The event type. Defaults to ``"message"`` when the stream does not
        specify one.
    :vartype event: str
    :ivar data: The event payload. Multiple ``data`` lines are joined with ``"\\n"``.
        Left as a raw string; the caller is responsible for any further parsing.
    :vartype data: str
    :ivar id: The last event ID. Defaults to an empty string until the stream
        provides one.
    :vartype id: str
    :ivar retry: The reconnection time in milliseconds, if the stream provided one.
    :vartype retry: int or None
    """

    def __init__(
        self,
        *,
        event: str = "message",
        data: str = "",
        id: str = "",  # pylint: disable=redefined-builtin
        retry: Optional[int] = None,
    ) -> None:
        self.event = event
        self.data = data
        self.id = id
        self.retry = retry

    def __repr__(self) -> str:
        return (
            f"ServerSentEvent(event={self.event!r}, data={self.data!r}, "
            f"id={self.id!r}, retry={self.retry!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServerSentEvent):
            return NotImplemented
        return (self.event, self.data, self.id, self.retry) == (
            other.event,
            other.data,
            other.id,
            other.retry,
        )


def _split_sse_lines(buf: str) -> Tuple[List[str], str]:
    """Split ``buf`` into complete SSE lines plus a trailing remainder.

    Per the SSE spec, lines may be separated by ``\\r\\n``, ``\\r`` or ``\\n``. A lone
    trailing ``\\r`` is kept in the remainder because it may be the first half of a
    ``\\r\\n`` that arrives in a later chunk.

    :param buf: The buffered, already UTF-8 decoded text.
    :type buf: str
    :return: A tuple of ``(complete_lines, remainder)`` where ``remainder`` is the
        unterminated tail (never containing a line separator, except a single trailing
        ``\\r`` awaiting a possible ``\\n``).
    :rtype: tuple[list[str], str]
    """
    lines: List[str] = []
    start = 0
    i = 0
    n = len(buf)
    while i < n:
        char = buf[i]
        if char == "\n":
            lines.append(buf[start:i])
            i += 1
            start = i
        elif char == "\r":
            if i + 1 < n:
                lines.append(buf[start:i])
                i += 2 if buf[i + 1] == "\n" else 1
                start = i
            else:
                # Trailing lone "\r": ambiguous, defer until the next chunk.
                break
        else:
            i += 1
    return lines, buf[start:]


def _iter_sse_lines(iter_bytes: Iterator[bytes]) -> Iterator[str]:
    """Iterate over SSE lines (line separators stripped) from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of decoded lines.
    """
    # SSE is always UTF-8 (WHATWG spec). Use utf-8-sig to drop one leading BOM and
    # errors="replace" so invalid byte sequences become U+FFFD instead of crashing.
    decoder = codecs.getincrementaldecoder("utf-8-sig")(errors="replace")

    buf = ""
    for chunk in iter_bytes:
        buf += decoder.decode(chunk)
        lines, buf = _split_sse_lines(buf)
        yield from lines

    buf += decoder.decode(b"", final=True)
    lines, remainder = _split_sse_lines(buf)
    yield from lines
    if remainder:
        yield remainder[:-1] if remainder.endswith("\r") else remainder


async def _aiter_sse_lines(iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """Asynchronously iterate over SSE lines (separators stripped) from a byte iterator.

    :param iter_bytes: An asynchronous iterator of byte chunks.
    :type iter_bytes: AsyncIterator[bytes]
    :rtype: AsyncIterator[str]
    :return: An asynchronous iterator of decoded lines.
    """
    # SSE is always UTF-8 (WHATWG spec). Use utf-8-sig to drop one leading BOM and
    # errors="replace" so invalid byte sequences become U+FFFD instead of crashing.
    decoder = codecs.getincrementaldecoder("utf-8-sig")(errors="replace")

    buf = ""
    try:
        async for chunk in iter_bytes:
            buf += decoder.decode(chunk)
            lines, buf = _split_sse_lines(buf)
            for line in lines:
                yield line
    finally:
        aclose = getattr(iter_bytes, "aclose", None)
        if aclose is not None:
            await aclose()

    buf += decoder.decode(b"", final=True)
    lines, remainder = _split_sse_lines(buf)
    for line in lines:
        yield line
    if remainder:
        yield remainder[:-1] if remainder.endswith("\r") else remainder


class _SSEEventBuilder:
    """Accumulates SSE field lines and builds :class:`ServerSentEvent` instances."""

    def __init__(self) -> None:
        self._data: List[str] = []
        self._event_type = ""
        self._last_id = ""
        self._retry: Optional[int] = None

    def add_line(self, line: str) -> Optional[ServerSentEvent]:
        """Process a single SSE line, dispatching an event on a blank line.

        :param line: A single SSE line with its terminator already stripped.
        :type line: str
        :return: A :class:`ServerSentEvent` when ``line`` is blank and an event is
            pending, otherwise ``None``.
        :rtype: ~azure.core.streaming.ServerSentEvent or None
        """
        if line == "":
            return self._dispatch()
        if line.startswith(":"):
            # Comment line, ignored.
            return None

        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]

        if field == "event":
            self._event_type = value
        elif field == "data":
            self._data.append(value)
        elif field == "id":
            if "\x00" not in value:
                self._last_id = value
        elif field == "retry":
            if value.isascii() and value.isdigit():
                try:
                    self._retry = int(value)
                except ValueError:
                    # All ASCII digits but too long for int() (CPython's int-string
                    # conversion limit). Ignore rather than crashing the stream.
                    pass
        # Unknown fields are ignored per spec.
        return None

    def _dispatch(self) -> Optional[ServerSentEvent]:
        if not self._data:
            # No data accumulated: reset and dispatch nothing.
            self._event_type = ""
            return None
        event = ServerSentEvent(
            event=self._event_type or "message",
            data="\n".join(self._data),
            id=self._last_id,
            retry=self._retry,
        )
        self._data = []
        self._event_type = ""
        return event


class SSEDecoder:
    """Decoder for Server-Sent Events (SSE).

    https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[ServerSentEvent]:
        """Iterate over SSE events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :rtype: Iterator[~azure.core.streaming.ServerSentEvent]
        :return: An iterator of server-sent events.
        """
        builder = _SSEEventBuilder()
        for line in _iter_sse_lines(iter_bytes):
            event = builder.add_line(line)
            if event is not None:
                yield event


class AsyncSSEDecoder:
    """Asynchronous decoder for Server-Sent Events (SSE).

    https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    # pylint: disable=invalid-overridden-method
    async def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[ServerSentEvent]:
        """Asynchronously iterate over SSE events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :rtype: AsyncIterator[~azure.core.streaming.ServerSentEvent]
        :return: An asynchronous iterator of server-sent events.
        """
        builder = _SSEEventBuilder()
        async with aclosing(_aiter_sse_lines(iter_bytes)) as lines:
            async for line in lines:
                event = builder.add_line(line)
                if event is not None:
                    yield event
