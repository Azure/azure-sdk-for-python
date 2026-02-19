# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore cafile ests
import os
import tempfile
import time
from unittest.mock import mock_open, MagicMock, patch

import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.identity import WorkloadIdentityCredential
from azure.identity._credentials.workload_identity import _get_transport

from helpers import mock_response, build_aad_response, GET_TOKEN_METHODS
from proxy_server import TokenProxyTestServer


PEM_CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")


@pytest.fixture(scope="module")
def ca_data() -> str:
    """Read CA certificate data from a PEM file for testing."""
    with open(PEM_CERT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_workload_identity_credential_initialize():
    tenant_id = "tenant-id"
    client_id = "client-id"

    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path="foo-path"
    )


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_workload_identity_credential_get_token(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    access_token = "foo"
    token_file_path = "foo-path"
    assertion = "foo-assertion"

    def send(request, **kwargs):
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        assert request.data.get("client_assertion") == assertion
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    transport = MagicMock(send=send)
    credential: WorkloadIdentityCredential = WorkloadIdentityCredential(
        tenant_id=tenant_id, client_id=client_id, token_file_path=token_file_path, transport=transport
    )

    open_mock = mock_open(read_data=assertion)
    with patch("builtins.open", open_mock):
        token = getattr(credential, get_token_method)("scope")
        assert token.token == access_token

    open_mock.assert_called_once_with(token_file_path, encoding="utf-8")


class TestWorkloadIdentityCredentialTokenProxy:
    """Test cases for WorkloadIdentityCredential with enable_azure_proxy=True."""

    def test_enable_azure_proxy_creates_custom_transport(self):
        """Test that enable_azure_proxy=True creates a custom transport with correct parameters."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        proxy_endpoint = "https://proxy.example.com:8080"
        sni_hostname = "sni.example.com"
        ca_file_path = "/path/to/ca.pem"

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
            "AZURE_KUBERNETES_SNI_NAME": sni_hostname,
            "AZURE_KUBERNETES_CA_FILE": ca_file_path,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

                mock_get_transport.assert_called_once_with(
                    sni=sni_hostname,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=ca_file_path,
                    ca_data=None,
                )

    def test_enable_azure_proxy_with_ca_data(self):
        """Test enable_azure_proxy with CA data instead of CA file."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        proxy_endpoint = "https://proxy.example.com:8080"
        ca_data = "-----BEGIN CERTIFICATE-----\nTest CA data\n-----END CERTIFICATE-----"

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
            "AZURE_KUBERNETES_CA_DATA": ca_data,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

                mock_get_transport.assert_called_once_with(
                    sni=None,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=None,
                    ca_data=ca_data,
                )

    def test_enable_azure_proxy_minimal_config(self):
        """Test enable_azure_proxy with minimal configuration (only proxy endpoint)."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        proxy_endpoint = "https://proxy.example.com:8080"

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

                mock_get_transport.assert_called_once_with(
                    sni=None,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=None,
                    ca_data=None,
                )

    def test_enable_azure_proxy_missing_proxy_endpoint(self):
        """Test that enable_azure_proxy=True without proxy endpoint uses the normal transport."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"

        # Ensure proxy endpoint env var is not set
        with patch.dict(os.environ, {}, clear=False):
            if "AZURE_KUBERNETES_TOKEN_PROXY" in os.environ:
                del os.environ["AZURE_KUBERNETES_TOKEN_PROXY"]

            with patch("azure.identity._credentials.workload_identity._get_transport") as mock_get_transport:
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )
                mock_get_transport.assert_not_called()

    def test_enable_azure_proxy_both_ca_file_and_data_raises_error(self):
        """Test that setting both CA file and CA data raises ValueError."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        proxy_endpoint = "https://proxy.example.com:8080"
        ca_file_path = "/path/to/ca.pem"
        ca_data = "-----BEGIN CERTIFICATE-----\nTest CA data\n-----END CERTIFICATE-----"

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
            "AZURE_KUBERNETES_CA_FILE": ca_file_path,
            "AZURE_KUBERNETES_CA_DATA": ca_data,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with pytest.raises(ValueError, match="Both AZURE_KUBERNETES_CA_FILE and AZURE_KUBERNETES_CA_DATA are set"):
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

    def test_enable_azure_proxy_missing_endpoint_with_custom_env_vars_raises_error(self):
        """Test that enable_azure_proxy=True without proxy endpoint but with other custom env vars raises ValueError."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        sni_hostname = "sni.example.com"
        ca_file_path = "/path/to/ca.pem"
        ca_data = "-----BEGIN CERTIFICATE-----\nTest CA data\n-----END CERTIFICATE-----"

        # Ensure proxy endpoint is not set
        if "AZURE_KUBERNETES_TOKEN_PROXY" in os.environ:
            del os.environ["AZURE_KUBERNETES_TOKEN_PROXY"]

        # Test with SNI set but no proxy endpoint
        env_vars_sni = {
            "AZURE_KUBERNETES_SNI_NAME": sni_hostname,
        }
        with patch.dict(os.environ, env_vars_sni, clear=False):
            with pytest.raises(ValueError):
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

        # Test with CA file set but no proxy endpoint
        env_vars_ca_file = {
            "AZURE_KUBERNETES_CA_FILE": ca_file_path,
        }
        with patch.dict(os.environ, env_vars_ca_file, clear=False):
            with pytest.raises(ValueError):
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

        # Test with CA data set but no proxy endpoint
        env_vars_ca_data = {
            "AZURE_KUBERNETES_CA_DATA": ca_data,
        }
        with patch.dict(os.environ, env_vars_ca_data, clear=False):
            with pytest.raises(ValueError):
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    enable_azure_proxy=True,
                )

    def test_enable_azure_proxy_false_does_not_create_transport(self):
        """Test that enable_azure_proxy=False (default) does not create a custom transport."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"

        with patch("azure.identity._credentials.workload_identity._get_transport") as mock_get_transport:
            WorkloadIdentityCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                token_file_path=token_file_path,
                enable_azure_proxy=False,
            )
            mock_get_transport.assert_not_called()


class TestCustomRequestsTransport:
    """Test cases for the custom RequestsTransport used by WorkloadIdentityCredential."""

    def test_get_transport_creates_custom_requests_transport(self, ca_data):
        """Test that _get_transport creates CustomRequestsTransport with correct parameters."""
        sni = "test.sni.com"
        proxy_endpoint = "https://proxy.example.com:8080"
        ca_file = PEM_CERT_PATH

        transport = _get_transport(
            sni=sni,
            token_proxy_endpoint=proxy_endpoint,
            ca_file=ca_file,
            ca_data=None,
        )

        assert transport is not None
        assert hasattr(transport, "_sni")
        assert hasattr(transport, "_proxy_endpoint")
        assert hasattr(transport, "_ca_file")
        assert hasattr(transport, "_ca_data")
        assert transport._sni == sni
        assert transport._proxy_endpoint == proxy_endpoint
        assert transport._ca_file == ca_file
        assert transport._ca_data == ca_data

    def test_get_transport_with_minimal_config(self):
        """Test _get_transport with minimal configuration."""
        proxy_endpoint = "https://proxy.example.com:8080"

        transport = _get_transport(
            sni=None,
            token_proxy_endpoint=proxy_endpoint,
            ca_file=None,
            ca_data=None,
        )

        assert transport is not None
        assert transport._sni is None
        assert transport._proxy_endpoint == proxy_endpoint
        assert transport._ca_file is None
        assert transport._ca_data is None

    def test_custom_requests_transport_inherits_from_token_binding_mixin(self):
        """Test that CustomRequestsTransport inherits from TokenBindingTransportMixin."""
        transport = _get_transport(
            sni="test.sni.com",
            token_proxy_endpoint="https://proxy.example.com:8080",
            ca_file=None,
            ca_data=None,
        )

        assert transport is not None

        # Verify inheritance from TokenBindingTransportMixin
        from azure.identity._internal.token_binding_transport_mixin import TokenBindingTransportMixin

        assert isinstance(transport, TokenBindingTransportMixin)

        # Verify TokenBindingTransportMixin methods are available
        assert hasattr(transport, "_update_request_url")
        assert hasattr(transport, "_has_ca_file_changed")
        assert hasattr(transport, "_load_ca_file_to_data")
        assert hasattr(transport, "_validate_url")


class TestCustomRequestsTransportWithLocalServer:
    """Integration tests using a local test server for CustomRequestsTransport."""

    def test_basic_https_request(self):
        """Test basic HTTPS request to test server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport with server's CA certificate
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None
            request = HttpRequest("GET", f"{server.base_url}/health")

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

    def test_post_request_with_body(self):
        """Test POST request with request body."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

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
            transport = _get_transport(
                sni=None, token_proxy_endpoint=server.base_url, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None

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
            transport = _get_transport(
                sni="1234.ests.aks", token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/health")
            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

            # Check an invalid SNI hostname
            transport = _get_transport(
                sni="unmatched.sni.hostname", token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None
            request = HttpRequest("GET", f"{server.base_url}/health")
            with pytest.raises(ServiceRequestError):
                transport.send(request)

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
                transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=temp_ca_path, ca_data=None)
                assert transport is not None

                # First request should work
                request = HttpRequest("GET", f"{server.base_url}/health")
                response1 = transport.send(request)
                assert response1.status_code == 200

                # Modify the CA file (add some content)
                time.sleep(0.1)
                with open(temp_ca_path, "a") as f:
                    f.write("\n# Modified for testing\n")

                # Second request should still work (using the same cert content)
                response2 = transport.send(request)
                assert transport._ca_data != original_content
                assert "Modified for testing" in transport._ca_data
                assert response2.status_code == 200

            finally:
                os.unlink(temp_ca_path)

    def test_ssl_error_handling(self):
        """Test SSL error handling."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport without proper CA file (will cause SSL error)
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=None, ca_data=None)
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/health")

            # Should raise SSL-related error
            with pytest.raises((ServiceRequestError, ServiceResponseError)):
                transport.send(request)

    def test_server_error_response(self):
        """Test handling of server error responses."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/error/500")

            response = transport.send(request)

            assert response.status_code == 500
            # Should not raise exception, just return error response

    def test_custom_headers_preserved(self):
        """Test that custom headers are preserved and sent to server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            custom_headers = {
                "Authorization": "Bearer test-token",
                "User-Agent": "CustomRequestsTransport/1.0",
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
            transport = _get_transport(
                sni=None, token_proxy_endpoint=server.base_url, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None

            # Request with query parameters
            original_url = "https://example.com/api/data?scope=read&limit=10&format=json"
            request = HttpRequest("GET", original_url)

            response = transport.send(request)

            assert response.status_code == 200
            data = response.json()

            # The path should include the query parameters
            expected_path = "/api/data?scope=read&limit=10&format=json"
            assert data["proxied_path"] == expected_path
