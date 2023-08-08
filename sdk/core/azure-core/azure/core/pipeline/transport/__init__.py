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
from typing import List
from ._base import HttpTransport, HttpRequest, HttpResponse
from ._base_async import AsyncHttpTransport, AsyncHttpResponse

# pylint: disable=undefined-all-variable

__all__ = [
    "HttpTransport",
    "HttpRequest",
    "HttpResponse",
    "RequestsTransport",
    "RequestsTransportResponse",
    "AsyncHttpTransport",
    "AsyncHttpResponse",
    "AsyncioRequestsTransport",
    "AsyncioRequestsTransportResponse",
    "TrioRequestsTransport",
    "TrioRequestsTransportResponse",
    "AioHttpTransport",
    "AioHttpTransportResponse",
]

# pylint: disable=unused-import, redefined-outer-name, no-member, too-many-statements, too-many-branches


def __dir__() -> List[str]:
    return __all__


# To do nice overloads, need https://github.com/python/mypy/issues/8203


def __getattr__(name: str):
    if name == "AsyncioRequestsTransport":
        try:
            from ._requests_asyncio import AsyncioRequestsTransport

            return AsyncioRequestsTransport
        except ImportError as err:
            raise ImportError("requests package is not installed") from err
    if name == "AsyncioRequestsTransportResponse":
        try:
            from ._requests_asyncio import AsyncioRequestsTransportResponse

            return AsyncioRequestsTransportResponse
        except ImportError as err:
            raise ImportError("requests package is not installed") from err
    if name == "RequestsTransport":
        try:
            from ._requests_basic import RequestsTransport

            return RequestsTransport
        except ImportError as err:
            raise ImportError("requests package is not installed") from err
    if name == "RequestsTransportResponse":
        try:
            from ._requests_basic import RequestsTransportResponse

            return RequestsTransportResponse
        except ImportError as err:
            raise ImportError("requests package is not installed") from err
    if name == "AioHttpTransport":
        try:
            from ._aiohttp import AioHttpTransport

            return AioHttpTransport
        except ImportError as err:
            raise ImportError("aiohttp package is not installed") from err
    if name == "AioHttpTransportResponse":
        try:
            from ._aiohttp import AioHttpTransportResponse

            return AioHttpTransportResponse
        except ImportError as err:
            raise ImportError("aiohttp package is not installed") from err
    if name == "TrioRequestsTransport":
        try:
            from ._requests_trio import TrioRequestsTransport

            return TrioRequestsTransport
        except ImportError as ex:
            if ex.msg.endswith("'requests'"):
                raise ImportError("requests package is not installed") from ex
            raise ImportError("trio package is not installed") from ex
    if name == "TrioRequestsTransportResponse":
        try:
            from ._requests_trio import TrioRequestsTransportResponse

            return TrioRequestsTransportResponse
        except ImportError as err:
            raise ImportError("trio package is not installed") from err
    raise AttributeError(f"module 'azure.core.pipeline.transport' has no attribute {name}")
