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
from typing import AsyncIterator

import httpx
from ..exceptions import DecodeError, IncompleteReadError
from ._http_response_impl import HttpResponseImpl
from ._http_response_impl_async import AsyncHttpResponseImpl
from ..rest import HttpRequest
from ..runtime.pipeline import Pipeline

_LOGGER = logging.getLogger(__name__)


class HttpXTransportResponse(HttpResponseImpl):
    """HttpX response implementation.

    :param request: The request sent to the server
    :type request: ~corehttp.rest.HTTPRequest
    :param httpx.Response httpx_response: The response object returned from the HttpX library
    """

    def __init__(
        self,
        request: HttpRequest,
        httpx_response: httpx.Response,
    ) -> None:
        super().__init__(
            request=request,
            internal_response=httpx_response,
            status_code=httpx_response.status_code,
            headers=httpx_response.headers,
            reason=httpx_response.reason_phrase,
            content_type=httpx_response.headers.get("content-type"),
            stream_download_generator=HttpXStreamDownloadGenerator,
        )


# pylint: disable=unused-argument
class HttpXStreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~corehttp.runtime.pipeline.Pipeline
    :param response: The response object.
    :type response: HttpXTransportResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self, pipeline: Pipeline, response: HttpXTransportResponse, *, decompress: bool = True, **kwargs
    ) -> None:

        self.pipeline = pipeline
        self.response = response
        should_decompress = decompress

        if should_decompress:
            self.iter_content_func = self.response._internal_response.iter_bytes()
        else:
            self.iter_content_func = self.response._internal_response.iter_raw()

    def __iter__(self) -> "HttpXStreamDownloadGenerator":
        return self

    def __next__(self):
        internal_response = self.response._internal_response  # pylint: disable=protected-access
        try:
            return next(self.iter_content_func)
        except StopIteration:
            internal_response.close()
            raise
        except httpx.RemoteProtocolError as ex:
            _LOGGER.warning("Incomplete download: %s", ex)
            internal_response.close()
            raise IncompleteReadError(ex, error=ex) from ex
        except httpx.DecodingError as ex:
            if len(ex.args) > 0:
                raise DecodeError(ex.args[0]) from ex
            raise DecodeError("Failed to decode.") from ex
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.close()
            raise


class AsyncHttpXTransportResponse(AsyncHttpResponseImpl):
    """Async HttpX response implementation.

    :param request: The request sent to the server
    :type request: ~corehttp.rest.HTTPRequest
    :param httpx.Response httpx_response: The response object returned from HttpX library
    """

    def __init__(
        self,
        request: HttpRequest,
        httpx_response: httpx.Response,
    ) -> None:
        super().__init__(
            request=request,
            internal_response=httpx_response,
            status_code=httpx_response.status_code,
            headers=httpx_response.headers,
            reason=httpx_response.reason_phrase,
            content_type=httpx_response.headers.get("content-type"),
            stream_download_generator=AsyncHttpXStreamDownloadGenerator,
        )

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        if not self.is_closed:
            self._is_closed = True
            await self._internal_response.aclose()


# pylint: disable=unused-argument
class AsyncHttpXStreamDownloadGenerator(AsyncIterator):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~corehttp.runtime.pipeline.Pipeline
    :param response: The response object.
    :type response: AsyncHttpXTransportResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self, pipeline: Pipeline, response: AsyncHttpXTransportResponse, *, decompress: bool = True, **kwargs
    ) -> None:
        self.pipeline = pipeline
        self.response = response
        should_decompress = decompress

        if should_decompress:
            self.iter_content_func = self.response._internal_response.aiter_bytes()
        else:
            self.iter_content_func = self.response._internal_response.aiter_raw()

    async def __len__(self) -> int:
        return self.response._internal_response.headers["content-length"]

    def __aiter__(self) -> "AsyncHttpXStreamDownloadGenerator":
        return self

    async def __anext__(self):
        internal_response = self.response._internal_response  # pylint: disable=protected-access
        try:
            return await self.iter_content_func.__anext__()
        except StopAsyncIteration:
            await internal_response.aclose()
            raise
        except httpx.RemoteProtocolError as ex:
            _LOGGER.warning("Incomplete download: %s", ex)
            internal_response.aclose()
            raise IncompleteReadError(ex, error=ex) from ex
        except httpx.DecodingError as ex:
            if len(ex.args) > 1:
                raise DecodeError(ex.args[0]) from ex
            raise DecodeError("Failed to decode.") from ex
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.aclose()
            raise
