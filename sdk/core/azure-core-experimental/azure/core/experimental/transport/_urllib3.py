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
import os
import functools
import collections
from itertools import groupby
from typing import Any, Callable, Mapping, Optional, Union, Dict, cast, List, Tuple, Iterator

import urllib3
from urllib3 import HTTPHeaderDict  # type: ignore[attr-defined]

from azure.core.pipeline import Pipeline
from azure.core.exceptions import ServiceRequestError, ServiceResponseError, IncompleteReadError, DecodeError
from azure.core.configuration import ConnectionConfiguration
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest as RestHttpRequest, HttpResponse as RestHttpResponse
from azure.core.rest._http_response_impl import HttpResponseImpl


DEFAULT_BLOCK_SIZE = 32768
_TYPE_FIELD_VALUE = Union[str, bytes]
_TYPE_FIELD_VALUE_TUPLE = Union[
    _TYPE_FIELD_VALUE,
    Tuple[str, _TYPE_FIELD_VALUE],
    Tuple[str, _TYPE_FIELD_VALUE, str],
]


def _read_files(fields, files):
    if files is None:
        return
    if isinstance(files, Mapping):
        files = list(files.items())
    for k, v in files:
        if hasattr(v, "read"):
            updated = v.read()
        elif isinstance(v, tuple):
            updated = tuple(i.read() if hasattr(i, "read") else i for i in v)
        else:
            updated = v
        fields.append((k, updated))


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


class Urllib3TransportHeaders(HTTPHeaderDict):
    """TODO: This is inefficient, as it's reprocessing the items after urllib3 already
    does it. If this transport is made part of Core, this should probably be revised.
    """

    def items(self) -> _ItemsView:
        return _ItemsView(super().items())

    def keys(self) -> _KeysView:
        return _KeysView(self.items())

    def values(self) -> _ValuesView:
        return _ValuesView(self.items())


class Urllib3StreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(self, pipeline: Pipeline, response: "Urllib3TransportResponse", **kwargs: Any) -> None:
        self.pipeline = pipeline
        self.response = response
        decompress: bool = kwargs.pop("decompress", True)
        self.iter_content_func: Iterator[bytes] = self.response._internal_response.stream(
            amt=self.response._block_size, decode_content=decompress
        )

    def __iter__(self) -> "Urllib3StreamDownloadGenerator":
        return self

    def __next__(self) -> bytes:
        try:
            return next(self.iter_content_func)
        except urllib3.exceptions.DecodeError as err:
            raise DecodeError(err, error=err) from err
        except (urllib3.exceptions.IncompleteRead, urllib3.exceptions.InvalidChunkLength) as err:
            raise IncompleteReadError(err, error=err) from err
        except urllib3.exceptions.HTTPError as err:
            msg = err.__str__()
            if "IncompleteRead" in msg:
                raise IncompleteReadError(err, error=err) from err
            raise ServiceResponseError(err, error=err) from err


class Urllib3TransportResponse(HttpResponseImpl):
    def __init__(
        self, *, request: RestHttpRequest, internal_response: urllib3.response.HTTPResponse, **kwargs: Any
    ) -> None:
        headers = Urllib3TransportHeaders(kwargs.pop("headers", internal_response.headers))
        super().__init__(
            request=request,
            internal_response=internal_response,
            status_code=kwargs.pop("status_code", internal_response.status),
            headers=headers,
            reason=kwargs.pop("reason", internal_response.reason),
            content_type=kwargs.pop("content-type", headers.get("content-type")),
            stream_download_generator=kwargs.pop("stream_download_generator", Urllib3StreamDownloadGenerator),
            **kwargs,
        )

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state["_internal_response"] = None  # urllib3 response are not pickable (see headers comments)
        return state

    def close(self) -> None:
        super().close()
        self._internal_response.release_conn()


class Urllib3Transport(HttpTransport[RestHttpRequest, RestHttpResponse]):
    """Implements a basic urllib3 HTTP sender.

    Missing features:

     - Support for per-request proxy configuration override. Proxy configuration is currently
       only supported at client/transport construction.

    :keyword pool: A preconfigured urllib3 PoolManager.
    :paramtype pool: ~urllib3.PoolManager or None
    """

    def __init__(self, *, pool: Optional[urllib3.PoolManager] = None, **kwargs: Any) -> None:
        self._pool: Optional[urllib3.PoolManager] = pool
        self._pool_owner: bool = kwargs.get("pool_owner", True)
        self._config = ConnectionConfiguration(**kwargs)
        self._pool_cls: Callable[..., urllib3.PoolManager] = urllib3.PoolManager
        if "proxies" in kwargs:
            proxies = kwargs.pop("proxies")
            if len(proxies) > 1:
                raise ValueError("Only a single proxy url is supported for urllib3.")
            proxy_url = list(proxies.values())[0]
            self._pool_cls = functools.partial(urllib3.ProxyManager, proxy_url)

        # See https://github.com/Azure/azure-sdk-for-python/issues/25640 to understand why we track this
        self._has_been_opened = False

    def _cert_verify(self, kwargs: Dict[str, Any]) -> None:
        """Update the request kwargs to configure the SSL certificate.

        :param dict[str, Any] kwargs: The request context keyword args.
        """
        verify: Union[bool, str] = kwargs.pop("connection_verify", self._config.verify)
        cert_kwargs: Dict[str, Optional[str]] = {}
        if verify is False:
            # We ignore verify=True as "CERT_REQUIRED" is the default for HTTPS.
            cert_kwargs["cert_reqs"] = "CERT_NONE"
        elif os.path.isdir(verify):
            cert_kwargs["ca_cert_dir"] = cast(str, verify)
        elif isinstance(verify, str):
            cert_kwargs["ca_certs"] = verify

        cert: Optional[Union[str, Tuple[str, str]]] = kwargs.pop("connection_cert", self._config.cert)
        if cert:
            if not isinstance(cert, str):
                cert_kwargs["cert_file"] = cert[0]
                cert_kwargs["key_file"] = cert[1]
            else:
                cert_kwargs["cert_file"] = cert
                cert_kwargs["key_file"] = None
        kwargs.update(cert_kwargs)

    def open(self) -> None:
        """Assign new session if one does not already exist."""
        if self._has_been_opened and not self._pool:
            raise ValueError(
                "HTTP transport has already been closed. "
                "You may check if you're calling a function outside of the `with` of your client creation, "
                "or if you called `close()` on your client already."
            )
        if not self._pool:
            if self._pool_owner:
                self._pool = self._pool_cls(retries=False, blocksize=DEFAULT_BLOCK_SIZE)
            else:
                raise ValueError("pool_owner cannot be False and no pool is available")
        self._has_been_opened = True

    def close(self) -> None:
        """Close the pool if it is not externally owned."""
        if self._pool and self._pool_owner:
            self._pool.clear()
            self._pool = None

    def send(self, request: RestHttpRequest, **kwargs: Any) -> RestHttpResponse:
        """Send the request using this HTTP sender.

        :param request: The HTTP request.
        :type request: ~azure.core.rest.HttpRequest
        :rtype: ~azure.core.rest.HttpResponse
        :return: The HTTP response.
        """
        if "proxies" in kwargs:
            raise NotImplementedError(
                "Proxies are not yet supported. Please create the transport using a configured urllib3.ProxyManager."
            )
        self.open()
        connection_timeout = kwargs.pop("connection_timeout", self._config.timeout)
        read_timeout = kwargs.pop("read_timeout", self._config.read_timeout)
        timeout = urllib3.util.Timeout(connect=connection_timeout, read=read_timeout)
        self._cert_verify(kwargs)
        stream_response: bool = kwargs.pop("stream", False)
        self._pool = cast(urllib3.PoolManager, self._pool)
        try:
            if request.files:
                fields: List[Tuple[str, _TYPE_FIELD_VALUE_TUPLE]] = []
                _read_files(fields, request.data)
                _read_files(fields, request.files)
                result = self._pool.request_encode_body(
                    method=request.method,
                    url=request.url,
                    fields=fields,
                    encode_multipart=True,
                    timeout=timeout,
                    headers=request.headers,
                    preload_content=False,
                    decode_content=False,
                    redirect=False,
                    retries=False,
                    **kwargs,
                )
            elif isinstance(request.data, Mapping):
                result = self._pool.request_encode_body(
                    method=request.method,
                    url=request.url,
                    fields=request.data,
                    encode_multipart=False,
                    timeout=timeout,
                    headers=request.headers,
                    preload_content=False,
                    decode_content=False,
                    redirect=False,
                    retries=False,
                    **kwargs,
                )
            else:
                result = self._pool.urlopen(
                    method=request.method,
                    url=request.url,
                    body=request.data,
                    timeout=timeout,
                    headers=request.headers,
                    preload_content=False,
                    decode_content=False,
                    redirect=False,
                    retries=False,
                    **kwargs,
                )
            response = Urllib3TransportResponse(
                request=request,
                internal_response=result,
                block_size=self._config.data_block_size,
            )
            if not stream_response:
                response.read()
        except AttributeError as err:
            if not self._pool:
                raise ValueError() from err
            raise
        except (urllib3.exceptions.IncompleteRead, urllib3.exceptions.InvalidChunkLength) as err:
            raise IncompleteReadError(err, error=err) from err
        except (
            urllib3.exceptions.RequestError,
            urllib3.exceptions.ProtocolError,
            urllib3.exceptions.ResponseError,
        ) as err:
            raise ServiceResponseError(err, error=err) from err
        except (
            ValueError,
            urllib3.exceptions.SSLError,
            urllib3.exceptions.ProxyError,
            urllib3.exceptions.ConnectTimeoutError,
            urllib3.exceptions.PoolError,
        ) as err:
            raise ServiceRequestError(err, error=err) from err
        except urllib3.exceptions.HTTPError as err:
            # Catch anything else that urllib3 gives us
            raise ServiceResponseError(err, error=err) from err
        return response

    def __enter__(self) -> "Urllib3Transport":
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
