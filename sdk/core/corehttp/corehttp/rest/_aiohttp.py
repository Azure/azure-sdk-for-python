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
import collections.abc
import asyncio
import logging
from itertools import groupby
from typing import Iterator, cast, TYPE_CHECKING
from multidict import CIMultiDict
import aiohttp.client_exceptions  # pylint: disable=networking-import-outside-azure-core-transport

from ._http_response_impl_async import AsyncHttpResponseImpl
from ..exceptions import (
    ResponseNotReadError,
    ServiceRequestError,
    ServiceResponseError,
    IncompleteReadError,
)
from ..runtime.pipeline import AsyncPipeline
from ..transport._base_async import _ResponseStopIteration

if TYPE_CHECKING:
    from ..rest import HttpRequest, AsyncHttpResponse

_LOGGER = logging.getLogger(__name__)


def _aiohttp_content_helper(response: "RestAioHttpTransportResponse") -> bytes:
    # pylint: disable=protected-access
    """Helper for body method of Aiohttp responses.

    The aiohttp body methods need decompression to work synchronously.

    :param response: The response to decode
    :type response: ~corehttp.rest.RestAioHttpTransportResponse
    :rtype: bytes
    :return: The response's bytes
    """
    if response._content is None:
        raise ValueError("Content is not available. Call async method read, or do your call with stream=False.")
    if not response._decompress:
        return response._content
    if response._decompressed_content:
        return response._content
    enc = response.headers.get("Content-Encoding")
    if not enc:
        return response._content
    enc = enc.lower()
    if enc in ("gzip", "deflate"):
        import zlib

        zlib_mode = (16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS
        decompressor = zlib.decompressobj(wbits=zlib_mode)
        response._content = decompressor.decompress(response._content)
        response._decompressed_content = True
        return response._content
    return response._content


class _ItemsView(collections.abc.ItemsView):
    def __init__(self, ref):
        super().__init__(ref)
        self._ref = ref

    def __iter__(self):
        for key, groups in groupby(self._ref.__iter__(), lambda x: x[0]):
            yield tuple([key, ", ".join(group[1] for group in groups)])

    def __contains__(self, item):
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            return False
        for k, v in self.__iter__():
            if item[0].lower() == k.lower() and item[1] == v:
                return True
        return False

    def __repr__(self):
        return f"dict_items({list(self.__iter__())})"


class _KeysView(collections.abc.KeysView):
    def __init__(self, items):
        super().__init__(items)
        self._items = items

    def __iter__(self) -> Iterator[str]:
        for key, _ in self._items:
            yield key

    def __contains__(self, key):
        try:
            for k in self.__iter__():
                if cast(str, key).lower() == k.lower():
                    return True
        except AttributeError:  # Catch "lower()" if key not a string
            pass
        return False

    def __repr__(self) -> str:
        return f"dict_keys({list(self.__iter__())})"


class _ValuesView(collections.abc.ValuesView):
    def __init__(self, items):
        super().__init__(items)
        self._items = items

    def __iter__(self):
        for _, value in self._items:
            yield value

    def __contains__(self, value):
        for v in self.__iter__():
            if value == v:
                return True
        return False

    def __repr__(self):
        return f"dict_values({list(self.__iter__())})"


class _CIMultiDict(CIMultiDict):
    """Dictionary with the support for duplicate case-insensitive keys."""

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        """Return a new view of the dictionary's keys.

        :return: A new view of the dictionary's keys
        :rtype: ~collections.abc.KeysView
        """
        return _KeysView(self.items())

    def items(self):
        """Return a new view of the dictionary's items.

        :return: A new view of the dictionary's items
        :rtype: ~collections.abc.ItemsView
        """
        return _ItemsView(super().items())

    def values(self):
        """Return a new view of the dictionary's values.

        :return: A new view of the dictionary's values
        :rtype: ~collections.abc.ValuesView
        """
        return _ValuesView(self.items())

    def __getitem__(self, key: str) -> str:
        return ", ".join(self.getall(key, []))

    def get(self, key, default=None):
        values = self.getall(key, None)
        if values:
            values = ", ".join(values)
        return values or default


class RestAioHttpTransportResponse(AsyncHttpResponseImpl):
    def __init__(self, *, internal_response, decompress: bool = True, **kwargs):
        headers = _CIMultiDict(internal_response.headers)
        super().__init__(
            internal_response=internal_response,
            status_code=internal_response.status,
            headers=headers,
            content_type=headers.get("content-type"),
            reason=internal_response.reason,
            stream_download_generator=AioHttpStreamDownloadGenerator,
            content=None,
            **kwargs,
        )
        self._decompress = decompress
        self._decompressed_content = False

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state["_internal_response"] = None  # aiohttp response are not pickable (see headers comments)
        state["headers"] = CIMultiDict(self.headers)  # MultiDictProxy is not pickable
        return state

    @property
    def content(self) -> bytes:
        """Return the response's content in bytes.

        :return: The response's content in bytes
        :rtype: bytes
        """
        if self._content is None:
            raise ResponseNotReadError(self)
        return _aiohttp_content_helper(self)

    async def read(self) -> bytes:
        """Read the response's bytes into memory.

        :return: The response's bytes
        :rtype: bytes
        """
        if not self._content:
            self._stream_download_check()
            self._content = await self._internal_response.read()
        await self._set_read_checks()
        return _aiohttp_content_helper(self)

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        if not self.is_closed:
            self._is_closed = True
            self._internal_response.close()
            await asyncio.sleep(0)


class AioHttpStreamDownloadGenerator(collections.abc.AsyncIterator):
    """Streams the response body data.

    :param pipeline: The pipeline object
    :type pipeline: ~corehttp.runtime.pipeline.AsyncPipeline
    :param response: The client response object.
    :type response: ~corehttp.rest.AsyncHttpResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self,
        pipeline: AsyncPipeline[HttpRequest, AsyncHttpResponse],
        response: RestAioHttpTransportResponse,
        *,
        decompress: bool = True,
    ) -> None:
        self.pipeline = pipeline
        self.request = response.request
        self.response = response

        # TODO: determine if block size should be public on RestAioHttpTransportResponse.
        self.block_size = response._block_size  # pylint: disable=protected-access
        self._decompress = decompress
        self.content_length = int(response.headers.get("Content-Length", 0))
        self._decompressor = None

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        internal_response = self.response._internal_response  # pylint: disable=protected-access
        try:
            # TODO: Determine how chunks should be read.
            # chunk = await self.response.internal_response.content.read(self.block_size)
            chunk = await internal_response.content.read(self.block_size)  # pylint: disable=protected-access
            if not chunk:
                raise _ResponseStopIteration()
            if not self._decompress:
                return chunk
            # TODO: Determine if the following is equivalent to internal_response.headers.get("Content-Encoding")
            enc = self.response.headers.get("Content-Encoding")
            if not enc:
                return chunk
            enc = enc.lower()
            if enc in ("gzip", "deflate"):
                if not self._decompressor:
                    import zlib

                    zlib_mode = (16 + zlib.MAX_WBITS) if enc == "gzip" else -zlib.MAX_WBITS
                    self._decompressor = zlib.decompressobj(wbits=zlib_mode)
                chunk = self._decompressor.decompress(chunk)
            return chunk
        except _ResponseStopIteration:
            internal_response.close()
            raise StopAsyncIteration()  # pylint: disable=raise-missing-from
        except aiohttp.client_exceptions.ClientPayloadError as err:
            # This is the case that server closes connection before we finish the reading. aiohttp library
            # raises ClientPayloadError.
            _LOGGER.warning("Incomplete download: %s", err)
            internal_response.close()
            raise IncompleteReadError(err, error=err) from err
        except aiohttp.client_exceptions.ClientResponseError as err:
            raise ServiceResponseError(err, error=err) from err
        except asyncio.TimeoutError as err:
            raise ServiceResponseError(err, error=err) from err
        except aiohttp.client_exceptions.ClientError as err:
            raise ServiceRequestError(err, error=err) from err
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.close()
            raise
