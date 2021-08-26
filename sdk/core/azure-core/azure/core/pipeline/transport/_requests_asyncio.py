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
import asyncio
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Union, Optional, AsyncIterator as AsyncIteratorType
import urllib3 # type: ignore

import requests

from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError
)
from azure.core.pipeline import Pipeline
from ._base_async import (
    AsyncHttpResponse,
    _ResponseStopIteration,
    _iterate_response_content)
from ._requests_basic import (
    _RestRequestsTransportResponseBase,
    RequestsTransportResponse,
    _read_raw_stream,
    _has_content,
)
from ._base_requests_async import RequestsAsyncTransportBase
from .._tools import get_block_size as _get_block_size, get_internal_response as _get_internal_response

from .._tools_async import read_in_response as _read_in_response
from ...rest import HttpRequest, AsyncHttpResponse as RestAsyncHttpResponse
from ...rest._helpers_py3 import (
    iter_raw_helper as _iter_raw_helper,
    iter_bytes_helper as _iter_bytes_helper,
)

_LOGGER = logging.getLogger(__name__)


def _get_running_loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:  # 3.5 / 3.6
        loop = asyncio._get_running_loop()  # pylint: disable=protected-access, no-member
        if loop is None:
            raise RuntimeError('No running event loop')
        return loop


#pylint: disable=too-many-ancestors
class AsyncioRequestsTransport(RequestsAsyncTransportBase):
    """Identical implementation as the synchronous RequestsTransport wrapped in a class with
    asynchronous methods. Uses the built-in asyncio event loop.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_async.py
            :start-after: [START asyncio]
            :end-before: [END asyncio]
            :language: python
            :dedent: 4
            :caption: Asynchronous transport with asyncio.
    """
    async def __aenter__(self):
        return super(AsyncioRequestsTransport, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(AsyncioRequestsTransport, self).__exit__()

    async def sleep(self, duration):  # pylint:disable=invalid-overridden-method
        await asyncio.sleep(duration)

    async def send(self, request: HttpRequest, **kwargs: Any) -> RestAsyncHttpResponse:  # type: ignore # pylint:disable=invalid-overridden-method
        """Send the request using this HTTP sender.

        :param request: The HttpRequest
        :type request: ~azure.core.rest.HttpRequest
        :return: The AsyncHttpResponse
        :rtype: ~azure.core.rest.AsyncHttpResponse

        :keyword requests.Session session: will override the driver session and use yours.
         Should NOT be done unless really required. Anything else is sent straight to requests.
        :keyword dict proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """
        self.open()
        loop = kwargs.get("loop", _get_running_loop())
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]
        data_to_send = await self._retrieve_request_data(request)
        try:
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.session.request,
                    request.method,
                    request.url,
                    headers=request.headers,
                    data=data_to_send,
                    files=request.files,
                    verify=kwargs.pop('connection_verify', self.connection_config.verify),
                    timeout=kwargs.pop('connection_timeout', self.connection_config.timeout),
                    cert=kwargs.pop('connection_cert', self.connection_config.cert),
                    allow_redirects=False,
                    **kwargs))

        except urllib3.exceptions.NewConnectionError as err:
            error = ServiceRequestError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error

        retval = RestAsyncioRequestsTransportResponse(
            request=request,
            internal_response=response,
        )
        retval._connection_data_block_size = self.connection_config.data_block_size  # pylint: disable=protected-access
        await _read_in_response(retval, kwargs.get("stream"))
        return retval

class AsyncioStreamDownloadGenerator(AsyncIterator):
    """Streams the response body data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
            on the *content-encoding* header.
    """
    def __init__(self, pipeline: Pipeline, response: AsyncHttpResponse, **kwargs) -> None:
        self.pipeline = pipeline
        self.request = response.request
        self.response = response
        self.block_size = _get_block_size(response)
        decompress = kwargs.pop("decompress", True)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        internal_response = _get_internal_response(response)
        if decompress:
            self.iter_content_func = internal_response.iter_content(self.block_size)
        else:
            self.iter_content_func = _read_raw_stream(internal_response, self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        loop = _get_running_loop()
        internal_response = _get_internal_response(self.response)
        try:
            chunk = await loop.run_in_executor(
                None,
                _iterate_response_content,
                self.iter_content_func,
            )
            if not chunk:
                raise _ResponseStopIteration()
            return chunk
        except _ResponseStopIteration:
            internal_response.close()
            raise StopAsyncIteration()
        except requests.exceptions.StreamConsumedError:
            raise
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.close()
            raise


class AsyncioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse): # type: ignore
    """Asynchronous streaming of data from the response.
    """
    def stream_download(self, pipeline, **kwargs) -> AsyncIteratorType[bytes]: # type: ignore
        """Generator for streaming request body data."""
        return AsyncioStreamDownloadGenerator(pipeline, self, **kwargs) # type: ignore

##################### REST #####################

class RestAsyncioRequestsTransportResponse(_RestRequestsTransportResponseBase, RestAsyncHttpResponse): # type: ignore
    """Asynchronous streaming of data from the response.
    """

    async def iter_raw(self) -> AsyncIteratorType[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """

        async for part in _iter_raw_helper(AsyncioStreamDownloadGenerator, self):
            yield part
        await self.close()

    async def iter_bytes(self) -> AsyncIteratorType[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in _iter_bytes_helper(
            AsyncioStreamDownloadGenerator,
            self,
            content=self.content if _has_content(self) else None
        ):
            yield part
        await self.close()

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self.is_closed = True
        self._internal_response.close()
        await asyncio.sleep(0)

    async def read(self) -> bytes:
        """Read the response's bytes into memory.

        :return: The response's bytes
        :rtype: bytes
        """
        if not _has_content(self):
            parts = []
            async for part in self.iter_bytes():  # type: ignore
                parts.append(part)
            self._internal_response._content = b"".join(parts)  # pylint: disable=protected-access
        return self.content
