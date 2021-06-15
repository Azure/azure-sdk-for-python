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
from typing import Any, Optional, AsyncIterator as AsyncIteratorType
from collections.abc import AsyncIterator
try:
    import cchardet as chardet
except ImportError:  # pragma: no cover
    import chardet  # type: ignore

import logging
import asyncio
import codecs
import aiohttp
from multidict import CIMultiDict
from requests.exceptions import StreamConsumedError as RequestsStreamConsumedError

from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline import Pipeline

from ._base_async import (
    AsyncHttpTransport,
    _ResponseStopIteration)
from ...rest import AsyncHttpResponse, ResponseClosedError, StreamConsumedError, HttpRequest

# Matching requests, because why not?
CONTENT_CHUNK_SIZE = 10 * 1024
_LOGGER = logging.getLogger(__name__)

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
    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None, loop=None, session_owner=True, **kwargs):
        self._loop = loop
        self._session_owner = session_owner
        self.session = session
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop('use_env_settings', True)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        await self.close()

    async def open(self):
        """Opens the connection.
        """
        if not self.session and self._session_owner:
            jar = aiohttp.DummyCookieJar()
            self.session = aiohttp.ClientSession(
                loop=self._loop,
                trust_env=self._use_env_settings,
                cookie_jar=jar,
                auto_decompress=False,
            )
        if self.session is not None:
            await self.session.__aenter__()

    async def close(self):
        """Closes the connection.
        """
        if self._session_owner and self.session:
            await self.session.close()
            self._session_owner = False
            self.session = None

    def _build_ssl_config(self, cert, verify):  # pylint: disable=no-self-use
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

    def _get_request_data(self, request): #pylint: disable=no-self-use
        if request._files:
            form_data = aiohttp.FormData()
            for form_file, data in request._files.items():
                content_type = data[2] if len(data) > 2 else None
                try:
                    form_data.add_field(form_file, data[1], filename=data[0], content_type=content_type)
                except IndexError:
                    raise ValueError("Invalid formdata formatting: {}".format(data))
            return form_data
        return request._data

    async def send(self, request: HttpRequest, **config: Any) -> Optional[AsyncHttpResponse]:
        """Send the request using this HTTP sender.

        Will pre-load the body into memory to be available with a sync method.
        Pass stream=True to avoid this behavior.

        :param request: The HttpRequest object
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :param config: Any keyword arguments
        :return: The AsyncHttpResponse
        :rtype: ~azure.core.pipeline.transport.AsyncHttpResponse

        :keyword bool stream: Defaults to False.
        :keyword dict proxies: dict of proxy to used based on protocol. Proxy is a dict (protocol, url)
        :keyword str proxy: will define the proxy to use all the time
        """
        await self.open()
        try:
            auto_decompress = self.session.auto_decompress  # type: ignore
        except AttributeError:
            # auto_decompress is introduced in aiohttp 3.7. We need this to handle Python 3.6.
            auto_decompress = False

        proxies = config.pop('proxies', None)
        if proxies and 'proxy' not in config:
            # aiohttp needs a single proxy, so iterating until we found the right protocol

            # Sort by longest string first, so "http" is not used for "https" ;-)
            for protocol in sorted(proxies.keys(), reverse=True):
                if request.url.startswith(protocol):
                    config['proxy'] = proxies[protocol]
                    break

        response = None
        config['ssl'] = self._build_ssl_config(
            cert=config.pop('connection_cert', self.connection_config.cert),
            verify=config.pop('connection_verify', self.connection_config.verify)
        )
        # If we know for sure there is not body, disable "auto content type"
        # Otherwise, aiohttp will send "application/octect-stream" even for empty POST request
        # and that break services like storage signature
        if not request._data and not request._files:
            config['skip_auto_headers'] = ['Content-Type']
        try:
            stream_response = config.pop("stream", False)
            timeout = config.pop('connection_timeout', self.connection_config.timeout)
            read_timeout = config.pop('read_timeout', self.connection_config.read_timeout)
            socket_timeout = aiohttp.ClientTimeout(sock_connect=timeout, sock_read=read_timeout)
            result = await self.session.request(    # type: ignore
                request.method,
                request.url,
                headers=request.headers,
                data=self._get_request_data(request),
                timeout=socket_timeout,
                allow_redirects=False,
                **config
            )
            response = AioHttpTransportResponse(request=request, internal_response=result)
            response._connection_data_block_size = self.connection_config.data_block_size
            if not stream_response:
                await response.read()
                await response.close()
        except aiohttp.client_exceptions.ClientResponseError as err:
            raise ServiceResponseError(err, error=err) from err
        except aiohttp.client_exceptions.ClientError as err:
            raise ServiceRequestError(err, error=err) from err
        except asyncio.TimeoutError as err:
            raise ServiceResponseError(err, error=err) from err
        return response

class AioHttpStreamDownloadGenerator(AsyncIterator):
    """Streams the response body data.

    :param pipeline: The pipeline object
    :param response: The client response object.
    :param bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """
    def __init__(
        self, pipeline: Pipeline, response: AsyncHttpResponse, *, decompress=True, chunk_size: int = None
    ) -> None:
        self.pipeline = pipeline
        self.request = response.request
        self.response = response
        self.block_size = chunk_size or response._connection_data_block_size
        self._decompress = decompress
        self.content_length = int(response.internal_response.headers.get('Content-Length', 0))
        self._decompressor = None

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        try:
            chunk = await self.response.internal_response.content.read(self.block_size)
            if not chunk:
                raise _ResponseStopIteration()
            if not self._decompress:
                return chunk
            enc = self.response.internal_response.headers.get('Content-Encoding')
            if not enc:
                return chunk
            enc = enc.lower()
            if enc in ("gzip", "deflate"):
                if not self._decompressor:
                    import zlib
                    zlib_mode = 16 + zlib.MAX_WBITS if enc == "gzip" else zlib.MAX_WBITS
                    self._decompressor = zlib.decompressobj(wbits=zlib_mode)
                chunk = self._decompressor.decompress(chunk)
            return chunk
        except _ResponseStopIteration:
            self.response.internal_response.close()
            raise StopAsyncIteration()
        except RequestsStreamConsumedError:
            raise
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.internal_response.close()
            raise

class AioHttpTransportResponse(AsyncHttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        internal_response,
        **kwargs
    ):
        super().__init__(request=request, internal_response=internal_response, **kwargs)
        self.status_code = internal_response.status
        self.headers = CIMultiDict(internal_response.headers)
        self.reason = internal_response.reason
        self.content_type = internal_response.headers.get('content-type')
        self._content = None

    @property
    def text(self) -> str:
        content = self.content
        encoding = self.encoding
        ctype = self.headers.get(aiohttp.hdrs.CONTENT_TYPE, "").lower()
        mimetype = aiohttp.helpers.parse_mimetype(ctype)

        encoding = mimetype.parameters.get("charset")
        if encoding:
            try:
                codecs.lookup(encoding)
            except LookupError:
                encoding = None
        if not encoding:
            if mimetype.type == "application" and (
                    mimetype.subtype == "json" or mimetype.subtype == "rdap"
            ):
                # RFC 7159 states that the default encoding is UTF-8.
                # RFC 7483 defines application/rdap+json
                encoding = "utf-8"
            elif content is None:
                raise RuntimeError(
                    "Cannot guess the encoding of a not yet read content"
                )
            else:
                encoding = chardet.detect(content)["encoding"]
        if not encoding:
            encoding = "utf-8-sig"

        return content.decode(encoding)

    def _get_content(self):
        """Return the internal response's content"""
        return self._content

    def _set_content(self, val):
        """Set the internal response's content"""
        self._content = val

    def _has_content(self):
        """How to check if your internal response has content"""
        return self._content is not None

    async def _stream_download_helper(self, decompress, chunk_size=None):
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise ResponseClosedError()

        self.is_stream_consumed = True
        stream_download = AioHttpStreamDownloadGenerator(
            pipeline=None,
            response=self,
            chunk_size=chunk_size,
            decompress=decompress,
        )
        async for part in stream_download:
            self._num_bytes_downloaded += len(part)
            yield part

    async def iter_raw(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the raw response bytes
        """
        async for raw_bytes in self._stream_download_helper(decompress=False, chunk_size=chunk_size):
            yield raw_bytes
        await self.close()

    async def iter_bytes(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the bytes in the response stream
        """
        content = self._get_content()
        if content is not None:
            if chunk_size is None:
                chunk_size = len(content)
            for i in range(0, len(content), chunk_size):
                yield content[i: i + chunk_size]
        else:
            async for raw_bytes in self._stream_download_helper(decompress=True, chunk_size=chunk_size):
                yield raw_bytes
        await self.close()

    def __getstate__(self):
        # Be sure body is loaded in memory, otherwise not pickable and let it throw
        # await self.read()

        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state['internal_response'] = None  # aiohttp response are not pickable (see headers comments)
        state['headers'] = CIMultiDict(self.headers)  # MultiDictProxy is not pickable
        return state
