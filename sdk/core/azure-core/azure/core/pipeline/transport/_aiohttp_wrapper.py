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
from typing import TYPE_CHECKING
from azure.core.configuration import ConnectionConfiguration
from ._base_async import AsyncHttpTransport, AsyncHttpResponse

if TYPE_CHECKING:
    from ._base import HttpRequest
    import aiohttp

class AioHttpTransport(AsyncHttpTransport):
    """AioHttp HTTP sender implementation.

    Fully asynchronous implementation using the aiohttp library.

    :param session: The client session.
    :param loop: The event loop.
    :param bool session_owner: Session owner. Defaults True.

    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_async.py
            :start-after: [START aiohttp]
            :end-before: [END aiohttp]
            :language: python
            :dedent: 4
            :caption: Asynchronous transport with aiohttp.
    """
    def __init__(self, *, session=None, loop=None, session_owner=True, **kwargs):
        self._loop = loop
        self._session_owner = session_owner
        self.session = session
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop('use_env_settings', True)

    def __new__(cls, session=None, loop=None, session_owner=True, **kwargs):
        try:
            from .aiohttp import AioHttpTransport as _AioHttpTransport
            return _AioHttpTransport(session=session, loop=loop, session_owner=session_owner, **kwargs)
        except ImportError:
            raise ImportError("aiohttp package is not installed")

class AioHttpTransportResponse(AsyncHttpResponse):
    """Methods for accessing response body data.

    :param request: The HttpRequest object
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param aiohttp_response: Returned from ClientSession.request().
    :type aiohttp_response: aiohttp.ClientResponse object
    :param block_size: block size of data sent over connection.
    :type block_size: int
    """
    def __init__(self, request: HttpRequest, aiohttp_response: aiohttp.ClientResponse, block_size=None) -> None:
        super(AioHttpTransportResponse, self).__init__(request, aiohttp_response, block_size=block_size)
        # https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse
        self.status_code = aiohttp_response.status
        self.headers = CIMultiDict(aiohttp_response.headers)
        self.reason = aiohttp_response.reason
        self.content_type = aiohttp_response.headers.get('content-type')
        self._body = None

    def __new__(cls, request, aiohttp_response, block_size=None):
        # type: (HttpRequest, aiohttp.ClientResponse, Optional[int]) -> AioHttpTransportResponse
        try:
            from .aiohttp import AioHttpTransportResponse as _AioHttpTransportResponse
            return _AioHttpTransportResponse(request=request, aiohttp_response=aiohttp_response, block_size=block_size)
        except ImportError:
            raise ImportError("aiohttp package is not installed")
