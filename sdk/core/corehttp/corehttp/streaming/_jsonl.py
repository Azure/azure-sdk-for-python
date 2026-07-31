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
from typing import Iterator, AsyncIterator, Any, MutableMapping, Generic

from typing_extensions import TypeVar


T = TypeVar("T", default=MutableMapping[str, Any])


def iter_lines(iter_bytes: Iterator[bytes]) -> Iterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()

    # Split only on "\n" (tolerating "\r\n") rather than using str.splitlines(),
    # which would also break on other Unicode boundaries (\v, \f, \x1c-\x1e, \x85,
    # \u2028, \u2029) that are valid inside a JSONL record's string value.
    decoded = ""
    for chunk in iter_bytes:
        decoded += decoder.decode(chunk)
        if decoded:
            decoded_lines = [line[:-1] if line.endswith("\r") else line for line in decoded.split("\n")]
            yield from decoded_lines[:-1]
            decoded = decoded_lines[-1]

    decoded += decoder.decode(b"", final=True)
    if decoded:
        yield decoded[:-1] if decoded.endswith("\r") else decoded


async def aiter_lines(iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()

    # Split only on "\n" (tolerating "\r\n") rather than using str.splitlines(),
    # which would also break on other Unicode boundaries (\v, \f, \x1c-\x1e, \x85,
    # \u2028, \u2029) that are valid inside a JSONL record's string value.
    decoded = ""
    async for chunk in iter_bytes:
        decoded += decoder.decode(chunk)
        if decoded:
            decoded_lines = [line[:-1] if line.endswith("\r") else line for line in decoded.split("\n")]
            for line in decoded_lines[:-1]:
                yield line
            decoded = decoded_lines[-1]

    decoded += decoder.decode(b"", final=True)
    if decoded:
        yield decoded[:-1] if decoded.endswith("\r") else decoded


class JSONLDecoder(Generic[T]):
    """Decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[T]:
        """Iterate over JSONL events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :rtype: Iterator[T]
        :return: An iterator of objects.
        """

        yield from (json.loads(line) for line in iter_lines(iter_bytes))


class AsyncJSONLDecoder(Generic[T]):
    """Asynchronous decoder for JSON Lines (JSONL) format. https://jsonlines.org/"""

    # pylint: disable=invalid-overridden-method
    async def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[T]:
        """Asynchronously iterate over JSONL events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :rtype: AsyncIterator[T]
        :return: An asynchronous iterator of objects.
        """

        async for line in aiter_lines(iter_bytes):
            yield json.loads(line)
