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
from ..exceptions import StreamClosedError, StreamConsumedError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Callable,
        Optional,
        Iterator,
    )
    from azure.core.rest import HttpResponse

def await_result(func, *args, **kwargs):
    """If func returns an awaitable, raise that this runner can't handle it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        raise TypeError(
            "Policy {} returned awaitable object in non-async pipeline.".format(func)
        )
    return result

def _stream_download_helper(decompress, stream_download_generator, response, chunk_size=None):
    # type: (bool, Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    if response.is_stream_consumed:
        raise StreamConsumedError()
    if response.is_closed:
        raise StreamClosedError()

    response.is_stream_consumed = True
    stream_download = stream_download_generator(
        pipeline=None,
        response=response,
        chunk_size=chunk_size or response._connection_data_block_size,  # pylint: disable=protected-access
        decompress=decompress,
    )
    for part in stream_download:
        response._num_bytes_downloaded += len(part)
        yield part

def iter_bytes_helper(stream_download_generator, response, chunk_size=None):
    # type: (Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    if response._has_content():  # pylint: disable=protected-access
        if chunk_size is None:
            chunk_size = len(response.content)
        for i in range(0, len(response.content), chunk_size):
            yield response.content[i: i + chunk_size]
    else:
        for part in _stream_download_helper(
            decompress=True,
            stream_download_generator=stream_download_generator,
            response=response,
            chunk_size=chunk_size
        ):
            yield part
    response.close()

def iter_raw_helper(stream_download_generator, response, chunk_size=None):
    # type: (Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    for raw_bytes in _stream_download_helper(
        decompress=False,
        stream_download_generator=stream_download_generator,
        response=response,
        chunk_size=chunk_size
    ):
        yield raw_bytes
    response.close()

def to_rest_response_helper(pipeline_transport_response, response_type):
    response = response_type(
        request=pipeline_transport_response.request._to_rest_request(),  # pylint: disable=protected-access
        internal_response=pipeline_transport_response.internal_response,
    )
    response._connection_data_block_size = pipeline_transport_response.block_size  # pylint: disable=protected-access
    return response

def set_block_size(response, **kwargs):
    chunk_size = kwargs.pop("chunk_size", None)
    if not chunk_size:
        if hasattr(response, "block_size"):
            chunk_size = response.block_size
        elif hasattr(response, "_connection_data_block_size"):
            chunk_size = response._connection_data_block_size  # pylint: disable=protected-access
    return chunk_size
