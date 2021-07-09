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
import logging
from typing import Iterator, Optional, ContextManager, AsyncIterator as AsyncIteratorType, Any, Union
from collections.abc import AsyncIterator
import httpx
import urllib3
from ._base import HttpResponse, HttpTransport, HttpRequest, _HttpResponseBase
from ._base_async import AsyncHttpResponse, AsyncHttpTransport
from ...exceptions import DecodeError, ServiceRequestError, ServiceResponseError
from ...configuration import ConnectionConfiguration

_LOGGER = logging.getLogger(__name__)

class _HttpXTransportResponseBase(_HttpResponseBase):
    """Base class for accessing response data.
    :param HttpRequest request: The request.
    :param httpx_response: The object returned from the HTTP library.
    :param int block_size: Size in bytes.
    """
    def __init__(self,
                 request: HttpRequest,
                 httpx_response: httpx.Response,
                 *,
                 stream_contextmanager: Optional[ContextManager] = None,
                 block_size: Optional[int] = None
                 ):
        super(_HttpXTransportResponseBase, self).__init__(request, httpx_response, block_size=block_size)
        self.status_code = httpx_response.status_code
        self.headers = httpx_response.headers
        self.reason = httpx_response.reason_phrase
        self.content_type = httpx_response.headers.get('content-type')
        self.stream_contextmanager = stream_contextmanager

    def body(self):
        return self.internal_response.content

    def text(self, encoding=None):
        # type: (Optional[str]) -> str
        """Return the whole body as a string.
        If encoding is not provided, mostly rely on httpx auto-detection, except
        for BOM, that httpx ignores. If we see a UTF8 BOM, we assumes UTF8 unlike httpx.
        :param str encoding: The encoding to apply.
        """
        if not encoding:
            # There is a few situation where "httpx" magic doesn't fit us:
            # - https://github.com/psf/httpx/issues/654
            # - https://github.com/psf/httpx/issues/1737
            # - https://github.com/psf/httpx/issues/2086
            from codecs import BOM_UTF8
            if self.internal_response.content[:3] == BOM_UTF8:
                encoding = "utf-8-sig"

        if encoding:
            if encoding == "utf-8":
                encoding = "utf-8-sig"

            self.internal_response.encoding = encoding

        return self.internal_response.text

class HttpXTransportResponse(HttpResponse, _HttpXTransportResponseBase):
    """Streaming of data from the response."""
    def stream_download(self, pipeline, **kwargs) -> Iterator[bytes]:
        return HttpxStreamDownloadGenerator(pipeline, self, **kwargs)

class HttpxStreamDownloadGenerator(object):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """
    def __init__(self, pipeline, response, **kwargs):
        self.pipeline = pipeline
        self.response = response
        decompress = kwargs.pop("decompress", True)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        if decompress:
            self.iter_bytes_func = self.response.internal_response.iter_bytes()
        else:
            self.iter_bytes_func = self.response.internal_response.iter_raw()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.iter_bytes_func)
        except StopIteration:
            self.response.stream_contextmanager.__exit__(None, None, None)
            raise
        except httpx.DecodingError as ex:
            if len(ex.args) > 0:
                raise DecodeError(ex.args[0])
            raise DecodeError("Fail to decode.")

class HttpXTransport(HttpTransport):
    """Implements a HTTPX sender.
    :keyword httpx.Client client: Request client to use instead of the default one.
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_httpx.py
            :start-after: [START httpx]
            :end-before: [END httpx]
            :language: python
            :dedent: 4
            :caption: Synchronous transport with HTTPX.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self.client = kwargs.get('client', None)  # type: Optional[httpx.Client]
        self._client_owner = kwargs.get('client_owner', True)
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop('use_env_settings', True)

    def open(self):
        if not self.client and self._client_owner:
            self.client = httpx.Client(
                trust_env=self._use_env_settings,
                verify=self.connection_config.verify,
                cert=self.connection_config.cert,
            )

    def close(self):
        if self._client_owner and self.client:
            self.client.close()
            self.client = None

    def __enter__(self) -> "HttpXTransport":
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def send(self, request: HttpRequest, **kwargs) -> HttpXTransportResponse:
        """Send request object according to configuration.
        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HttpXTransportResponse object.
        :rtype: ~azure.core.pipeline.transport.HttpXTransportResponse
        """
        self.open()
        response = None
        error = None  # type: Optional[Union[ServiceRequestError, ServiceResponseError]]

        try:
            stream_response = kwargs.pop("stream", False)
            connection_timeout = kwargs.pop('connection_timeout', self.connection_config.timeout)

            if isinstance(connection_timeout, tuple):
                if 'read_timeout' in kwargs:
                    raise ValueError('Cannot set tuple connection_timeout and read_timeout together')
                _LOGGER.warning("Tuple timeout setting is deprecated")
                timeout = connection_timeout
            else:
                read_timeout = kwargs.pop('read_timeout', self.connection_config.read_timeout)
                timeout = (connection_timeout, read_timeout)

            parameters = {
                "method": request.method,
                "url": request.url,
                "headers": request.headers.items(),
                "data": request.data,
                "files": request.files,
                "allow_redirects": False,
                "timeout": timeout,
                **kwargs
            }

            stream_ctx = None  # type: Optional[ContextManager]
            if stream_response:
                stream_ctx = self.client.stream(**parameters)   # type: ignore
                response = stream_ctx.__enter__()
            else:
                response = self.client.request(**parameters)    # type: ignore

        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.ConnectTimeoutError) as err:
            error = ServiceRequestError(err, error=err)
        except httpx.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except httpx.ConnectError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except httpx.HTTPError as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error

        return HttpXTransportResponse(
            request,
            response,
            stream_contextmanager=stream_ctx,
        )


class AsyncHttpXTransportResponse(AsyncHttpResponse, _HttpXTransportResponseBase):
    def stream_download(self, pipeline, **kwargs) -> AsyncIteratorType[bytes]:
        return AsyncHttpxStreamDownloadGenerator(pipeline, self, **kwargs)

class AsyncHttpxStreamDownloadGenerator(AsyncIterator):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """
    def __init__(self, pipeline, response, **kwargs):
        self.pipeline = pipeline
        self.response = response
        decompress = kwargs.pop("decompress", True)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        if decompress:
            self.iter_bytes_func = self.response.internal_response.aiter_bytes()
        else:
            self.iter_bytes_func = self.response.internal_response.aiter_raw()

    async def __anext__(self):
        try:
            return await self.iter_bytes_func.__anext__()
        except StopAsyncIteration:
            await self.response.stream_contextmanager.__aexit__(None, None, None)
            raise
        except httpx.DecodingError as ex:
            if len(ex.args) > 0:
                raise DecodeError(ex.args[0])
            raise DecodeError("Fail to decode.")

class AsyncHttpXTransport(AsyncHttpTransport):
    """Implements a HTTPX sender.
    :keyword httpx.Client client: Request client to use instead of the default one.
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_httpx.py
            :start-after: [START httpx]
            :end-before: [END httpx]
            :language: python
            :dedent: 4
            :caption: Synchronous transport with HTTPX.
    """

    def __init__(self, **kwargs):
        self.client = kwargs.get('client', None)  # type: Optional[httpx.AsyncClient]
        self._client_owner = kwargs.get('client_owner', True)
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop('use_env_settings', True)

    async def open(self):
        if not self.client and self._client_owner:
            self.client = httpx.AsyncClient(
                trust_env=self._use_env_settings,
                verify=self.connection_config.verify,
                cert=self.connection_config.cert,
            )

    async def close(self):
        if self._client_owner and self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self) -> "AsyncHttpXTransport":
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def send(self, request: HttpRequest, **kwargs) -> AsyncHttpXTransportResponse:
        """Send request object according to configuration.
        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An AsyncHttpXTransportResponse object.
        :rtype: ~azure.core.pipeline.transport.AsyncHttpXTransportResponse
        """
        await self.open()
        response = None
        error = None  # type: Optional[Union[ServiceRequestError, ServiceResponseError]]

        try:
            stream_response = kwargs.pop("stream", False)
            parameters = {
                "method": request.method,
                "url": request.url,
                "headers": request.headers.items(),
                "data": request.data,
                "files": request.files,
                "allow_redirects": False,
                **kwargs
            }

            stream_ctx = None
            if stream_response:
                stream_ctx = self.client.stream(**parameters)   # type: ignore
                response = await stream_ctx.__aenter__()
            else:
                response = await self.client.request(**parameters)  # type: ignore
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.ConnectTimeoutError) as err:
            error = ServiceRequestError(err, error=err)
        except httpx.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except httpx.ConnectError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except httpx.HTTPError as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error
        return AsyncHttpXTransportResponse(
            request,
            response,
            stream_contextmanager=stream_ctx,
        )
