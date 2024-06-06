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
from typing import Any, Mapping, Optional, Union

import urllib3
from azure.core.pipeline import Pipeline
from azure.core.utils import case_insensitive_dict

from azure.core.exceptions import ServiceRequestError, ServiceResponseError, IncompleteReadError
from azure.core.configuration import ConnectionConfiguration
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest as RestHttpRequest, HttpResponse as RestHttpResponse
from azure.core.rest._http_response_impl import HttpResponseImpl

DEFAULT_BLOCK_SIZE = 32768


class Urllib3StreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(self, pipeline: Pipeline, response: "Urllib3TransportResponse", **kwargs) -> None:
        self.pipeline = pipeline
        self.response = response
        decompress = kwargs.pop("decompress", True)
        self.iter_content_func = self.response.internal_response.read_chunked(decode_content=decompress)

    def __iter__(self) -> "Urllib3StreamDownloadGenerator":
        return self

    def __next__(self) -> bytes:
        return next(self.iter_content_func)


class Urllib3TransportResponse(HttpResponseImpl):
    def __init__(
        self,
        *,
        request: RestHttpRequest,
        internal_response: urllib3.response.HTTPResponse,
    ) -> None:
        headers = case_insensitive_dict(internal_response.getheaders())
        super().__init__(
            request=request,
            internal_response=internal_response,
            status_code=internal_response.status_code,
            headers=headers,
            reason=internal_response.reason,
            content_type=headers.get("content-type"),
            stream_download_generator=Urllib3StreamDownloadGenerator,
        )
    
    def close(self) -> None:
        super().close()
        self._internal_response.release_conn()


class Urllib3Transport(HttpTransport[RestHttpRequest, RestHttpResponse]):
    """Implements a basic urllib3 HTTP sender.

    :keyword pool: A preconfigured urllib3 PoolManager of HttpConnectionPool.
    :paramtype pool: ~urllib3.PoolManager or ~urllib3.HTTPConnectionPool
    """

    def __init__(
        self,
        *,
        pool: Optional[Union[urllib3.PoolManager, urllib3.HTTPConnectionPool]] = None,
        **kwargs
    ) -> None:
        self._pool: Optional[Union[urllib3.PoolManager, urllib3.HTTPConnectionPool]] = pool
        self._pool_owner: bool = kwargs.get("pool_owner", True)
        self._config = ConnectionConfiguration(**kwargs)
        self._pool_cls = urllib3.PoolManager
        if 'proxies' in kwargs:
            proxies = kwargs.pop('proxies')
            if len(proxies) > 1:
                raise ValueError("Only a single proxy url is supported for urllib3.")
            proxy_url = list(proxies.values())[0]
            self._pool_cls = functools.partial(urllib3.ProxyManager, proxy_url)

        # See https://github.com/Azure/azure-sdk-for-python/issues/25640 to understand why we track this
        self._has_been_opened = False

    def _cert_verify(self, kwargs: Mapping[str, Any]) -> None:
        """Update the request kwargs to configure the SSL certificate.

        :param dict[str, Any] kwargs: The request context keyword args. 
        """
        verify : Union[bool, str] = kwargs.pop("connection_verify", self._config.verify)
        cert_kwargs = {}
        if verify is False:
            # We ignore verify=True as "CERT_REQUIRED" is the default for HTTPS.
            cert_kwargs["cert_reqs"] = "CERT_NONE"
        elif os.path.isdir(verify):
            cert_kwargs["ca_cert_dir"] = verify
        elif isinstance(verify, str):
            cert_kwargs["ca_certs"] = verify

        cert: Optional[str] = kwargs.pop("connection_cert", self._config.cert)
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
                self._pool = self._pool_cls(
                    retries=False,
                    blocksize=DEFAULT_BLOCK_SIZE
                )
            else:
                raise ValueError("pool_owner cannot be False and no pool is available")
        self._has_been_opened = True

    def close(self) -> None:
        """Close the session if it is not externally owned."""
        if self._pool and self._pool_owner:
            try:
                self._pool.clear()  # Used for an instance of PoolManager/ProxyManager
            except AttributeError:
                self._pool.close()  # Used for an instance of HTTPConnectionPool/HTTPSConnectionPool
            self._pool = None


    def send(self, request: RestHttpRequest, **kwargs) -> Urllib3TransportResponse:
        """Send the request using this HTTP sender.

        :param request: The HTTP request.
        :paramtype request: ~azure.core.rest.HttpRequest
        :rtype: ~azure.core.rest.HttpResponse
        """
        if 'proxies' in kwargs:
            raise NotImplementedError(
                "Proxies are not yet supported. Please create the transport using a configured urllib3.ProxyManager."
            )
        self.open()
        connection_timeout = kwargs.pop("connection_timeout", self._config.timeout)
        read_timeout = kwargs.pop("read_timeout", self._config.read_timeout)
        timeout=urllib3.util.Timeout(
            connect=connection_timeout,
            read=read_timeout
        )
        self._cert_verify(kwargs)
        stream_response: bool = kwargs.pop("stream", False)
        try:
            result = self._pool.urlopen(
                method=request.method,
                url=request.url,
                body=request.content,
                timeout=timeout,
                headers=request.headers.items(),
                preload_context=not stream_response,
                decode_content=False,
                redirect=False,
                reties=False,
                **kwargs
            )
            response = Urllib3TransportResponse(
                    request=request,
                    internal_response=result,
                    block_size=self.connection_config.data_block_size,
                )
            if not stream_response:
                response.read()
        except AttributeError as err:
            if not self._pool:
                raise ValueError() from err
            raise
        except (
                urllib3.exceptions.IncompleteRead,
                urllib3.exceptions.InvalidChunkLength) as err:
            raise IncompleteReadError(err, error=err) from err
        except (
                urllib3.exceptions.RequestError,
                urllib3.exceptions.ProtocolError,
                urllib3.exceptions.ResponseError) as err:
            raise ServiceResponseError(err, error=err) from err
        except (
                ValueError,
                urllib3.exceptions.SSLError,
                urllib3.exceptions.ProxyError,
                urllib3.exceptions.ConnectTimeoutError,
                urllib3.exceptions.PoolError) as err:
            raise ServiceRequestError(err, error=err) from err
        except urllib3.exceptions.HTTPError as err:
            # Catch anything else that urllib3 gives us
            raise ServiceResponseError(err, error=err) from err
        return response
        

    def __enter__(self) -> "Urllib3Transport":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()
