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
import json
from contextlib import aclosing
from typing import Iterator, AsyncIterator, Any, List, Optional, cast


class JSONLEvent:
    """A single JSON Lines (JSONL) event.

    :ivar data: The raw JSONL record.
    :vartype data: str or None
    """

    def __init__(
        self,
        *,
        data: Optional[str] = None,
    ) -> None:
        self.data = data

    def json(self) -> Any:
        """Parse the event data as JSON.

        :return: The parsed JSON value.
        :rtype: Any
        """
        return json.loads(cast(str, self.data))


class _JSONLLineFramer:
    """Incremental JSONL line framer with linear-time behavior.

    JSONL records are separated only by ``"\\n"`` (tolerating ``"\\r\\n"``). Unlike
    ``str.splitlines()``, other Unicode boundaries (``\\v``, ``\\f``, ``\\x1c``-``\\x1e``,
    ``\\x85``, ``\\u2028``, ``\\u2029``) are preserved because they are valid inside a JSONL
    record's string value.

    Rather than re-concatenating and re-splitting the whole pending record on every network chunk
    (which is O(n^2) for a single long record fragmented across many chunks), the unfinished record
    is held as a list of fragments and joined only when a terminator arrives (or at EOF). Only the
    newly decoded text is scanned per chunk, giving O(total) behavior.
    """

    def __init__(self) -> None:
        # Fragments of the current, not-yet-terminated record. Never contains a "\n".
        self._parts: List[str] = []

    def push(self, text: str) -> List[str]:
        """Feed newly decoded text and return any completed records.

        :param text: Newly decoded text from a single chunk.
        :type text: str
        :return: Completed records produced by this chunk (may be empty).
        :rtype: list[str]
        """
        if not text:
            return []

        segments = text.split("\n")
        # Fast path: no line terminator, so this is a continuation of the current record. Stash the
        # fragment without joining or rescanning the accumulated tail.
        if len(segments) == 1:
            self._parts.append(text)
            return []

        first = "".join(self._parts) + segments[0]
        # All but the final segment are complete records (terminated by "\n"). Strip a trailing "\r"
        # to tolerate "\r\n" line endings.
        completed = [line[:-1] if line.endswith("\r") else line for line in [first, *segments[1:-1]]]
        self._parts = [segments[-1]]
        return completed

    def flush(self, extra: str = "") -> List[str]:
        """Return the final unterminated record, if any, at end of stream.

        :param extra: Trailing text from finalizing the incremental decoder.
        :type extra: str
        :return: The final record, if non-empty.
        :rtype: list[str]
        """
        tail = "".join(self._parts) + extra
        self._parts = []
        if not tail:
            return []
        return [tail[:-1] if tail.endswith("\r") else tail]


def iter_lines(iter_bytes: Iterator[bytes]) -> Iterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    framer = _JSONLLineFramer()

    for chunk in iter_bytes:
        yield from framer.push(decoder.decode(chunk))

    yield from framer.flush(decoder.decode(b"", final=True))


async def aiter_lines(iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    framer = _JSONLLineFramer()

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


class JSONLDecoder:
    """Decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[JSONLEvent]:
        """Iterate over JSONL events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :rtype: Iterator[~azure.core.streaming.JSONLEvent]
        :return: An iterator of JSONL events.
        """

        yield from (JSONLEvent(data=line) for line in iter_lines(iter_bytes))


class AsyncJSONLDecoder:
    """Asynchronous decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    # pylint: disable=invalid-overridden-method
    async def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[JSONLEvent]:
        """Asynchronously iterate over JSONL events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :rtype: AsyncIterator[~azure.core.streaming.JSONLEvent]
        :return: An asynchronous iterator of JSONL events.
        """

        async with aclosing(aiter_lines(iter_bytes)) as lines:
            async for line in lines:
                yield JSONLEvent(data=line)
