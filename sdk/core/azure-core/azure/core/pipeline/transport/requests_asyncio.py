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
from .base import HttpRequest
from .base_async import (
    AsyncHttpTransport,
    AsyncHttpResponse,
    _ResponseStopIteration,
    _iterate_response_content)
from .requests_basic import RequestsTransport, RequestsTransportResponse


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
class AsyncioRequestsTransport(RequestsTransport, AsyncHttpTransport):  # type: ignore
    """Identical implementation as the synchronous RequestsTransport wrapped in a class with
     asynchronous methods. Uses the built-in asyncio event loop.
    """
    async def __aenter__(self):
        return super(AsyncioRequestsTransport, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(AsyncioRequestsTransport, self).__exit__()

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponse:  # type: ignore
        """Send the request using this HTTP sender.

        :param request: The HttpRequest
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :param kwargs: Any keyword arguments
        :return: The AsyncHttpResponse
        :rtype: ~azure.core.pipeline.transport.AsyncHttpResponse
        """
        self.open()
        loop = kwargs.get("loop", _get_running_loop())
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]
        if self.config.proxy_policy and 'proxies' not in kwargs:
            kwargs['proxies'] = self.config.proxy_policy.proxies
        try:
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.session.request, # type: ignore
                    request.method,
                    request.url,
                    headers=request.headers,
                    data=request.data,
                    files=request.files,
                    verify=kwargs.get('connection_verify', self.config.connection.verify),
                    timeout=kwargs.get('connection_timeout', self.config.connection.timeout),
                    cert=kwargs.get('connection_cert', self.config.connection.cert),
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

        return AsyncioRequestsTransportResponse(request, response, self.config.connection.data_block_size)


class AsyncioStreamDownloadGenerator(AsyncIterator):
    """Streams the response body data.

    :param pipeline: The pipeline object
    :param request: The request object
    :param response: The response object.
    :param int block_size: block size of data sent over connection.
    :param generator iter_content_func: Iterator for response data.
    :param int content_length: size of body in bytes.
    """
    def __init__(self, pipeline: Pipeline, request: HttpRequest, response: requests.Response, block_size: int) -> None:
        self.pipeline = pipeline
        self.request = request
        self.response = response
        self.block_size = block_size
        self.iter_content_func = self.response.iter_content(self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))
        self.downloaded = 0

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        loop = _get_running_loop()
        retry_active = True
        retry_total = 3
        retry_interval = 1000
        while retry_active:
            try:
                chunk = await loop.run_in_executor(
                    None,
                    _iterate_response_content,
                    self.iter_content_func,
                )
                if not chunk:
                    raise _ResponseStopIteration()
                self.downloaded += self.block_size
                return chunk
            except _ResponseStopIteration:
                self.response.close()
                raise StopAsyncIteration()
            except (requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ConnectionError):
                retry_total -= 1
                if retry_total <= 0:
                    retry_active = False
                else:
                    await asyncio.sleep(retry_interval)
                    headers = {'range': 'bytes=' + self.downloaded + '-'}
                    resp = self.pipeline.run(self.request, stream=True, headers=headers)
                    if resp.status_code == 416:
                        raise
                    chunk = await loop.run_in_executor(
                        None,
                        _iterate_response_content,
                        self.iter_content_func,
                    )
                    if not chunk:
                        raise StopIteration()
                    self.downloaded += chunk
                    return chunk
                continue
            except requests.exceptions.StreamConsumedError:
                raise
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.close()
                raise


class AsyncioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse): # type: ignore
    """Asynchronous streaming of data from the response.
    """
    def stream_download(self, pipeline) -> AsyncIteratorType[bytes]: # type: ignore
        """Generator for streaming request body data."""
        return AsyncioStreamDownloadGenerator(pipeline, self.request,
                                              self.internal_response, self.block_size) # type: ignore
