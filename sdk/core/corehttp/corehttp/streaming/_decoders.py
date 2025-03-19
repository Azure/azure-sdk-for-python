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
from typing import Iterator, AsyncIterator, Protocol, Any, MutableMapping, Generic

from typing_extensions import runtime_checkable, TypeVar

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T", default=MutableMapping[str, Any])


@runtime_checkable
class StreamDecoder(Protocol[T_co]):
    """Protocol for stream decoders."""

    def iter_events(self, iter_bytes: Iterator[bytes]) -> Iterator[T_co]:
        """Iterate over events from a byte iterator.

        :param iter_bytes: An iterator of byte chunks.
        :type iter_bytes: Iterator[bytes]
        :return: An iterator of decoded data.
        :rtype: Iterator[DecodedType_co]
        """
        ...


@runtime_checkable
class AsyncStreamDecoder(Protocol[T_co]):
    """Protocol for async stream decoders."""

    # Why this isn't async def: https://mypy.readthedocs.io/en/stable/more_types.html#asynchronous-iterators
    def aiter_events(self, iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[T_co]:
        """Asynchronously iterate over events from a byte iterator.

        :param iter_bytes: An asynchronous iterator of byte chunks.
        :type iter_bytes: AsyncIterator[bytes]
        :return: An asynchronous iterator of decoded data.
        :rtype: AsyncIterator[DecodedType_co]
        """
        ...


def iter_lines(iter_bytes: Iterator[bytes]) -> Iterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()

    decoded = ""
    for chunk in iter_bytes:
        decoded += decoder.decode(chunk)
        if decoded:
            decoded_lines = decoded.splitlines()
            if decoded.endswith(("\n", "\r\n")):
                yield from decoded_lines
                decoded = ""
            else:
                yield from decoded_lines[:-1]
                decoded = decoded_lines[-1]

    decoded += decoder.decode(b"", final=True)
    if decoded:
        yield from decoded.splitlines()


async def aiter_lines(iter_bytes: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """Iterate over lines from a byte iterator.

    :param iter_bytes: An iterator of byte chunks.
    :type iter_bytes: Iterator[bytes]
    :rtype: Iterator[str]
    :return: An iterator of lines.
    """
    decoder = codecs.getincrementaldecoder("utf-8")()

    decoded = ""
    async for chunk in iter_bytes:
        decoded += decoder.decode(chunk)
        if decoded:
            decoded_lines = decoded.splitlines()
            if decoded.endswith(("\n", "\r\n")):
                for line in decoded_lines:
                    yield line
                decoded = ""
            else:
                for line in decoded_lines[:-1]:
                    yield line
                decoded = decoded_lines[-1]

    decoded += decoder.decode(b"", final=True)
    if decoded:
        for line in decoded.splitlines():
            yield line


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
