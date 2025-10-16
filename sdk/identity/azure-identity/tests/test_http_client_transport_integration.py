# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore ests
"""
Integration tests for HttpClientTransport using a real test server.

These tests verify the transport behavior with actual HTTP connections
instead of mocking, providing more realistic validation.
"""

import tempfile
import time
import os

import pytest

from azure.core.rest import HttpRequest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.identity._internal.http_client_transport import HttpClientTransport

# Import test server
try:
    from .test_server import TokenProxyTestServer
except ImportError:
    from test_server import TokenProxyTestServer


class TestHttpClientTransportIntegration:
    """Integration tests using a real test server."""

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
                f"{server.base_url}/oauth2/v2.0/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=body.encode("utf-8"),
            )

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "Bearer"
            assert data["expires_in"] == 3600

    def test_proxy_endpoint_request_routing(self):
        """Test that proxy endpoint correctly routes requests."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Configure transport with proxy endpoint
            transport = HttpClientTransport(proxy_endpoint=server.base_url, ca_file=server.ca_file)

            # Make request to a different host that will be routed through proxy
            original_url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"
            request = HttpRequest("GET", original_url)

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            # Verify the proxy received the correct path
            assert data["proxied_path"] == "/tenant/oauth2/v2.0/token"
            assert data["method"] == "GET"

    def test_proxy_endpoint_comprehensive(self):
        """Test comprehensive proxy endpoint functionality with various HTTP methods and scenarios."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Configure transport with proxy endpoint
            transport = HttpClientTransport(proxy_endpoint=server.base_url, ca_file=server.ca_file)

            # Test 1: POST request with JSON body through proxy
            post_data = {"grant_type": "client_credentials", "scope": "https://graph.microsoft.com/.default"}
            post_request = HttpRequest(
                "POST",
                "https://login.microsoftonline.com/tenant/oauth2/v2.0/token",
                headers={"Content-Type": "application/json"},
                json=post_data,
            )

            post_response = transport.send(post_request)
            assert post_response.status_code == 200
            post_data_response = post_response.json()
            assert post_data_response["method"] == "POST"
            assert post_data_response["proxied_path"] == "/tenant/oauth2/v2.0/token"

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
                time.sleep(0.1)  # Ensure mtime changes
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

            def make_request(request_id):
                # Create a separate transport instance for each thread
                # to avoid connection sharing issues
                transport = HttpClientTransport(ca_file=server.ca_file)
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
