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
from typing import (
    AsyncIterable, Iterable, Mapping,
    Sequence,
    Tuple,
    Union,
    Optional,
    IO,
)


Primitives = Optional[Union[str, int, float, bool]]


# Everything is pretty much a dict of str -> content, or a list of tuples of str + content.
QueryTypes = Union[
    Mapping[str, Union[Primitives, Sequence[Primitives]]],
    Sequence[Tuple[str, Primitives]]
]

HeaderTypes = Union[
    Mapping[str, str],
    Sequence[Tuple[str, str]]
]


FileContent = Union[IO[str], IO[bytes], str, bytes]
FileTypes = Union[Mapping[str, FileContent], Sequence[Tuple[str, FileContent]]]

ByteStream = Union[Iterable[bytes], AsyncIterable[bytes]]
ContentTypes = Union[str, bytes, ByteStream]
