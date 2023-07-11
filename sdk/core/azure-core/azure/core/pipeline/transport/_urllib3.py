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
from typing import Any, ContextManager, Iterator, Mapping, Optional, Union

import urllib3
import certifi
from azure.core.pipeline import Pipeline

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.configuration import ConnectionConfiguration
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest as RestHttpRequest, HttpResponse as RestHttpResponse

DEFAULT_BLOCK_SIZE = 32768


class Urllib3TransportResponse(RestHttpResponse):
    ...



class Urllib3StreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(self, pipeline: Pipeline, response: Urllib3TransportResponse, **kwargs) -> None:
        self.pipeline = pipeline
        self.response = response
        decompress = kwargs.pop("decompress", True)

        if decompress:
            self.iter_content_func = self.response.internal_response.iter_bytes()
        else:
            self.iter_content_func = self.response.internal_response.iter_raw()

    def __iter__(self) -> "Urllib3StreamDownloadGenerator":
        return self

    def __next__(self):
        try:
            return next(self.iter_content_func)
        except StopIteration:
            self.response.stream_contextmanager.__exit__(None, None, None)
            raise


class Urllib3Transport(HttpTransport[RestHttpRequest, RestHttpResponse]):
    """Implements a basic httpx HTTP sender

    :keyword httpx.Client client: HTTPX client to use instead of the default one
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
        if 'proxies' in kwargs:
            raise NotImplementedError(
                "Proxies are not yet supported. Please pass in a configured urllib3.ProxyManager."
            )

    def _cert_verify(self, url: str, kwargs: Mapping[str, Any]) -> None:
        """Verify a SSL certificate.

        :param url: The requested URL.
        :param verify: Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use
        :param cert: The SSL certificate to verify.
        """
        verify : Union[bool, str] = kwargs.pop("connection_verify", self._config.verify)
        cert: Optional[str] = kwargs.pop("connection_cert", self._config.verify)
        cert_kwargs = {}
        if url.lower().startswith("https") and verify:

            cert_loc = None

            # Allow self-specified cert location.
            if verify is not True:
                cert_loc = verify

            if not cert_loc:
                cert_loc = certifi.where()

            if not cert_loc or not os.path.exists(cert_loc):
                raise OSError(
                    f"Could not find a suitable TLS CA certificate bundle, "
                    f"invalid path: {cert_loc}"
                )

            cert_kwargs["cert_reqs"] = "CERT_REQUIRED"

            if not os.path.isdir(cert_loc):
                cert_kwargs["ca_certs"] = cert_loc
            else:
                cert_kwargs["ca_cert_dir"] = cert_loc
        else:
            cert_kwargs["cert_reqs"] = "CERT_NONE"
            cert_kwargs["ca_certs"] = None
            cert_kwargs["ca_cert_dir"] = None

        if cert:
            if not isinstance(cert, str):
                cert_kwargs["cert_file"] = cert[0]
                cert_kwargs["key_file"] = cert[1]
            else:
                cert_kwargs["cert_file"] = cert
                cert_kwargs["key_file"] = None
            if cert_kwargs["cert_file"] and not os.path.exists(cert_kwargs["cert_file"]):
                raise OSError(
                    f"Could not find the TLS certificate file, "
                    f"invalid path: {cert_kwargs['cert_file']}"
                )
            if cert_kwargs["key_file"] and not os.path.exists(cert_kwargs["key_file"]):
                raise OSError(
                    f"Could not find the TLS key file, invalid path: {cert_kwargs['key_file']}"
                )
        kwargs.update(cert_kwargs)
    
    def open(self):
        """Assign new session if one does not already exist."""
        if not self._pool and self._pool_owner:
            self._pool = urllib3.PoolManager(
                retries=False,
                blocksize=DEFAULT_BLOCK_SIZE
            )

    def close(self):
        """Close the session if it is not externally owned."""
        if self._pool and self._pool_owner:
            try:
                self._pool.clear()  # Used for an instance of PoolManager/ProxyManager
            except AttributeError:
                self._pool.close()  # Used for an instance of HTTPConnectionPool/HTTPSConnectionPool
            self._pool = None


    def send(self, request: RestHttpRequest, **kwargs) -> Urllib3TransportResponse:
        """Send the request using this HTTP sender.

        :param request: The pipeline request object
        :type request: ~azure.core.transport.HTTPRequest
        :return: The pipeline response object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse
        """
        if 'proxies' in kwargs:
            raise NotImplementedError(
                "Proxies are not yet supported. Please pass in a configured urllib3.ProxyManager."
            )
        self.open()
        connection_timeout = kwargs.pop("connection_timeout", self._config.timeout)
        read_timeout = kwargs.pop("read_timeout", self._config.read_timeout)
        timeout=urllib3.util.Timeout(
            connect=connection_timeout,
            read=read_timeout
        )
        self._cert_verify(request.url, kwargs)
        try:
            response = self._pool.urlopen(
                method=request.method,
                url=request.url,
                body=request.content,
                timeout=timeout,
                headers=request.headers.items(),
                preload_context=not kwargs.pop("stream", False),
                decode_content=False,
                redirect=False,
                **kwargs
            )
        except:
            ...
        



    def __enter__(self) -> "Urllib3Transport":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def send(self, request: HttpRequest, **kwargs) -> HttpXTransportResponse:
        stream_response = kwargs.pop("stream", False)
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request.data,
            "content": request.content,
            "files": request.files,
            **kwargs,
        }
        stream_ctx: Optional[ContextManager] = None
        try:
            if stream_response:
                stream_ctx = self.client.stream(**parameters)
                if stream_ctx:
                    response = stream_ctx.__enter__()
            else:
                response = self.client.request(**parameters)
        except (
            httpx.ReadTimeout,
            httpx.ProtocolError,
        ) as err:
            raise ServiceResponseError(err, error=err)
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err)

        return HttpXTransportResponse(request, response, stream_contextmanager=stream_ctx)
