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
from typing import Iterator, AsyncIterator, List, Optional


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
        return f"ServerSentEvent(event={self.event!r}, data={self.data!r}, " f"id={self.id!r}, retry={self.retry!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServerSentEvent):
            return NotImplemented
        return (self.event, self.data, self.id, self.retry) == (
            other.event,
            other.data,
            other.id,
            other.retry,
        )


class _SSELineFramer:
    """Incremental SSE line framer with linear-time behavior.

    Per the SSE spec, lines may be separated by ``"\\r\\n"``, ``"\\r"`` or ``"\\n"``. A lone trailing
    ``"\\r"`` at a chunk boundary is ambiguous (it may be the first half of a ``"\\r\\n"``) and its
    resolution is deferred until the next chunk (or EOF).

    Rather than re-concatenating and re-scanning the whole pending line on every network chunk
    (which is O(n^2) for a single long line fragmented across many chunks), the unfinished line is
    held as a list of fragments and joined only when a terminator arrives (or at EOF). Only the
    newly decoded text is scanned per chunk, giving O(total) behavior.
    """

    def __init__(self) -> None:
        # Fragments of the current, not-yet-terminated line. Never contains a separator.
        self._parts: List[str] = []
        # True when the previous chunk ended with a lone "\r" whose "\r\n" status is still unknown.
        self._pending_cr = False

    def _emit_current(self) -> str:
        line = "".join(self._parts)
        self._parts = []
        return line

    def push(self, text: str) -> List[str]:
        """Feed newly decoded text and return any completed lines.

        :param text: Newly decoded text from a single chunk.
        :type text: str
        :return: Completed lines (separators stripped) produced by this chunk.
        :rtype: list[str]
        """
        if not text:
            return []

        out: List[str] = []
        if self._pending_cr:
            # The deferred "\r" terminates the current line now that more data is available.
            out.append(self._emit_current())
            self._pending_cr = False
            # A leading "\n" is the second half of that "\r\n" pair: consume it.
            if text[:1] == "\n":
                text = text[1:]

        n = len(text)
        start = 0
        i = 0
        while i < n:
            char = text[i]
            if char == "\n":
                self._parts.append(text[start:i])
                out.append(self._emit_current())
                i += 1
                start = i
            elif char == "\r":
                if i + 1 < n:
                    self._parts.append(text[start:i])
                    out.append(self._emit_current())
                    i += 2 if text[i + 1] == "\n" else 1
                    start = i
                else:
                    # Trailing lone "\r": defer resolution until the next chunk.
                    self._parts.append(text[start:i])
                    self._pending_cr = True
                    start = n
                    break
            else:
                i += 1

        if start < n:
            self._parts.append(text[start:n])
        return out

    def flush(self, extra: str = "") -> List[str]:
        """Return any remaining lines at end of stream.

        A lone trailing ``"\\r"`` is treated as a terminator (its ``"\\r\\n"`` half never arrives),
        and a non-empty final unterminated line is emitted; an empty tail is not, so no blank line
        (and therefore no spurious event) is invented at EOF.

        :param extra: Trailing text from finalizing the incremental decoder.
        :type extra: str
        :return: The remaining lines, if any.
        :rtype: list[str]
        """
        out: List[str] = []
        if self._pending_cr:
            out.append(self._emit_current())
            self._pending_cr = False
            if extra[:1] == "\n":
                extra = extra[1:]

        if extra:
            out.extend(self.push(extra))

        if self._pending_cr:
            # 'extra' ended in a lone "\r": at EOF it is a terminator; emit the preceding content.
            out.append(self._emit_current())
            self._pending_cr = False
        else:
            tail = self._emit_current()
            if tail:
                out.append(tail)
        return out


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
    framer = _SSELineFramer()

    for chunk in iter_bytes:
        yield from framer.push(decoder.decode(chunk))

    yield from framer.flush(decoder.decode(b"", final=True))


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
    framer = _SSELineFramer()

    try:
        async for chunk in iter_bytes:
            for line in framer.push(decoder.decode(chunk)):
                yield line
    finally:
        aclose = getattr(iter_bytes, "aclose", None)
        if aclose is not None:
            await aclose()

    for line in framer.flush(decoder.decode(b"", final=True)):
        yield line


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
