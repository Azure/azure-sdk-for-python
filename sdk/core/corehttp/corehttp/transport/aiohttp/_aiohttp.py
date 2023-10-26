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
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Type, cast
from types import TracebackType

import logging
import asyncio
import aiohttp  # pylint: disable=networking-import-outside-azure-core-transport
import aiohttp.client_exceptions  # pylint: disable=networking-import-outside-azure-core-transport

from ...exceptions import (
    ServiceRequestError,
    ServiceResponseError,
)
from .._base_async import AsyncHttpTransport, _handle_non_stream_rest_response
from .._base import _create_connection_config
from ...rest._aiohttp import RestAioHttpTransportResponse


if TYPE_CHECKING:
    from ...rest import (
        HttpRequest as RestHttpRequest,
        AsyncHttpResponse as RestAsyncHttpResponse,
    )

# Matching requests, because why not?
CONTENT_CHUNK_SIZE = 10 * 1024
_LOGGER = logging.getLogger(__name__)


class AioHttpTransport(AsyncHttpTransport):
    """AioHttp HTTP sender implementation.

    Fully asynchronous implementation using the aiohttp library.

    :keyword session: The client session.
    :paramtype session: ~aiohttp.ClientSession
    :keyword bool session_owner: Session owner. Defaults True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None, session_owner: bool = True, **kwargs):
        self._session_owner = session_owner
        self.session = session
        if not self._session_owner and not self.session:
            raise ValueError("session_owner cannot be False if no session is provided")
        self.connection_config = _create_connection_config(**kwargs)
        self._use_env_settings = kwargs.pop("use_env_settings", True)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.close()

    async def open(self):
        """Opens the connection."""
        if not self.session and self._session_owner:
            jar = aiohttp.DummyCookieJar()
            clientsession_kwargs = {
                "trust_env": self._use_env_settings,
                "cookie_jar": jar,
                "auto_decompress": False,
            }
            self.session = aiohttp.ClientSession(**clientsession_kwargs)
        # pyright has trouble to understand that self.session is not None, since we raised at worst in the init
        self.session = cast(aiohttp.ClientSession, self.session)
        await self.session.__aenter__()

    async def close(self):
        """Closes the connection."""
        if self._session_owner and self.session:
            await self.session.close()
            self._session_owner = False
            self.session = None

    def _build_ssl_config(self, cert, verify):
        """Build the SSL configuration.

        :param tuple cert: Cert information
        :param bool verify: SSL verification or path to CA file or directory
        :rtype: bool or str or :class:`ssl.SSLContext`
        :return: SSL configuration
        """
        ssl_ctx = None

        if cert or verify not in (True, False):
            import ssl

            if verify not in (True, False):
                ssl_ctx = ssl.create_default_context(cafile=verify)
            else:
                ssl_ctx = ssl.create_default_context()
            if cert:
                ssl_ctx.load_cert_chain(*cert)
            return ssl_ctx
        return verify

    def _get_request_data(self, request: RestHttpRequest):
        """Get the request data.

        :param request: The request object
        :type request:  ~corehttp.rest.HttpRequest
        :rtype: bytes or ~aiohttp.FormData
        :return: The request data
        """
        if request._files:  # pylint: disable=protected-access
            form_data = aiohttp.FormData(request._data or {})  # pylint: disable=protected-access
            for form_file, data in request._files.items():  # pylint: disable=protected-access
                content_type = data[2] if len(data) > 2 else None
                try:
                    form_data.add_field(form_file, data[1], filename=data[0], content_type=content_type)
                except IndexError as err:
                    raise ValueError("Invalid formdata formatting: {}".format(data)) from err
            return form_data
        return request.content

    async def send(self, request: RestHttpRequest, **config) -> RestAsyncHttpResponse:
        """Send the request using this HTTP sender.

        Will pre-load the body into memory to be available with a sync method.
        Pass stream=True to avoid this behavior.

        :param request: The HttpRequest object
        :type request: ~corehttp.rest.HttpRequest
        :keyword any config: Any keyword arguments
        :return: The AsyncHttpResponse
        :rtype: ~corehttp.rest.AsyncHttpResponse

        :keyword bool stream: Defaults to False.
        :keyword dict proxies: dict of proxy to used based on protocol. Proxy is a dict (protocol, url)
        :keyword str proxy: will define the proxy to use all the time
        """
        await self.open()
        try:
            auto_decompress = self.session.auto_decompress  # type: ignore
        except AttributeError:
            # auto_decompress is introduced in aiohttp 3.7. We need this to handle aiohttp 3.6-.
            auto_decompress = False

        proxies = config.pop("proxies", None)
        if proxies and "proxy" not in config:
            # aiohttp needs a single proxy, so iterating until we found the right protocol

            # Sort by longest string first, so "http" is not used for "https" ;-)
            for protocol in sorted(proxies.keys(), reverse=True):
                if request.url.startswith(protocol):
                    config["proxy"] = proxies[protocol]
                    break

        response: Optional[RestAsyncHttpResponse] = None
        config["ssl"] = self._build_ssl_config(
            cert=config.pop("connection_cert", self.connection_config.get("cert")),
            verify=config.pop("connection_verify", self.connection_config.get("verify")),
        )
        # If we know for sure there is not body, disable "auto content type"
        # Otherwise, aiohttp will send "application/octet-stream" even for empty POST request
        # and that break services like storage signature
        if not request.content:
            config["skip_auto_headers"] = ["Content-Type"]
        try:
            stream_response = config.pop("stream", False)
            timeout = config.pop("connection_timeout", self.connection_config.get("timeout"))
            read_timeout = config.pop("read_timeout", self.connection_config.get("read_timeout"))
            socket_timeout = aiohttp.ClientTimeout(sock_connect=timeout, sock_read=read_timeout)
            result = await self.session.request(  # type: ignore
                request.method,
                request.url,
                headers=request.headers,
                data=self._get_request_data(request),
                timeout=socket_timeout,
                allow_redirects=False,
                **config,
            )

            response = RestAioHttpTransportResponse(
                request=request,
                internal_response=result,
                block_size=self.connection_config.get("data_block_size"),
                decompress=not auto_decompress,
            )
            if not stream_response:
                await _handle_non_stream_rest_response(response)

        except aiohttp.client_exceptions.ClientResponseError as err:
            raise ServiceResponseError(err, error=err) from err
        except asyncio.TimeoutError as err:
            raise ServiceResponseError(err, error=err) from err
        except aiohttp.client_exceptions.ClientError as err:
            raise ServiceRequestError(err, error=err) from err
        return response
