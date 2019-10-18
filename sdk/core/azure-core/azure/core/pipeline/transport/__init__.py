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

from ._base import HttpTransport, HttpRequest, HttpResponse
from ._requests_basic import RequestsTransport, RequestsTransportResponse

__all__ = [
    'HttpTransport',
    'HttpRequest',
    'HttpResponse',
    'RequestsTransport',
    'RequestsTransportResponse',
]

#pylint: disable=unused-import

try:
    from ._base_async import AsyncHttpTransport, AsyncHttpResponse
    from ._requests_asyncio import AsyncioRequestsTransport, AsyncioRequestsTransportResponse
    __all__.extend([
        'AsyncHttpTransport',
        'AsyncHttpResponse',
        'AsyncioRequestsTransport',
        'AsyncioRequestsTransportResponse'
    ])

    try:
        from ._requests_trio import TrioRequestsTransport, TrioRequestsTransportResponse
        __all__.extend([
            'TrioRequestsTransport',
            'TrioRequestsTransportResponse'
        ])
    except ImportError:
        pass  # Trio not installed

    try:
        from ._aiohttp import AioHttpTransport, AioHttpTransportResponse
        __all__.extend([
            'AioHttpTransport',
            'AioHttpTransportResponse',
        ])
    except ImportError:
        pass  # Aiohttp not installed
except (ImportError, SyntaxError):
    pass  # Asynchronous pipelines not supported.
