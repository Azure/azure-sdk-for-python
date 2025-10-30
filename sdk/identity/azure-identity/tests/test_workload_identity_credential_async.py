# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore cafile aexit ests
import os
import tempfile
from time import sleep as real_sleep
from unittest.mock import mock_open, patch, MagicMock

import pytest
from azure.core.rest import HttpRequest
from azure.identity.aio import WorkloadIdentityCredential
from azure.identity.aio._credentials.workload_identity import _get_transport

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


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_workload_identity_credential_get_token(get_token_method):
    tenant_id = "tenant-id"
    client_id = "client-id"
    access_token = "foo"
    token_file_path = "foo-path"
    assertion = "foo-assertion"

    async def send(request, **kwargs):
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
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == access_token

    open_mock.assert_called_once_with(token_file_path, encoding="utf-8")


class TestWorkloadIdentityCredentialTokenProxyAsync:
    """Async test cases for WorkloadIdentityCredential with use_token_proxy=True."""

    def test_use_token_proxy_creates_custom_aiohttp_transport(self):
        """Test that use_token_proxy=True creates a custom aiohttp transport with correct parameters."""
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
            with patch("azure.identity.aio._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                mock_get_transport.assert_called_once_with(
                    sni=sni_hostname,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=ca_file_path,
                    ca_data=None,
                )

    def test_use_token_proxy_with_ca_data(self):
        """Test use_token_proxy with CA data instead of CA file."""
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
            with patch("azure.identity.aio._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )
                mock_get_transport.assert_called_once_with(
                    sni=None,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=None,
                    ca_data=ca_data,
                )

    def test_use_token_proxy_minimal_config(self):
        """Test use_token_proxy with minimal configuration (only proxy endpoint)."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"
        proxy_endpoint = "https://proxy.example.com:8080"

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity.aio._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_transport_instance = MagicMock()
                mock_get_transport.return_value = mock_transport_instance

                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                mock_get_transport.assert_called_once_with(
                    sni=None,
                    token_proxy_endpoint=proxy_endpoint,
                    ca_file=None,
                    ca_data=None,
                )

    def test_use_token_proxy_missing_proxy_endpoint_raises_error(self):
        """Test that use_token_proxy=True without proxy endpoint raises ValueError."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"

        # Ensure proxy endpoint env var is not set
        with patch.dict(os.environ, {}, clear=False):
            if "AZURE_KUBERNETES_TOKEN_PROXY" in os.environ:
                del os.environ["AZURE_KUBERNETES_TOKEN_PROXY"]

            with pytest.raises(ValueError, match="use_token_proxy is True, but no token proxy endpoint was found"):
                WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

    def test_use_token_proxy_both_ca_file_and_data_raises_error(self):
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
                    use_token_proxy=True,
                )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
    async def test_use_token_proxy_get_token_success(self, get_token_method):
        """Test successful token acquisition when using token proxy."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        access_token = "foo-access-token"
        token_file_path = "foo-path"
        assertion = "foo-assertion"
        proxy_endpoint = "https://proxy.example.com:8080"

        async def send(request, **kwargs):
            assert "claims" not in kwargs
            assert "tenant_id" not in kwargs
            assert request.data.get("client_assertion") == assertion
            return mock_response(json_payload=build_aad_response(access_token=access_token))

        mock_transport_instance = MagicMock(send=send)

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity.aio._credentials.workload_identity._get_transport") as mock_get_transport:
                mock_get_transport.return_value = mock_transport_instance

                credential = WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                open_mock = mock_open(read_data=assertion)
                with patch("builtins.open", open_mock):
                    token = await getattr(credential, get_token_method)("scope")
                    assert token.token == access_token

                open_mock.assert_called_once_with(token_file_path, encoding="utf-8")

    def test_use_token_proxy_false_does_not_create_transport(self):
        """Test that use_token_proxy=False (default) does not create a custom transport."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"

        with patch("azure.identity.aio._credentials.workload_identity._get_transport") as mock_get_transport:
            WorkloadIdentityCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                token_file_path=token_file_path,
                use_token_proxy=False,
            )
            mock_get_transport.assert_not_called()


class TestCustomAioHttpTransport:
    """Test cases for the custom AioHttpTransport used by WorkloadIdentityCredential."""

    def test_get_transport_creates_workload_identity_aiohttp_transport(self, ca_data):
        """Test that _get_transport creates WorkloadIdentityAioHttpTransport with correct parameters."""
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

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_send_with_sni(self):
        """Test that WorkloadIdentityAioHttpTransport.send sets server_hostname correctly."""
        sni = "test.sni.com"
        proxy_endpoint = "https://proxy.example.com:8080"

        transport = _get_transport(
            sni=sni,
            token_proxy_endpoint=proxy_endpoint,
            ca_file=None,
            ca_data=None,
        )
        assert transport is not None

        # Mock the parent send method
        mock_request = MagicMock()
        mock_request.url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"

        with patch.object(transport.__class__.__bases__[1], "send") as mock_parent_send:
            mock_parent_send.return_value = MagicMock()

            await transport.send(mock_request)

            # Verify parent send was called with server_hostname set
            mock_parent_send.assert_called_once()
            call_args = mock_parent_send.call_args
            assert call_args[1]["server_hostname"] == sni

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_send_updates_url(self):
        """Test that WorkloadIdentityAioHttpTransport.send updates request URL with proxy endpoint."""
        proxy_endpoint = "https://proxy.example.com:8080/path"
        original_url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"
        expected_url = "https://proxy.example.com:8080/path/tenant/oauth2/v2.0/token"

        transport = _get_transport(
            sni=None,
            token_proxy_endpoint=proxy_endpoint,
            ca_file=None,
            ca_data=None,
        )
        assert transport is not None

        mock_request = MagicMock()
        mock_request.url = original_url

        with patch.object(transport.__class__.__bases__[1], "send") as mock_parent_send:
            mock_parent_send.return_value = MagicMock()

            await transport.send(mock_request)

            # Verify URL was updated to use proxy endpoint
            assert mock_request.url == expected_url

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_send_with_ca_data(self, ca_data):
        """Test that WorkloadIdentityAioHttpTransport.send creates SSL context from CA data."""
        proxy_endpoint = "https://proxy.example.com:8080"

        transport = _get_transport(
            sni=None,
            token_proxy_endpoint=proxy_endpoint,
            ca_file=None,
            ca_data=ca_data,
        )
        assert transport is not None

        mock_request = MagicMock()
        mock_request.url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"

        with patch.object(transport.__class__.__bases__[1], "send") as mock_parent_send:
            mock_parent_send.return_value = MagicMock()

            await transport.send(mock_request)

            # Verify SSL context was set
            mock_parent_send.assert_called_once()
            call_args = mock_parent_send.call_args
            assert "ssl" in call_args[1]
            assert call_args[1]["ssl"] is not None

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_send_with_ca_file_reload(self, ca_data):
        """Test that WorkloadIdentityAioHttpTransport.send reloads CA file when changed."""

        # Create a temporary CA file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem") as ca_file:
            ca_file.write(ca_data)
            ca_file_path = ca_file.name

        try:
            proxy_endpoint = "https://proxy.example.com:8080"

            transport = _get_transport(
                sni=None,
                token_proxy_endpoint=proxy_endpoint,
                ca_file=ca_file_path,
                ca_data=None,
            )

            assert transport is not None
            # Store original CA data
            original_ca_data = transport._ca_data

            # Simulate file change by modifying mtime tracking
            real_sleep(0.1)  # Ensure different mtime
            with open(ca_file_path, "a") as f:
                f.write("\n")

            mock_request = MagicMock()
            mock_request.url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"

            with patch.object(transport.__class__.__bases__[1], "send") as mock_parent_send:
                mock_parent_send.return_value = MagicMock()

                await transport.send(mock_request)

                # Verify CA data was reloaded
                assert transport._ca_data != original_ca_data

        finally:
            # Clean up temporary file
            os.unlink(ca_file_path)

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_context_manager(self):
        """Test that WorkloadIdentityAioHttpTransport works as async context manager."""
        transport = _get_transport(
            sni=None,
            token_proxy_endpoint="https://proxy.example.com:8080",
            ca_file=None,
            ca_data=None,
        )
        assert transport is not None

        # Mock the parent context manager methods
        with patch.object(transport.__class__.__bases__[1], "__aenter__") as mock_aenter, patch.object(
            transport.__class__.__bases__[1], "__aexit__"
        ) as mock_aexit:

            mock_aenter.return_value = transport
            mock_aexit.return_value = None

            async with transport as ctx_transport:
                assert ctx_transport == transport

            mock_aenter.assert_called_once()
            mock_aexit.assert_called_once()

    def test_workload_identity_aiohttp_transport_initialization_with_ca_data(self, ca_data):
        """Test WorkloadIdentityAioHttpTransport initialization with CA data creates SSL context."""
        transport = _get_transport(
            sni=None,
            token_proxy_endpoint="https://proxy.example.com:8080",
            ca_file=None,
            ca_data=ca_data,
        )
        assert transport is not None

        # Verify SSL context was created during initialization
        assert hasattr(transport, "_ssl_context")
        assert transport._ssl_context is not None

    def test_workload_identity_aiohttp_transport_initialization_without_ca_data(self):
        """Test WorkloadIdentityAioHttpTransport initialization without CA data."""
        transport = _get_transport(
            sni=None,
            token_proxy_endpoint="https://proxy.example.com:8080",
            ca_file=None,
            ca_data=None,
        )
        assert transport is not None

        # Verify SSL context is created with None ca_data (creates default context)
        assert hasattr(transport, "_ssl_context")
        # SSL context should still be created even with None ca_data

    @pytest.mark.asyncio
    async def test_workload_identity_aiohttp_transport_send_no_ssl_context_when_no_ca_data(self):
        """Test that no SSL context is passed when ca_data is None and SSL context creation fails."""
        transport = _get_transport(
            sni=None,
            token_proxy_endpoint="https://proxy.example.com:8080",
            ca_file=None,
            ca_data=None,
        )
        assert transport is not None

        # Mock SSL context creation to return None
        with patch("ssl.create_default_context", return_value=None):
            # Manually set ssl_context to None to test the conditional logic
            with patch.object(transport, "_ssl_context", None):
                mock_request = MagicMock()
                mock_request.url = "https://login.microsoftonline.com/tenant/oauth2/v2.0/token"

                with patch.object(transport.__class__.__bases__[1], "send") as mock_parent_send:
                    mock_parent_send.return_value = MagicMock()

                    await transport.send(mock_request)

                    # Verify SSL context was not set when None
                    mock_parent_send.assert_called_once()
                    call_args = mock_parent_send.call_args
                    assert "ssl" not in call_args[1] or call_args[1].get("ssl") is None

    def test_workload_identity_aiohttp_transport_inherits_from_token_binding_mixin(self):
        """Test that WorkloadIdentityAioHttpTransport inherits from TokenBindingTransportMixin."""
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


class TestCustomAioHttpTransportWithLocalServer:
    """Integration tests using a local test server for WorkloadIdentityAioHttpTransport."""

    @pytest.mark.asyncio
    async def test_basic_https_request(self):
        """Test basic HTTPS request to test server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport with server's CA certificate
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None
            request = HttpRequest("GET", f"{server.base_url}/health")

            response = await transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_post_request_with_body(self):
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

            response = await transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "Bearer"
            assert data["expires_in"] == 3600

    @pytest.mark.asyncio
    async def test_proxy_endpoint_comprehensive(self):
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

            post_response = await transport.send(post_request)
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

            put_response = await transport.send(put_request)
            assert put_response.status_code == 200
            put_data_response = put_response.json()
            assert put_data_response["method"] == "PUT"
            assert put_data_response["proxied_path"] == "/v1.0/me/profile"

            # Test 3: DELETE request through proxy
            delete_request = HttpRequest("DELETE", "https://graph.microsoft.com/v1.0/applications/app-id")

            delete_response = await transport.send(delete_request)
            assert delete_response.status_code == 200
            delete_data_response = delete_response.json()
            assert delete_data_response["method"] == "DELETE"
            assert delete_data_response["proxied_path"] == "/v1.0/applications/app-id"

            # Test 4: Complex URL with multiple path segments and query parameters
            complex_url = "https://management.azure.com/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account?api-version=2021-04-01&expand=properties"
            complex_request = HttpRequest("GET", complex_url)

            complex_response = await transport.send(complex_request)
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

            headers_response = await transport.send(headers_request)
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

    @pytest.mark.asyncio
    async def test_sni_with_custom_hostname(self):
        """Test SNI (Server Name Indication) with custom hostname."""
        with TokenProxyTestServer(use_ssl=True) as server:
            # Use SNI with a different hostname than the server
            transport = _get_transport(
                sni="1234.ests.aks", token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/health")

            response = await transport.send(request)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_ca_file_change_detection(self):
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
                response1 = await transport.send(request)
                assert response1.status_code == 200

                # Modify the CA file (add some content)
                real_sleep(0.1)
                with open(temp_ca_path, "a") as f:
                    f.write("\n# Modified for testing\n")

                # Second request should still work (using the same cert content)
                response2 = await transport.send(request)
                assert response2.status_code == 200

            finally:
                os.unlink(temp_ca_path)

    @pytest.mark.asyncio
    async def test_ssl_error_handling(self):
        """Test SSL error handling."""
        from azure.core.exceptions import ServiceRequestError, ServiceResponseError

        with TokenProxyTestServer(use_ssl=True) as server:
            # Create transport without proper CA file (will cause SSL error)
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=None, ca_data=None)
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/health")

            # Should raise SSL-related error
            with pytest.raises((ServiceRequestError, ServiceResponseError)):
                await transport.send(request)

    @pytest.mark.asyncio
    async def test_server_error_response(self):
        """Test handling of server error responses."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/error/500")

            response = await transport.send(request)

            assert response.status_code == 500
            # Should not raise exception, just return error response

    @pytest.mark.asyncio
    async def test_slow_server_response(self):
        """Test handling of slow server responses."""
        import time

        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            request = HttpRequest("GET", f"{server.base_url}/slow")

            start_time = time.time()
            response = await transport.send(request)
            elapsed_time = time.time() - start_time

            assert response.status_code == 200
            # Should take at least 2 seconds (server waits for 2s)
            assert elapsed_time >= 2.0
            data = response.json()
            assert data["message"] == "slow response"

    @pytest.mark.asyncio
    async def test_custom_headers_preserved(self):
        """Test that custom headers are preserved and sent to server."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            custom_headers = {
                "Authorization": "Bearer test-token",
                "User-Agent": "WorkloadIdentityAioHttpTransport/1.0",
                "X-Custom-Header": "test-value",
            }

            request = HttpRequest("GET", f"{server.base_url}/proxy/test", headers=custom_headers)

            response = await transport.send(request)

            assert response.status_code == 200
            data = response.json()

            # Server echoes back the headers it received
            received_headers = data["headers_received"]
            assert "Authorization" in received_headers
            assert "User-Agent" in received_headers
            assert "X-Custom-Header" in received_headers
            assert received_headers["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_query_parameters_preserved(self):
        """Test that query parameters are preserved in proxy requests."""
        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(
                sni=None, token_proxy_endpoint=server.base_url, ca_file=server.ca_file, ca_data=None
            )
            assert transport is not None

            # Request with query parameters
            original_url = "https://example.com/api/data?scope=read&limit=10&format=json"
            request = HttpRequest("GET", original_url)

            response = await transport.send(request)

            assert response.status_code == 200
            data = response.json()

            # The path should include the query parameters
            expected_path = "/api/data?scope=read&limit=10&format=json"
            assert data["proxied_path"] == expected_path

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        import asyncio

        with TokenProxyTestServer(use_ssl=True) as server:
            transport = _get_transport(sni=None, token_proxy_endpoint=None, ca_file=server.ca_file, ca_data=None)
            assert transport is not None

            async def make_request(request_id):
                request = HttpRequest("GET", f"{server.base_url}/health")
                response = await transport.send(request)
                return request_id, response.status_code, response.json()

            # Make 5 concurrent requests
            tasks = [make_request(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # All requests should succeed
            assert len(results) == 5
            for request_id, status_code, data in results:
                assert status_code == 200
                assert data["status"] == "healthy"
