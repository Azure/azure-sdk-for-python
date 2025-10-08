# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import tempfile
from unittest.mock import mock_open, patch, MagicMock

import pytest
from azure.identity.aio import WorkloadIdentityCredential
from azure.identity._internal.http_client_transport import HttpClientTransport

from helpers import mock_response, build_aad_response, GET_TOKEN_METHODS


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

    def test_use_token_proxy_creates_http_client_transport(self):
        """Test that use_token_proxy=True creates HttpClientTransport with correct parameters."""
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
            with patch("azure.identity.aio._credentials.workload_identity.HttpClientTransport") as mock_transport_class:
                mock_transport_instance = MagicMock()
                mock_transport_class.return_value = mock_transport_instance

                credential = WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                # Verify HttpClientTransport was called with correct parameters
                mock_transport_class.assert_called_once_with(
                    sni=sni_hostname,
                    proxy_endpoint=proxy_endpoint,
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
            with patch("azure.identity.aio._credentials.workload_identity.HttpClientTransport") as mock_transport_class:
                mock_transport_instance = MagicMock()
                mock_transport_class.return_value = mock_transport_instance

                credential = WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                # Verify HttpClientTransport was called with CA data
                mock_transport_class.assert_called_once_with(
                    sni=None,
                    proxy_endpoint=proxy_endpoint,
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
            with patch("azure.identity.aio._credentials.workload_identity.HttpClientTransport") as mock_transport_class:
                mock_transport_instance = MagicMock()
                mock_transport_class.return_value = mock_transport_instance

                credential = WorkloadIdentityCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    token_file_path=token_file_path,
                    use_token_proxy=True,
                )

                # Verify HttpClientTransport was called with minimal config
                mock_transport_class.assert_called_once_with(
                    sni=None,
                    proxy_endpoint=proxy_endpoint,
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

        # Mock the transport that would be created by HttpClientTransport
        mock_transport_instance = MagicMock(send=send)

        env_vars = {
            "AZURE_KUBERNETES_TOKEN_PROXY": proxy_endpoint,
        }

        with patch.dict(os.environ, env_vars, clear=False):
            with patch("azure.identity.aio._credentials.workload_identity.HttpClientTransport") as mock_transport_class:
                mock_transport_class.return_value = mock_transport_instance

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
        """Test that use_token_proxy=False (default) does not create HttpClientTransport."""
        tenant_id = "tenant-id"
        client_id = "client-id"
        token_file_path = "foo-path"

        with patch("azure.identity.aio._credentials.workload_identity.HttpClientTransport") as mock_transport_class:
            credential = WorkloadIdentityCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                token_file_path=token_file_path,
                use_token_proxy=False,
            )

            # Verify HttpClientTransport was NOT called
            mock_transport_class.assert_not_called()
