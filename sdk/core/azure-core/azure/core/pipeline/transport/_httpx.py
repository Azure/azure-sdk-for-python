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
from __future__ import absolute_import
import logging
from typing import Iterator, Optional, Any, Union, TypeVar, ContextManager
import time
import urllib3 # type: ignore
from urllib3.util.retry import Retry # type: ignore
import httpx

from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError
)
from . import HttpRequest # pylint: disable=unused-import

from ._base import (
    HttpTransport,
    HttpResponse,
    _HttpResponseBase
)

PipelineType = TypeVar("PipelineType")

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
            stream_contextmanager: Optional[ContextManager]=None,
            block_size: Optional[int]=None
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


class StreamDownloadGenerator(object):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    """
    def __init__(self, pipeline, response):
        self.pipeline = pipeline
        self.request = response.request
        self.response = response
        self.block_size = response.block_size
        # httpx does not support yet chunk_size
        # https://github.com/encode/httpx/issues/394
        self.iter_bytes_func = self.response.internal_response.iter_bytes()
        self.content_length = int(response.headers.get('Content-Length', 0))
        self.downloaded = 0

    def __len__(self):
        return self.content_length

    def __iter__(self):
        return self

    def __next__(self):
        retry_active = True
        retry_total = 3
        retry_interval = 1000
        while retry_active:
            try:
                chunk = next(self.iter_bytes_func)
                if not chunk:
                    raise StopIteration()
                self.downloaded += self.block_size
                return chunk
            except StopIteration:
                self.response.stream_contextmanager.__exit__()
                raise StopIteration()
            except (httpx.ChunkedEncodingError,
                    httpx.ConnectionError):
                retry_total -= 1
                if retry_total <= 0:
                    retry_active = False
                else:
                    time.sleep(retry_interval)
                    headers = {'range': 'bytes=' + str(self.downloaded) + '-'}
                    resp = self.pipeline.run(self.request, stream=True, headers=headers)
                    if resp.http_response.status_code == 416:
                        raise
                    chunk = next(self.iter_bytes_func)
                    if not chunk:
                        raise StopIteration()
                    self.downloaded += len(chunk)
                    return chunk
                continue
            except httpx.StreamConsumedError:
                raise
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.internal_response.close()
                raise


class HttpXTransportResponse(HttpResponse, _HttpXTransportResponseBase):
    """Streaming of data from the response.
    """
    def stream_download(self, pipeline):
        # type: (PipelineType) -> Iterator[bytes]
        """Generator for streaming request body data."""
        return StreamDownloadGenerator(pipeline, self)


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

    _protocols = ['http://', 'https://']

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.client = kwargs.get('client', None)  # type: Optional[httpx.Client]
        self._client_owner = kwargs.get('client_owner', True)
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop('use_env_settings', True)

    def __enter__(self):
        # type: () -> HttpXTransport
        self.open()
        return self

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        self.close()

    def _init_client(self, client):
        # type: (httpx.Client) -> None
        """Init client level configuration of httpx.

        This is initialization I want to do once only on a client.
        """
        disable_retries = Retry(total=False, redirect=False, raise_on_status=False)
        adapter = httpx.adapters.HTTPAdapter(max_retries=disable_retries)
        for p in self._protocols:
            client.mount(p, adapter)

    def open(self):
        if not self.client and self._client_owner:
            self.client = httpx.Client(
                trust_env=self._use_env_settings,
                verify=self.connection_config.verify,
                cert=self.connection_config.cert,
            )
            # self._init_client(self.client)

    def close(self):
        if self._client_owner and self.client:
            self.client.close()
            self._client_owner = False
            self.client = None

    def send(self, request, **kwargs): # type: ignore
        # type: (HttpRequest, Any) -> HttpResponse
        """Send request object according to configuration.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse

        :keyword httpx.Client client: will override the driver client and use yours.
         Should NOT be done unless really required. Anything else is sent straight to httpx.
        :keyword dict proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """
        self.open()
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]

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
                "timeout": timeout,
                "allow_redirects": False,
                **kwargs
            }

            stream_ctx = None  # type: Optional[ContextManager]
            if stream_response:
                stream_ctx = self.client.stream(**parameters)
                response = stream_ctx.__enter__()
            else:
                response = self.client.request(**parameters)

        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.ConnectTimeoutError) as err:
            error = ServiceRequestError(err, error=err)
        except httpx.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except httpx._exceptions.ConnectError as err:  # https://github.com/encode/httpx/pull/1045
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
            block_size=self.connection_config.data_block_size
        )
