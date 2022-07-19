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

import sys
from ._base import HttpTransport, HttpRequest, HttpResponse

__all__ = [
    'HttpTransport',
    'HttpRequest',
    'HttpResponse',
]

# pylint: disable=unused-import, redefined-outer-name
try:
    from ._requests_basic import RequestsTransport, RequestsTransportResponse
    __all__.extend([
        'RequestsTransport',
        'RequestsTransportResponse',
    ])
    try:
        from ._base_async import AsyncHttpTransport, AsyncHttpResponse
        from ._requests_asyncio import AsyncioRequestsTransport, AsyncioRequestsTransportResponse

        __all__.extend([
            'AsyncHttpTransport',
            'AsyncHttpResponse',
            'AsyncioRequestsTransport',
            'AsyncioRequestsTransportResponse'
            'TrioRequestsTransport',
            'TrioRequestsTransportResponse',
            'AioHttpTransport',
            'AioHttpTransportResponse',
        ])

        
        def __dir__():
            return __all__

        def __getattr__(name):
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

    except (ImportError, SyntaxError):
        # requests library is installed but asynchronous pipelines not supported.
        pass
except (ImportError, SyntaxError):
    # requests library is not installed
    try:
        from ._base_async import AsyncHttpTransport, AsyncHttpResponse
        __all__.extend([
            'AsyncHttpTransport',
            'AsyncHttpResponse',
            'AioHttpTransport',
            'AioHttpTransportResponse',
        ])
        def __dir__():
            return __all__
        def __getattr__(name):
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
            return name
    except (ImportError, SyntaxError):
        pass  # Asynchronous pipelines not supported.
