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
from typing import Any, Optional, cast

import httpx
from .._base import _create_connection_config, _handle_non_stream_rest_response
from .._base_async import _handle_non_stream_rest_response as _handle_non_stream_rest_response_async
from ...exceptions import ServiceRequestError, ServiceResponseError
from ...rest._httpx import HttpXTransportResponse, AsyncHttpXTransportResponse
from ...transport import HttpTransport, AsyncHttpTransport
from ...rest import HttpRequest, HttpResponse, AsyncHttpResponse


class HttpXTransport(HttpTransport):
    """Implements a basic httpx HTTP sender

    :keyword httpx.Client client: HTTPX client to use instead of the default one
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    def __init__(
        self,
        *,
        client: Optional[httpx.Client] = None,
        client_owner: bool = True,
        use_env_settings: bool = True,
        **kwargs: Any
    ) -> None:
        self.client = client
        self.connection_config = _create_connection_config(**kwargs)
        self._client_owner = client_owner
        self._use_env_settings = use_env_settings

    def open(self) -> None:
        if self.client is None:
            self.client = httpx.Client(
                trust_env=self._use_env_settings,
                verify=self.connection_config.get("connection_verify", True),
                cert=self.connection_config.get("connection_cert"),
            )

    def close(self) -> None:
        """Close the session.

        :return: None
        :rtype: None
        """
        if self._client_owner and self.client:
            self.client.close()
            self.client = None

    def __enter__(self) -> "HttpXTransport":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def send(self, request: HttpRequest, *, stream: bool = False, **kwargs) -> HttpResponse:
        """Send a request and get back a response.

        :param request: The request object to be sent.
        :type request: ~corehttp.rest.HTTPRequest
        :keyword bool stream: Whether to stream the response. Defaults to False.
        :return: An HTTPResponse object.
        :rtype: ~corehttp.rest.HttpResponse
        """
        self.open()
        connect_timeout = kwargs.pop("connection_timeout", self.connection_config.get("connection_timeout"))
        read_timeout = kwargs.pop("read_timeout", self.connection_config.get("read_timeout"))
        # not needed here as its already handled during init
        kwargs.pop("connection_verify", None)

        timeout = httpx.Timeout(connect_timeout, read=read_timeout)
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request._data,  # pylint: disable=protected-access
            "files": request._files,  # pylint: disable=protected-access
            "timeout": timeout,
            **kwargs,
        }

        response = None

        # Cast for typing since we know it's not None after the open call
        client = cast(httpx.Client, self.client)
        try:
            if stream:
                req = client.build_request(**parameters)
                response = client.send(req, stream=stream)
            else:
                response = client.request(**parameters)
        except (httpx.ReadTimeout, httpx.ProtocolError) as err:
            raise ServiceResponseError(err, error=err) from err
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err) from err

        retval = HttpXTransportResponse(request, response)
        if not stream:
            _handle_non_stream_rest_response(retval)
        return retval


class AsyncHttpXTransport(AsyncHttpTransport):
    """Implements a basic async httpx HTTP sender

    :keyword httpx.AsyncClient client: HTTPX client to use instead of the default one
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    def __init__(
        self,
        *,
        client: Optional[httpx.AsyncClient] = None,
        client_owner: bool = True,
        use_env_settings: bool = True,
        **kwargs: Any
    ) -> None:
        self.client = client
        self.connection_config = _create_connection_config(**kwargs)
        self._client_owner = client_owner
        self._use_env_settings = use_env_settings

    async def open(self) -> None:
        if self.client is None:
            self.client = httpx.AsyncClient(
                trust_env=self._use_env_settings,
                verify=self.connection_config.get("connection_verify", True),
                cert=self.connection_config.get("connection_cert"),
            )

    async def close(self) -> None:
        if self._client_owner and self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self) -> "AsyncHttpXTransport":
        await self.open()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def send(self, request: HttpRequest, *, stream: bool = False, **kwargs) -> AsyncHttpResponse:
        """Send the request using this HTTP sender.

        :param request: The request object to be sent.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether to stream the response. Defaults to False.
        :return: The response object.
        :rtype: ~corehttp.rest.AsyncHttpResponse
        """
        await self.open()
        connect_timeout = kwargs.pop("connection_timeout", self.connection_config.get("connection_timeout"))
        read_timeout = kwargs.pop("read_timeout", self.connection_config.get("read_timeout"))
        # not needed here as its already handled during init
        kwargs.pop("connection_verify", None)
        timeout = httpx.Timeout(connect_timeout, read=read_timeout)
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request._data,  # pylint: disable=protected-access
            "files": request._files,  # pylint: disable=protected-access
            "timeout": timeout,
            **kwargs,
        }

        response = None
        client = cast(httpx.AsyncClient, self.client)
        try:
            if stream:
                req = client.build_request(**parameters)
                response = await client.send(req, stream=stream)
            else:
                response = await client.request(**parameters)
        except (httpx.ReadTimeout, httpx.ProtocolError) as err:
            raise ServiceResponseError(err, error=err) from err
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err) from err

        retval = AsyncHttpXTransportResponse(request, response)
        if not stream:
            await _handle_non_stream_rest_response_async(retval)
        return retval
