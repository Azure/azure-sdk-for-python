# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore cafile
from json import loads
import hashlib
import http.client
import os
import ssl
import urllib.parse
from typing import Any, Iterator, MutableMapping, Optional

from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.pipeline.transport import HttpTransport


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
        instance = super().__new__(cls, protocol=protocol)
        instance.sni_hostname = sni_hostname  # type: ignore
        return instance

    def wrap_socket(self, *args, **kwargs):
        kwargs["server_hostname"] = self.sni_hostname  # type: ignore
        return super().wrap_socket(*args, **kwargs)


class HttpClientTransport(HttpTransport):
    """Implements an HTTP sender using Python's built-in http.client library."""

    def __init__(self, **kwargs) -> None:
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._ca_data = kwargs.pop("ca_data", None)
        self._ca_file = kwargs.pop("ca_file", None)

        if self._ca_file and self._ca_data:
            raise ValueError("Both ca_file and ca_data are set. Only one should be set")

        self._sni = kwargs.pop("sni", None)
        self._proxy_endpoint = kwargs.pop("proxy_endpoint", None)
        if self._proxy_endpoint:
            self._validate_url(self._proxy_endpoint)

        self._connection: Optional[http.client.HTTPSConnection] = None
        self._ca_file_hash: Optional[str] = None
        self._ca_file_mtime: Optional[float] = None

        # Initialize CA file tracking if a CA file is specified
        if self._ca_file:
            self._update_ca_file_tracking()

    def __enter__(self) -> "HttpClientTransport":
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self) -> None:
        pass  # We create connections as needed

    def close(self) -> None:
        if self._connection:
            self._connection.close()
        self._connection = None

    def _validate_url(self, url: str) -> None:
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme != "https":
            raise ValueError(f"Endpoint URL ({url}) must use the 'https' scheme. Got '{parsed_url.scheme}' instead.")
        if parsed_url.username or parsed_url.password:
            raise ValueError(f"Endpoint URL ({url}) must not contain username or password.")
        if parsed_url.fragment:
            raise ValueError(f"Endpoint URL ({url}) must not contain a fragment.")
        if parsed_url.query:
            raise ValueError(f"Endpoint URL ({url}) must not contain query parameters.")

    def _update_ca_file_tracking(self) -> None:
        """Update the CA file hash and modification time for change detection."""
        if not self._ca_file or not os.path.exists(self._ca_file):
            self._ca_file_hash = None
            self._ca_file_mtime = None
            return

        try:
            # Read file content first to check if empty
            with open(self._ca_file, "rb") as f:
                content = f.read()

                # Check if the file is empty
                if not content:
                    # If no prior tracking state exists (first read), fail
                    if self._ca_file_hash is None:
                        raise ValueError(f"CA file ({self._ca_file}) is empty. Cannot establish secure connection.")
                    return

                # File has content, update tracking
                self._ca_file_mtime = os.path.getmtime(self._ca_file)
                self._ca_file_hash = hashlib.sha256(content).hexdigest()
        except (OSError, IOError):
            # If we can't read the file, clear the tracking
            self._ca_file_hash = None
            self._ca_file_mtime = None

    def _has_ca_file_changed(self) -> bool:
        """Check if the CA file has changed since last tracking update.

        :return: True if the CA file has changed, False otherwise.
        :rtype: bool
        """
        if not self._ca_file:
            return False

        if not os.path.exists(self._ca_file):
            # File was deleted, consider this a change
            return self._ca_file_hash is not None or self._ca_file_mtime is not None

        try:
            # Check modification time first (faster)
            current_mtime = os.path.getmtime(self._ca_file)
            if self._ca_file_mtime != current_mtime:
                return True

            # If mtime is the same, check content hash to be sure
            with open(self._ca_file, "rb") as f:
                content = f.read()
                current_hash = hashlib.sha256(content).hexdigest()
                return self._ca_file_hash != current_hash

        except (OSError, IOError):
            # If we can't read the file, assume it changed
            return True

    def _get_connection(self, host: str) -> http.client.HTTPSConnection:

        # Check if CA file has changed and invalidate connections if needed
        if self._ca_file and self._has_ca_file_changed():
            # CA file changed, close all existing connections and clear cache
            if self._connection:
                self._connection.close()
            self._connection = None
            # Update tracking with new CA file state
            self._update_ca_file_tracking()

        # Use existing connection if available
        if self._connection:
            return self._connection

        # Create HTTPS connection
        ssl_context: ssl.SSLContext
        if self._sni:
            ssl_context = SniSSLContext(self._sni, ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.check_hostname = True

            if self._ca_data or self._ca_file:
                ssl_context.load_verify_locations(cafile=self._ca_file, cadata=self._ca_data)
            else:
                ssl_context.load_default_certs()
        else:
            ssl_context = ssl.create_default_context(cafile=self._ca_file, cadata=self._ca_data)

        if not self.connection_config.verify:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        connection = http.client.HTTPSConnection(
            host,
            timeout=self.connection_config.timeout,
            context=ssl_context,
        )

        self._connection = connection
        return connection

    def _update_request_url(self, request: HttpRequest) -> None:
        parsed_request_url = urllib.parse.urlparse(request.url)
        if self._proxy_endpoint:
            parsed_proxy_url = urllib.parse.urlparse(self._proxy_endpoint)
            combined_path = parsed_proxy_url.path.rstrip("/") + "/" + parsed_request_url.path.lstrip("/")
            new_url = urllib.parse.urlunparse(
                (
                    parsed_proxy_url.scheme,
                    parsed_proxy_url.netloc,
                    combined_path,
                    parsed_request_url.params,
                    parsed_request_url.query,
                    parsed_request_url.fragment,
                )
            )
            request.url = new_url

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

            connection.request(request.method, full_path, body=request.data, headers=request.headers)
            response = connection.getresponse()
            return HttpClientTransportResponse(
                request=request,
                httpclient_response=response,
                block_size=self.connection_config.data_block_size,
            )

        except http.client.HTTPException as err:
            raise ServiceRequestError(err) from err
        except ssl.SSLError as err:
            raise ServiceResponseError(err) from err
        except Exception as err:
            raise ServiceRequestError(err) from err

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"
