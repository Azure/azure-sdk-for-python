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
from typing import Optional, Callable, AsyncIterator
from ..exceptions import StreamClosedError, StreamConsumedError

async def await_result(func, *args, **kwargs):
    """If func returns an awaitable, await it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        # type ignore on await: https://github.com/python/mypy/issues/7587
        return await result  # type: ignore
    return result

def _stream_download_helper(
    decompress: bool,
    stream_download_generator: Callable,
    response,
    chunk_size: Optional[int] = None,
) -> AsyncIterator[bytes]:
    if response.is_stream_consumed:
        raise StreamConsumedError()
    if response.is_closed:
        raise StreamClosedError()

    response.is_stream_consumed = True
    return stream_download_generator(
        pipeline=None,
        response=response,
        chunk_size=chunk_size,
        decompress=decompress,
    )

def iter_bytes_helper(
    stream_download_generator: Callable,
    response,
    chunk_size: Optional[int] = None,
) -> AsyncIterator[bytes]:
    return _stream_download_helper(
        decompress=True,
        stream_download_generator=stream_download_generator,
        response=response,
        chunk_size=chunk_size
    )

def iter_raw_helper(
    stream_download_generator: Callable,
    response,
    chunk_size: Optional[int] = None
) -> AsyncIterator[bytes]:
    return _stream_download_helper(
        decompress=False,
        stream_download_generator=stream_download_generator,
        response=response,
        chunk_size=chunk_size
    )
