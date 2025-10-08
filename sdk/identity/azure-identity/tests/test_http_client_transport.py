# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import http.client
import json
import os
import ssl
import tempfile
import time
from unittest import mock
from urllib.parse import urlparse

import pytest

from azure.core.rest import HttpRequest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.identity._internal.http_client_transport import HttpClientTransport, SniSSLContext


class TestHttpClientTransport:
    """Test cases for HttpClientTransport class."""

    def test_init_basic(self):
        """Test basic initialization of HttpClientTransport."""
        transport = HttpClientTransport()
        assert transport._ca_data is None
        assert transport._ca_file is None
        assert transport._sni is None
        assert transport._proxy_endpoint is None
        assert transport._connection is None
        assert transport._ca_file_hash is None
        assert transport._ca_file_mtime is None

    def test_init_with_ca_data(self):
        """Test initialization with CA data."""
        ca_data = "-----BEGIN CERTIFICATE-----\nSome fake cert\n-----END CERTIFICATE-----"
        transport = HttpClientTransport(ca_data=ca_data)
        assert transport._ca_data == ca_data
        assert transport._ca_file is None

    def test_init_with_ca_file(self):
        """Test initialization with CA file."""
        # Use simple but valid-looking PEM content
        ca_content = "-----BEGIN CERTIFICATE-----\nMIIDummy certificate content here\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_content)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)
            assert transport._ca_file == temp_file_path
            assert transport._ca_data is None
            assert transport._ca_file_hash is not None
            assert transport._ca_file_mtime is not None
        finally:
            os.unlink(temp_file_path)

    def test_init_with_both_ca_file_and_data_raises_error(self):
        """Test that providing both CA file and data raises an error."""
        ca_data = "-----BEGIN CERTIFICATE-----\nMIIDummy certificate content\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_data)
            temp_file_path = temp_file.name

        try:
            with pytest.raises(ValueError, match="Both ca_file and ca_data are set"):
                HttpClientTransport(ca_file=temp_file_path, ca_data=ca_data)
        finally:
            os.unlink(temp_file_path)

    def test_init_with_empty_ca_file_raises_error(self):
        """Test that empty CA file raises an error."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            with pytest.raises(ValueError, match="CA file .* is empty"):
                HttpClientTransport(ca_file=temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_init_with_sni(self):
        """Test initialization with SNI hostname."""
        sni_hostname = "example.com"
        transport = HttpClientTransport(sni=sni_hostname)
        assert transport._sni == sni_hostname

    def test_init_with_proxy_endpoint(self):
        """Test initialization with proxy endpoint."""
        proxy_endpoint = "https://proxy.example.com:8080"
        transport = HttpClientTransport(proxy_endpoint=proxy_endpoint)
        assert transport._proxy_endpoint == proxy_endpoint

    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        transport = HttpClientTransport()
        # Should not raise any exception
        transport._validate_url("https://example.com/path")

    def test_validate_url_non_https_scheme(self):
        """Test URL validation rejects non-HTTPS schemes."""
        transport = HttpClientTransport()
        with pytest.raises(ValueError, match="must use the 'https' scheme"):
            transport._validate_url("http://example.com")

    def test_validate_url_with_user_info(self):
        """Test URL validation rejects URLs with user info."""
        transport = HttpClientTransport()
        with pytest.raises(ValueError, match="must not contain username or password"):
            transport._validate_url("https://user:pass@example.com")

    def test_validate_url_with_fragment(self):
        """Test URL validation rejects URLs with fragments."""
        transport = HttpClientTransport()
        with pytest.raises(ValueError, match="must not contain a fragment"):
            transport._validate_url("https://example.com#fragment")

    def test_validate_url_with_query(self):
        """Test URL validation rejects URLs with query parameters."""
        transport = HttpClientTransport()
        with pytest.raises(ValueError, match="must not contain query parameters"):
            transport._validate_url("https://example.com?query=value")

    def test_ca_file_tracking_nonexistent_file(self):
        """Test CA file tracking with non-existent file."""
        transport = HttpClientTransport()
        transport._ca_file = "/nonexistent/file.pem"
        transport._update_ca_file_tracking()
        assert transport._ca_file_hash is None
        assert transport._ca_file_mtime is None

    def test_ca_file_tracking_updates_hash_and_mtime(self):
        """Test CA file tracking updates hash and modification time."""
        content = "-----BEGIN CERTIFICATE-----\nMIIDummy certificate content\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)
            expected_hash = hashlib.sha256(content.encode()).hexdigest()
            assert transport._ca_file_hash == expected_hash
            assert transport._ca_file_mtime == os.path.getmtime(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_ca_file_change_detection_no_change(self):
        """Test CA file change detection when file hasn't changed."""
        content = "-----BEGIN CERTIFICATE-----\nMIIDummy certificate content\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)
            # File hasn't changed
            assert not transport._has_ca_file_changed()
        finally:
            os.unlink(temp_file_path)

    def test_ca_file_change_detection_content_changed(self):
        """Test CA file change detection when file content has changed."""
        original_content = "-----BEGIN CERTIFICATE-----\nMIIDOriginal certificate\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(original_content)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)

            # Modify the file
            time.sleep(0.1)  # Ensure mtime changes
            modified_content = "-----BEGIN CERTIFICATE-----\nMIIDModified certificate\n-----END CERTIFICATE-----"
            with open(temp_file_path, "w") as f:
                f.write(modified_content)

            # File should be detected as changed
            assert transport._has_ca_file_changed()
        finally:
            os.unlink(temp_file_path)

    def test_ca_file_change_detection_file_deleted(self):
        """Test CA file change detection when file is deleted."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("-----BEGIN CERTIFICATE-----\nSome cert\n-----END CERTIFICATE-----")
            temp_file_path = temp_file.name

        transport = HttpClientTransport(ca_file=temp_file_path)

        # Delete the file
        os.unlink(temp_file_path)

        # File deletion should be detected as a change
        assert transport._has_ca_file_changed()

    def test_ca_file_empty_during_rotation(self):
        """Test CA file becoming empty during rotation with existing connection."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("-----BEGIN CERTIFICATE-----\nSome cert\n-----END CERTIFICATE-----")
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)
            original_hash = transport._ca_file_hash

            # Simulate having an existing connection
            transport._connection = mock.Mock()

            # Make file empty
            with open(temp_file_path, "w") as f:
                f.write("")

            # Should not raise error and should preserve old hash
            transport._update_ca_file_tracking()
            assert transport._ca_file_hash == original_hash
        finally:
            os.unlink(temp_file_path)

    def test_update_request_url_no_proxy(self):
        """Test request URL update with no proxy."""
        transport = HttpClientTransport()
        request = HttpRequest("GET", "https://example.com/path?query=value")
        original_url = request.url

        transport._update_request_url(request)

        # URL should remain unchanged
        assert request.url == original_url

    def test_update_request_url_with_proxy(self):
        """Test request URL update with proxy."""
        proxy_endpoint = "https://proxy.example.com:8080/proxy"
        transport = HttpClientTransport(proxy_endpoint=proxy_endpoint)
        request = HttpRequest("GET", "https://original.com/api/endpoint?query=value")

        transport._update_request_url(request)

        # URL should be updated to use proxy
        expected_url = "https://proxy.example.com:8080/proxy/api/endpoint?query=value"
        assert request.url == expected_url

    def test_update_request_url_proxy_path_combination(self):
        """Test request URL update with proxy that has a path."""
        proxy_endpoint = "https://proxy.example.com/service"
        transport = HttpClientTransport(proxy_endpoint=proxy_endpoint)
        request = HttpRequest("GET", "https://original.com/oauth2/v2.0/token")

        transport._update_request_url(request)

        # Paths should be combined correctly
        expected_url = "https://proxy.example.com/service/oauth2/v2.0/token"
        assert request.url == expected_url

    def test_context_manager(self):
        """Test HttpClientTransport as context manager."""
        transport = HttpClientTransport()

        with transport as t:
            assert t is transport

        # Should be able to use after context manager
        assert transport is not None

    def test_close_with_connection(self):
        """Test closing transport with active connection."""
        transport = HttpClientTransport()
        mock_connection = mock.Mock()
        transport._connection = mock_connection

        transport.close()

        mock_connection.close.assert_called_once()
        assert transport._connection is None

    def test_close_without_connection(self):
        """Test closing transport without active connection."""
        transport = HttpClientTransport()

        # Should not raise any exception
        transport.close()
        assert transport._connection is None

    def test_repr(self):
        """Test string representation of HttpClientTransport."""
        transport = HttpClientTransport()
        repr_str = repr(transport)
        assert "HttpClientTransport" in repr_str


class TestSniSSLContext:
    """Test cases for SniSSLContext class."""

    def test_init(self):
        """Test SNI SSL context initialization."""
        hostname = "example.com"
        context = SniSSLContext(hostname, ssl.PROTOCOL_TLS_CLIENT)
        assert context.sni_hostname == hostname

    def test_wrap_socket_adds_server_hostname(self):
        """Test that wrap_socket adds server_hostname parameter."""
        hostname = "example.com"
        context = SniSSLContext(hostname, ssl.PROTOCOL_TLS_CLIENT)

        # Mock the parent wrap_socket method
        with mock.patch.object(ssl.SSLContext, "wrap_socket") as mock_wrap:
            mock_sock = mock.Mock()
            context.wrap_socket(mock_sock)

            # Verify server_hostname was added to kwargs
            mock_wrap.assert_called_once_with(mock_sock, server_hostname=hostname)


class TestHttpClientTransportIntegration:
    """Integration tests for HttpClientTransport with mocked HTTP connections."""

    def test_send_request_success(self):
        """Test successful request sending."""
        transport = HttpClientTransport()
        request = HttpRequest("GET", "https://example.com/test")

        # Mock the HTTP connection and response
        with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
            mock_conn = mock.Mock()
            mock_conn_class.return_value = mock_conn

            mock_response = mock.Mock()
            mock_response.status = 200
            mock_response.reason = "OK"
            mock_response.getheaders.return_value = [("content-type", "application/json")]
            mock_response.read.return_value = b'{"success": true}'
            mock_conn.getresponse.return_value = mock_response

            response = transport.send(request)

            # Verify connection was created and request was sent
            mock_conn_class.assert_called_once()
            mock_conn.request.assert_called_once_with("GET", "/test", body=None, headers=request.headers)

            # Verify response properties
            assert response.status_code == 200
            assert response.reason == "OK"
            assert response.headers["content-type"] == "application/json"

    def test_send_request_http_exception(self):
        """Test request sending with HTTP exception."""
        transport = HttpClientTransport()
        request = HttpRequest("GET", "https://example.com/test")

        with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
            mock_conn = mock.Mock()
            mock_conn_class.return_value = mock_conn
            mock_conn.request.side_effect = http.client.HTTPException("Connection failed")

            with pytest.raises(ServiceRequestError):
                transport.send(request)

    def test_send_request_ssl_error(self):
        """Test request sending with SSL error."""
        transport = HttpClientTransport()
        request = HttpRequest("GET", "https://example.com/test")

        with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
            mock_conn = mock.Mock()
            mock_conn_class.return_value = mock_conn
            mock_conn.request.side_effect = ssl.SSLError("SSL handshake failed")

            with pytest.raises(ServiceResponseError):
                transport.send(request)

    def test_send_request_with_proxy(self):
        """Test request sending through proxy."""
        proxy_endpoint = "https://proxy.example.com"
        transport = HttpClientTransport(proxy_endpoint=proxy_endpoint)
        request = HttpRequest("GET", "https://original.com/api/test")

        with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
            mock_conn = mock.Mock()
            mock_conn_class.return_value = mock_conn

            mock_response = mock.Mock()
            mock_response.status = 200
            mock_response.getheaders.return_value = []
            mock_response.read.return_value = b""
            mock_conn.getresponse.return_value = mock_response

            transport.send(request)

            # Verify connection was made to proxy host
            args, kwargs = mock_conn_class.call_args
            assert args[0] == "proxy.example.com"

            # Verify request was sent to proxy path
            mock_conn.request.assert_called_once()
            call_args = mock_conn.request.call_args
            method = call_args[0][0]  # First positional arg
            path = call_args[0][1]  # Second positional arg
            assert method == "GET"
            assert path == "/api/test"  # Original path

    def test_connection_reuse(self):
        """Test that connections are reused for multiple requests."""
        transport = HttpClientTransport()
        request1 = HttpRequest("GET", "https://example.com/test1")
        request2 = HttpRequest("GET", "https://example.com/test2")

        with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
            mock_conn = mock.Mock()
            mock_conn_class.return_value = mock_conn

            mock_response = mock.Mock()
            mock_response.status = 200
            mock_response.getheaders.return_value = []
            mock_response.read.return_value = b""
            mock_conn.getresponse.return_value = mock_response

            # Send two requests
            transport.send(request1)
            transport.send(request2)

            # Connection should be created only once
            assert mock_conn_class.call_count == 1
            # But request should be called twice
            assert mock_conn.request.call_count == 2

    def test_ca_file_change_invalidates_connection(self):
        """Test that CA file changes invalidate existing connections."""
        # Create test content that looks like PEM format but is just test data
        ca_content = "-----BEGIN CERTIFICATE-----\nMIIDummy certificate content here\n-----END CERTIFICATE-----"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_content)
            temp_file_path = temp_file.name

        try:
            # Mock the SSL context creation to avoid actual certificate validation
            with mock.patch("ssl.create_default_context") as mock_ssl_context:
                mock_ssl_context.return_value = mock.Mock()

                transport = HttpClientTransport(ca_file=temp_file_path)
                request = HttpRequest("GET", "https://example.com/test")

                with mock.patch("http.client.HTTPSConnection") as mock_conn_class:
                    mock_conn1 = mock.Mock()
                    mock_conn2 = mock.Mock()
                    mock_conn_class.side_effect = [mock_conn1, mock_conn2]

                    mock_response = mock.Mock()
                    mock_response.status = 200
                    mock_response.getheaders.return_value = []
                    mock_response.read.return_value = b""
                    mock_conn1.getresponse.return_value = mock_response
                    mock_conn2.getresponse.return_value = mock_response

                    # First request
                    transport.send(request)
                    assert mock_conn_class.call_count == 1

                    # Modify CA file
                    time.sleep(0.1)  # Ensure mtime changes
                    modified_content = ca_content.replace("Dummy", "Foo")
                    with open(temp_file_path, "w") as f:
                        f.write(modified_content)

                    # Second request should create new connection
                    transport.send(request)
                    assert mock_conn_class.call_count == 2

                    # First connection should be closed
                    mock_conn1.close.assert_called_once()

        finally:
            os.unlink(temp_file_path)


class TestHttpClientTransportResponse:
    """Test cases for HttpClientTransportResponse class."""

    def test_response_properties(self):
        """Test basic response properties."""
        request = HttpRequest("GET", "https://example.com/test")

        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.reason = "OK"
        mock_http_response.getheaders.return_value = [("Content-Type", "application/json"), ("Content-Length", "100")]
        mock_http_response.read.return_value = b'{"test": "data"}'

        response = transport.HttpClientTransportResponse(request, mock_http_response)

        assert response.status_code == 200
        assert response.reason == "OK"
        assert response.headers["content-type"] == "application/json"
        assert response.headers["content-length"] == "100"
        assert response.content == b'{"test": "data"}'
        assert response.text() == '{"test": "data"}'
        assert response.json() == {"test": "data"}
        assert response.url == "https://example.com/test"
        assert not response.is_closed
        # Stream is consumed after calling .content, .text(), or .json()
        assert response.is_stream_consumed

    def test_response_context_manager(self):
        """Test response as context manager."""
        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.getheaders.return_value = []

        response = transport.HttpClientTransportResponse(request, mock_http_response)

        with response as r:
            assert r is response
            assert not r.is_closed

        assert response.is_closed
        mock_http_response.close.assert_called_once()

    def test_response_raise_for_status_success(self):
        """Test raise_for_status with successful response."""
        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.getheaders.return_value = []

        response = transport.HttpClientTransportResponse(request, mock_http_response)

        # Should not raise any exception
        response.raise_for_status()

    def test_response_raise_for_status_error(self):
        """Test raise_for_status with error response."""
        from azure.core.exceptions import HttpResponseError

        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 404
        mock_http_response.getheaders.return_value = []

        response = transport.HttpClientTransportResponse(request, mock_http_response)

        with pytest.raises(HttpResponseError):
            response.raise_for_status()

    def test_response_iter_raw(self):
        """Test response iter_raw method."""
        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.getheaders.return_value = []
        mock_http_response.read.side_effect = [b"chunk1", b"chunk2", b""]

        response = transport.HttpClientTransportResponse(request, mock_http_response, block_size=6)

        chunks = list(response.iter_raw())
        assert chunks == [b"chunk1", b"chunk2"]

    def test_response_iter_bytes(self):
        """Test response iter_bytes method."""
        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.getheaders.return_value = []
        mock_http_response.read.side_effect = [b"chunk1", b"chunk2", b""]

        response = transport.HttpClientTransportResponse(request, mock_http_response, block_size=6)

        chunks = list(response.iter_bytes())
        assert chunks == [b"chunk1", b"chunk2"]

    def test_response_encoding(self):
        """Test response encoding property."""
        request = HttpRequest("GET", "https://example.com/test")
        mock_http_response = mock.Mock()
        mock_http_response.status = 200
        mock_http_response.getheaders.return_value = []
        mock_http_response.read.return_value = b"\xc3\xa9"  # é in UTF-8

        response = transport.HttpClientTransportResponse(request, mock_http_response)

        # Default encoding (UTF-8)
        assert response.text() == "é"

        # Create a new response for testing latin-1 encoding
        mock_http_response2 = mock.Mock()
        mock_http_response2.status = 200
        mock_http_response2.getheaders.return_value = []
        mock_http_response2.read.return_value = b"\xe9"  # é in Latin-1

        response2 = transport.HttpClientTransportResponse(request, mock_http_response2)
        response2.encoding = "latin-1"
        assert response2.text() == "é"

        # Test explicit encoding parameter overrides response encoding
        response2.encoding = "utf-8"
        assert response2.text(encoding="latin-1") == "é"


# Import the actual class for the response tests
from azure.identity._internal import http_client_transport as transport
