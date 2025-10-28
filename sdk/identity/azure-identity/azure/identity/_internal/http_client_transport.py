# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore cafile
from json import loads, dumps
import http.client
import ssl
import urllib.parse
from typing import Any, Iterator, MutableMapping, Optional

from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import ServiceRequestError
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.pipeline.transport import HttpTransport

from .token_binding_transport_mixin import TokenBindingTransportMixin


class HttpClientTransportResponse(HttpResponse):
    """Create a HttpResponse from an http.client response.

    :param HttpRequest request: The request.
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param httpclient_response: The response from http.client
    :type httpclient_response: http.client.HTTPResponse
    :param block_size: The block size to use for downloading the response content.
    :type block_size: int
    """

    def __init__(
        self, request: HttpRequest, httpclient_response: http.client.HTTPResponse, block_size: Optional[int] = None
    ) -> None:
        self._request = request
        self._httpclient_response = httpclient_response
        self._block_size = block_size or 4096
        self._data: Optional[bytes] = None
        self._closed = False
        self._headers = {k.lower(): v for k, v in httpclient_response.getheaders()}
        self._content_type = self._headers.get("content-type")
        self._encoding: Optional[str] = None

    def __enter__(self) -> "HttpClientTransportResponse":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed:
            self._httpclient_response.close()
            self._closed = True

    def read(self) -> bytes:
        if self._data is None:
            self._data = self._httpclient_response.read()
        return self._data

    def iter_raw(self, **kwargs: Any) -> Iterator[bytes]:
        if self._data:
            yield self._data
        else:
            chunk = self._httpclient_response.read(self._block_size)
            while chunk:
                yield chunk
                chunk = self._httpclient_response.read(self._block_size)

    def iter_bytes(self, **kwargs: Any) -> Iterator[bytes]:
        # http.client doesn't support compressed encoding automatically,
        # so the decompression is already done at read time.
        # Just use iter_raw here
        yield from self.iter_raw(**kwargs)

    @property
    def request(self) -> HttpRequest:
        return self._request

    @property
    def status_code(self) -> int:
        return self._httpclient_response.status

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._headers

    @property
    def reason(self) -> str:
        return self._httpclient_response.reason

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type

    @property
    def url(self) -> str:
        return self._request.url

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def is_stream_consumed(self) -> bool:
        return self._data is not None

    @property
    def encoding(self) -> Optional[str]:
        return self._encoding

    @encoding.setter
    def encoding(self, value: Optional[str]) -> None:
        self._encoding = value

    @property
    def content(self) -> bytes:
        return self.read()

    def text(self, encoding: Optional[str] = None) -> str:
        if encoding is None:
            encoding = self.encoding or "utf-8"
        return self.content.decode(encoding)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from azure.core.exceptions import HttpResponseError

            raise HttpResponseError(response=self)

    def json(self) -> Any:
        return loads(self.text())


class SniSSLContext(ssl.SSLContext):
    def __new__(cls, sni_hostname: str, protocol=None):
        if protocol is None:
            protocol = ssl.PROTOCOL_TLS_CLIENT
        instance = super().__new__(cls, protocol=protocol)
        instance.sni_hostname = sni_hostname  # type: ignore
        return instance

    def wrap_socket(self, *args, **kwargs):
        kwargs["server_hostname"] = self.sni_hostname  # type: ignore
        return super().wrap_socket(*args, **kwargs)


class HttpClientTransport(TokenBindingTransportMixin, HttpTransport):
    """Implements an HTTP sender using Python's built-in http.client library."""

    def __init__(self, **kwargs) -> None:
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._ssl_context: Optional[ssl.SSLContext] = None
        super().__init__(**kwargs)
        # Initialize SSL context if we have CA data
        if self._ca_data:
            self._ssl_context = self._create_ssl_context()

    def __enter__(self) -> "HttpClientTransport":
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self) -> None:
        pass  # We create connections as needed

    def close(self) -> None:
        pass  # No persistent connections to close

    def _create_ssl_context(self) -> ssl.SSLContext:
        # Create SSL context using current CA data or file.
        ssl_context: ssl.SSLContext
        if self._sni:
            ssl_context = SniSSLContext(self._sni, ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.check_hostname = True

            if self._ca_data:
                ssl_context.load_verify_locations(cadata=self._ca_data)
            else:
                ssl_context.load_default_certs()
        else:
            ssl_context = ssl.create_default_context(cadata=self._ca_data)

        if not self.connection_config.verify:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        return ssl_context

    def _get_connection(self, host: str) -> http.client.HTTPSConnection:
        # Check if CA file has changed and reload ca_data if needed
        if self._ca_file and self._has_ca_file_changed():
            self._load_ca_file_to_data()
            # If ca_data was updated, recreate SSL context with the new data
            if self._ca_data:
                self._ssl_context = self._create_ssl_context()

        # Use cached SSL context or create a new one
        ssl_context = self._ssl_context or self._create_ssl_context()

        connection = http.client.HTTPSConnection(
            host,
            timeout=self.connection_config.timeout,
            context=ssl_context,
        )

        return connection

    def send(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Send request object according to configuration.

        :param request: The HTTP request object.
        :type request: ~azure.core.rest.HttpRequest
        :return: The HTTP response object.
        :rtype: ~azure.core.rest.HttpResponse
        """

        # Get or create a connection for the URL
        self._update_request_url(request)
        parsed_url = urllib.parse.urlparse(request.url)
        full_path = urllib.parse.urlunparse(
            ("", "", parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment)
        )

        # Get connection timeout
        connection_timeout = kwargs.pop("connection_timeout", self.connection_config.timeout)

        try:
            # Get connection
            connection = self._get_connection(parsed_url.netloc)

            if connection_timeout is not None:
                connection.timeout = connection_timeout
            connection.request(
                request.method,
                full_path,
                body=dumps(request.data) if isinstance(request.data, (dict, list)) else request.data,
                headers=request.headers,
            )
            response = connection.getresponse()
            transport_response = HttpClientTransportResponse(
                request=request,
                httpclient_response=response,
                block_size=self.connection_config.data_block_size,
            )

            connection.close()
            return transport_response

        except http.client.HTTPException as err:
            raise ServiceRequestError(err) from err
        except ssl.SSLError as err:
            raise ServiceRequestError(err) from err
        except Exception as err:
            raise ServiceRequestError(err) from err

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"
