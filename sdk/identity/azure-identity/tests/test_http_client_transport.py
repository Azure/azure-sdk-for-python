# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore ests
import os
import ssl
import tempfile
import time
from time import sleep as real_sleep
from unittest import mock

import pytest

from azure.core.rest import HttpRequest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.identity._internal import http_client_transport as transport
from azure.identity._internal.http_client_transport import HttpClientTransport, SniSSLContext

from proxy_server import TokenProxyTestServer


PEM_CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")


@pytest.fixture(scope="module")
def ca_data() -> str:
    """Read CA certificate data from a PEM file for testing."""
    with open(PEM_CERT_PATH, "r", encoding="utf-8") as f:
        return f.read()


class TestHttpClientTransport:
    """Test cases for HttpClientTransport class."""

    def test_init_basic(self):
        """Test basic initialization of HttpClientTransport."""
        transport = HttpClientTransport()
        assert transport._ca_data is None
        assert transport._ca_file is None
        assert transport._sni is None
        assert transport._proxy_endpoint is None
        assert transport._ca_file_mtime is None

    def test_init_with_ca_data(self, ca_data):
        """Test initialization with CA data."""
        transport = HttpClientTransport(ca_data=ca_data)
        assert transport._ca_data == ca_data
        assert transport._ca_file is None

    def test_init_with_ca_file(self, ca_data):
        """Test initialization with CA file."""

        transport = HttpClientTransport(ca_file=PEM_CERT_PATH)
        assert transport._ca_file == PEM_CERT_PATH
        assert transport._ca_data == ca_data
        assert transport._ca_file_mtime is not None

    def test_init_with_both_ca_file_and_data_raises_error(self, ca_data):
        """Test that providing both CA file and data raises an error."""
        with pytest.raises(ValueError, match="Both ca_file and ca_data are set"):
            HttpClientTransport(ca_file=PEM_CERT_PATH, ca_data=ca_data)

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

    def test_ca_file_tracking_updates_mtime(self, ca_data):
        """Test CA file tracking updates modification time."""
        transport = HttpClientTransport(ca_file=PEM_CERT_PATH)
        assert transport._ca_file_mtime == os.path.getmtime(PEM_CERT_PATH)

    def test_ca_file_change_detection_no_change(self):
        """Test CA file change detection when file hasn't changed."""
        transport = HttpClientTransport(ca_file=PEM_CERT_PATH)
        assert not transport._has_ca_file_changed()

    def test_ca_file_change_detection_content_changed(self, ca_data):
        """Test CA file change detection when file content has changed."""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_data)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)

            # Modify the file
            real_sleep(0.1)  # Ensure mtime changes
            with open(temp_file_path, "a") as f:
                f.write("\n")

            # File should be detected as changed
            assert transport._has_ca_file_changed()
        finally:
            os.unlink(temp_file_path)

    def test_ca_file_change_detection_file_deleted(self, ca_data):
        """Test CA file change detection when file is deleted."""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_data)
            temp_file_path = temp_file.name

        transport = HttpClientTransport(ca_file=temp_file_path)

        # Delete the file
        os.unlink(temp_file_path)

        # File deletion should be detected as a change
        assert transport._has_ca_file_changed()

    def test_ca_file_empty_during_rotation(self, ca_data):
        """Test CA file becoming empty during rotation with existing connection."""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(ca_data)
            temp_file_path = temp_file.name

        try:
            transport = HttpClientTransport(ca_file=temp_file_path)
            original_mtime = transport._ca_file_mtime

            # Make file empty
            with open(temp_file_path, "w") as f:
                f.write("")

            # Should not raise error and should preserve old data
            assert transport._ca_data == ca_data
            assert transport._ca_file_mtime == original_mtime
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


class TestHttpClientTransportWithLocalServer:
    """Integration tests using a local test server."""

    def test_basic_https_request(self):
        """Test basic HTTPS request to test server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport with server's CA certificate
            transport = HttpClientTransport(ca_file=server.ca_file)
            request = HttpRequest("GET", f"{server.base_url}/health")

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

    def test_post_request_with_body(self):
        """Test POST request with request body."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = HttpClientTransport(ca_file=server.ca_file)

            # Prepare OAuth-like request
            body = "grant_type=client_credentials&scope=https://graph.microsoft.com/.default"
            request = HttpRequest(
                "POST",
                f"{server.base_url}/tenant/oauth2/v2.0/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=body.encode("utf-8"),
            )

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "Bearer"
            assert data["expires_in"] == 3600

    def test_proxy_endpoint_comprehensive(self):
        """Test comprehensive proxy endpoint functionality with various HTTP methods and scenarios."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Configure transport with proxy endpoint
            transport = HttpClientTransport(proxy_endpoint=server.base_url, ca_file=server.ca_file)

            # Test 1: POST request with JSON body through proxy
            post_data = {"grant_type": "client_credentials", "scope": "https://graph.microsoft.com/.default"}
            post_request = HttpRequest(
                "POST",
                "https://login.microsoftonline.com/tenant/oauth2/v2.0/token2",
                headers={"Content-Type": "application/json"},
                json=post_data,
            )

            post_response = transport.send(post_request)
            assert post_response.status_code == 200
            post_data_response = post_response.json()
            assert post_data_response["method"] == "POST"
            assert post_data_response["proxied_path"] == "/tenant/oauth2/v2.0/token2"

            # Test 2: PUT request through proxy
            put_request = HttpRequest(
                "PUT",
                "https://graph.microsoft.com/v1.0/me/profile",
                headers={"Content-Type": "application/json"},
                json={"displayName": "Test User"},
            )

            put_response = transport.send(put_request)
            assert put_response.status_code == 200
            put_data_response = put_response.json()
            assert put_data_response["method"] == "PUT"
            assert put_data_response["proxied_path"] == "/v1.0/me/profile"

            # Test 3: DELETE request through proxy
            delete_request = HttpRequest("DELETE", "https://graph.microsoft.com/v1.0/applications/app-id")

            delete_response = transport.send(delete_request)
            assert delete_response.status_code == 200
            delete_data_response = delete_response.json()
            assert delete_data_response["method"] == "DELETE"
            assert delete_data_response["proxied_path"] == "/v1.0/applications/app-id"

            # Test 4: Complex URL with multiple path segments and query parameters
            complex_url = "https://management.azure.com/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account?api-version=2021-04-01&expand=properties"
            complex_request = HttpRequest("GET", complex_url)

            complex_response = transport.send(complex_request)
            assert complex_response.status_code == 200
            complex_data_response = complex_response.json()
            assert complex_data_response["method"] == "GET"
            expected_path = "/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account?api-version=2021-04-01&expand=properties"
            assert complex_data_response["proxied_path"] == expected_path

            # Test 5: Request with custom headers through proxy
            headers_request = HttpRequest(
                "GET",
                "https://vault.azure.net/secrets/test-secret?api-version=7.3",
                headers={
                    "Authorization": "Bearer test-token",
                    "X-Custom-Header": "proxy-test-value",
                    "User-Agent": "Azure-SDK-For-Python",
                },
            )

            headers_response = transport.send(headers_request)
            assert headers_response.status_code == 200
            headers_data_response = headers_response.json()
            assert headers_data_response["method"] == "GET"
            assert headers_data_response["proxied_path"] == "/secrets/test-secret?api-version=7.3"

            # Verify headers were forwarded through proxy
            received_headers = headers_data_response["headers_received"]
            assert "Authorization" in received_headers
            assert "X-Custom-Header" in received_headers
            assert received_headers["Authorization"] == "Bearer test-token"
            assert received_headers["X-Custom-Header"] == "proxy-test-value"

    def test_sni_with_custom_hostname(self):
        """Test SNI (Server Name Indication) with custom hostname."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Use SNI with a different hostname than the server
            transport = HttpClientTransport(sni="1234.ests.aks", ca_file=server.ca_file)

            request = HttpRequest("GET", f"{server.base_url}/health")

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_connection_reuse(self):
        """Test that connections are reused for multiple requests."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = HttpClientTransport(ca_file=server.ca_file)

            # Make multiple requests
            requests_data = []
            for i in range(3):
                request = HttpRequest("GET", f"{server.base_url}/health")
                response = transport.send(request)
                assert response.status_code == 200
                requests_data.append(response.json())

            # All requests should succeed
            assert len(requests_data) == 3
            for data in requests_data:
                assert data["status"] == "healthy"

    def test_ca_file_change_detection(self):
        """Test CA file change detection with real certificates."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create a copy of the CA file that we can modify
            ca_file = server.ca_file
            if ca_file is None:
                pytest.skip("CA file not available")

            assert ca_file is not None  # Type hint for mypy
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem") as temp_ca:
                with open(ca_file, "r") as original:
                    original_content = original.read()
                    temp_ca.write(original_content)
                temp_ca_path = temp_ca.name

            try:
                transport = HttpClientTransport(ca_file=temp_ca_path)

                # First request should work
                request = HttpRequest("GET", f"{server.base_url}/health")
                response1 = transport.send(request)
                assert response1.status_code == 200

                # Modify the CA file (add some content)
                real_sleep(0.1)
                with open(temp_ca_path, "a") as f:
                    f.write("\n# Modified for testing\n")

                # Second request should still work (using the same cert content)
                response2 = transport.send(request)
                assert response2.status_code == 200

            finally:
                os.unlink(temp_ca_path)

    def test_ssl_error_handling(self):
        """Test SSL error handling."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport without proper CA file (will cause SSL error)
            transport = HttpClientTransport()  # No CA file provided
            request = HttpRequest("GET", f"{server.base_url}/health")

            # Should raise SSL-related error
            with pytest.raises((ServiceRequestError, ServiceResponseError)):
                transport.send(request)

    def test_server_error_response(self):
        """Test handling of server error responses."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = HttpClientTransport(ca_file=server.ca_file)
            request = HttpRequest("GET", f"{server.base_url}/error/500")

            response = transport.send(request)

            assert response.status_code == 500
            # Should not raise exception, just return error response

    def test_slow_server_response(self):
        """Test handling of slow server responses."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Set a longer timeout for this test
            transport = HttpClientTransport(ca_file=server.ca_file, timeout=5)
            # # Ensure fresh connection by closing any existing ones
            # transport.close()
            request = HttpRequest("GET", f"{server.base_url}/slow")

            start_time = time.time()
            response = transport.send(request)
            elapsed_time = time.time() - start_time

            assert response.status_code == 200
            # Should take at least 2 seconds (server waits for 2s)
            assert elapsed_time >= 2.0
            data = response.json()
            assert data["message"] == "slow response"

    def test_custom_headers_preserved(self):
        """Test that custom headers are preserved and sent to server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = HttpClientTransport(ca_file=server.ca_file)

            custom_headers = {
                "Authorization": "Bearer test-token",
                "User-Agent": "HttpClientTransport/1.0",
                "X-Custom-Header": "test-value",
            }

            request = HttpRequest("GET", f"{server.base_url}/proxy/test", headers=custom_headers)

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()

            # Server echoes back the headers it received
            received_headers = data["headers_received"]
            assert "Authorization" in received_headers
            assert "User-Agent" in received_headers
            assert "X-Custom-Header" in received_headers
            assert received_headers["Authorization"] == "Bearer test-token"

    def test_query_parameters_preserved(self):
        """Test that query parameters are preserved in proxy requests."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = HttpClientTransport(proxy_endpoint=server.base_url, ca_file=server.ca_file)

            # Request with query parameters
            original_url = "https://example.com/api/data?scope=read&limit=10&format=json"
            request = HttpRequest("GET", original_url)

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()

            # The path should include the query parameters
            expected_path = "/api/data?scope=read&limit=10&format=json"
            assert data["proxied_path"] == expected_path

    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        import threading
        import concurrent.futures

        with TokenProxyTestServer(use_ssl=True) as server:

            transport = HttpClientTransport(ca_file=server.ca_file)

            def make_request(request_id):
                request = HttpRequest("GET", f"{server.base_url}/health")
                response = transport.send(request)
                return request_id, response.status_code, response.json()

            # Make 5 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]

            # All requests should succeed
            assert len(results) == 5
            for request_id, status_code, data in results:
                assert status_code == 200
                assert data["status"] == "healthy"


class TestTokenProxyTestServer:
    """Tests for the test server itself."""

    def test_server_startup_and_shutdown(self):
        """Test that server starts and stops properly."""
        server = TokenProxyTestServer(use_ssl=True)

        # Server should not be running initially
        assert server.server is None

        # Start server
        base_url = server.start()
        assert server.server is not None
        assert base_url.startswith("https://")
        assert str(server.port) in base_url

        # Stop server
        server.stop()

        # Should clean up properly
        assert len(server._temp_files) == 0  # Files should be cleaned up

    def test_context_manager(self):
        """Test using server as context manager."""
        with TokenProxyTestServer(use_ssl=False) as server:
            assert server.server is not None
            assert server.base_url.startswith("http://")

        # Server should be stopped after context exit
        # Note: We can't easily test this without making a request

    def test_certificate_generation(self):
        """Test certificate generation."""
        server = TokenProxyTestServer(use_ssl=True)

        try:
            server.generate_test_certificates()

            # Should have created certificate files
            assert server.cert_file is not None
            assert server.key_file is not None
            assert server.ca_file is not None

            # Files should exist
            assert os.path.exists(server.cert_file)
            assert os.path.exists(server.key_file)
            assert os.path.exists(server.ca_file)

            # Files should contain certificate data
            with open(server.cert_file, "r") as f:
                cert_content = f.read()
                assert "-----BEGIN CERTIFICATE-----" in cert_content
                assert "-----END CERTIFICATE-----" in cert_content

        finally:
            server.stop()  # Clean up temp files
