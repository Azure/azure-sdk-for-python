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
from ._helpers import (
    RequestNotReadError,
    ResponseNotReadError,
    StreamConsumedError,
    ResponseClosedError,
)
try:
    from ._rest_py3 import (
        HttpRequest,
        HttpResponse,
    )
except (SyntaxError, ImportError):
    from ._rest import (  # type: ignore
        HttpRequest,
        HttpResponse,
    )
from ._requests_basic import RequestsTransportResponse

__all__ = [
    "HttpRequest",
    "HttpResponse",
    "StreamConsumedError",
    "ResponseNotReadError",
    "ResponseClosedError",
    "RequestNotReadError",
    "RequestsTransportResponse",
]

try:
    from ._rest_py3 import (  # pylint: disable=unused-import
        AsyncHttpResponse,
        _AsyncContextManager,
    )
    __all__.extend([
        "AsyncHttpResponse",
        "_AsyncContextManager",
    ])

    if sys.version_info >= (3, 7):
        __all__.extend([
            'AioHttpTransportResponse',
        ])

        def __getattr__(name):
            if name == "AioHttpTransportResponse":
                try:
                    from ._aiohttp import AioHttpTransportResponse
                    return AioHttpTransportResponse
                except ImportError:
                    raise ImportError("aiohttp package is not installed")
            return name

except (SyntaxError, ImportError):
    pass

#### FOR BUGBASH

from ._sync_test_client import TestRestClient  # pylint: disable=unused-import
__all__.extend(["TestRestClient"])
try:
    from ._async_test_client import AsyncTestRestClient  # pylint: disable=unused-import
    __all__.extend(["AsyncTestRestClient"])
except (SyntaxError, ImportError):
    pass
