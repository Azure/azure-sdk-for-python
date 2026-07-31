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

from typing import Iterator, AsyncIterator, Protocol

from typing_extensions import runtime_checkable, TypeVar


T_co = TypeVar("T_co", covariant=True)


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
