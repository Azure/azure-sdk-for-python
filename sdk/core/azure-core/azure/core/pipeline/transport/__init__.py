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

__all__ = [
    'HttpTransport',
    'HttpRequest',
    'HttpResponse',
    'RequestsTransport',
    'RequestsTransportResponse',
    'AsyncHttpTransport',
    'AsyncHttpResponse',
    'AsyncioRequestsTransport',
    'AsyncioRequestsTransportResponse'
    'TrioRequestsTransport',
    'TrioRequestsTransportResponse',
    'AioHttpTransport',
    'AioHttpTransportResponse',
]

# pylint: disable=unused-import, redefined-outer-name

        
def __dir__():
    return __all__

def __getattr__(name):
    if name == 'AsyncioRequestsTransport':
        try:
            from ._requests_asyncio import AsyncHttpResponse
            return AsyncHttpResponse
        except ImportError:
            pass
    if name == 'AsyncioRequestsTransportResponse':
        try:
            from ._requests_asyncio import AsyncioRequestsTransportResponse
            return AsyncioRequestsTransportResponse
        except ImportError:
            pass
    if name == 'AsyncHttpTransport':
        try:
            from ._base_async import AsyncHttpTransport
            return AsyncHttpTransport
        except ImportError:
            pass
    if name == 'AsyncHttpResponse':
        try:
            from ._base_async import AsyncHttpResponse
            return AsyncHttpResponse
        except ImportError:
            pass
    if name == 'RequestsTransport':
        try:
            from ._requests_basic import RequestsTransport
            return RequestsTransport
        except ImportError:
            raise ImportError("requests package is not installed")
    if name == 'RequestsTransportResponse':
        try:
            from ._requests_basic import RequestsTransportResponse
            return RequestsTransportResponse
        except ImportError:
            raise ImportError("requests package is not installed")
    if name == 'AioHttpTransport':
        try:
            from ._aiohttp import AioHttpTransport
            return AioHttpTransport
        except ImportError:
            raise ImportError("aiohttp package is not installed")
    if name == 'AioHttpTransportResponse':
        try:
            from ._aiohttp import AioHttpTransportResponse
            return AioHttpTransportResponse
        except ImportError:
            raise ImportError("aiohttp package is not installed")
    if name == 'TrioRequestsTransport':
        try:
            from ._requests_trio import TrioRequestsTransport
            return TrioRequestsTransport
        except ImportError:
            raise ImportError("trio package is not installed")
    if name == 'TrioRequestsTransportResponse':
        try:
            from ._requests_trio import TrioRequestsTransportResponse
            return TrioRequestsTransportResponse
        except ImportError:
            raise ImportError("trio package is not installed")
    if name == '__bases__':
        raise AttributeError("module 'azure.core.pipeline.transport' has no attribute '__bases__'")
    return name