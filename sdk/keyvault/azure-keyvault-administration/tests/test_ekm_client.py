# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError
from azure.keyvault.administration import (
    KeyVaultEkmClient,
    KeyVaultEkmConnection,
    KeyVaultEkmProxyClientCertificateInfo,
    KeyVaultEkmProxyInfo,
)
from azure.keyvault.administration._generated.models import EkmConnection as _GeneratedEkmConnection

from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultEkmClientPreparer, get_decorator


# EKM operations are only available on the 2026-01-01-preview API version.
ekm_api_versions = get_decorator(api_versions=["2026-01-01-preview"])

# Minimal placeholder bytes; real ca certificates are PEM/DER chains pinned to your EKM proxy.
_PROXY_CA_BYTES = b"\x30\x82\x01\x00"


def _build_connection(host: str = "ekm.contoso.com") -> KeyVaultEkmConnection:
    return KeyVaultEkmConnection(
        host=host,
        server_ca_certificates=[_PROXY_CA_BYTES],
        path_prefix="/api",
        server_subject_common_name="ekm.contoso.com",
    )


class TestEkmModels:
    """Unit tests for EKM public model wrappers (no service interaction)."""

    def test_ekm_connection_init_required_and_optional_fields(self):
        connection = _build_connection()
        assert connection.host == "ekm.contoso.com"
        assert connection.server_ca_certificates == [_PROXY_CA_BYTES]
        assert connection.path_prefix == "/api"
        assert connection.server_subject_common_name == "ekm.contoso.com"

    def test_ekm_connection_optional_fields_default_to_none(self):
        connection = KeyVaultEkmConnection(host="h.example", server_ca_certificates=[_PROXY_CA_BYTES])
        assert connection.path_prefix is None
        assert connection.server_subject_common_name is None

    def test_ekm_connection_repr_includes_host(self):
        connection = _build_connection("repr.example.net")
        assert "repr.example.net" in repr(connection)

    def test_ekm_connection_round_trip_to_and_from_generated(self):
        original = _build_connection()
        generated = original._to_generated()
        assert isinstance(generated, _GeneratedEkmConnection)
        assert generated.host == original.host
        assert generated.server_ca_certificates == original.server_ca_certificates
        assert generated.path_prefix == original.path_prefix
        assert generated.server_subject_common_name == original.server_subject_common_name

        round_tripped = KeyVaultEkmConnection._from_generated(generated)
        assert round_tripped.host == original.host
        assert round_tripped.server_ca_certificates == original.server_ca_certificates
        assert round_tripped.path_prefix == original.path_prefix
        assert round_tripped.server_subject_common_name == original.server_subject_common_name

    def test_ekm_proxy_client_certificate_info_kwargs(self):
        info = KeyVaultEkmProxyClientCertificateInfo(
            ca_certificates=[_PROXY_CA_BYTES], subject_common_name="ekm-client.contoso.com"
        )
        assert info.ca_certificates == [_PROXY_CA_BYTES]
        assert info.subject_common_name == "ekm-client.contoso.com"
        assert "ekm-client.contoso.com" in repr(info)

    def test_ekm_proxy_info_kwargs(self):
        info = KeyVaultEkmProxyInfo(
            api_version="2.0", proxy_vendor="Contoso", proxy_name="ProxyX 1.2", ekm_vendor="Acme", ekm_product="HSM 9000"
        )
        assert info.api_version == "2.0"
        assert info.proxy_vendor == "Contoso"
        assert info.proxy_name == "ProxyX 1.2"
        assert info.ekm_vendor == "Acme"
        assert info.ekm_product == "HSM 9000"
        rendered = repr(info)
        assert "Contoso" in rendered and "Acme" in rendered


class TestEkmClient(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_ekm_connection_lifecycle(self, client: KeyVaultEkmClient, **kwargs):
        """Exercise create -> get -> update -> delete on an EKM connection."""
        # Pre-condition: there should not be an existing EKM connection.
        # If the recording was made against a clean HSM, delete is a no-op below.
        try:
            client.delete_ekm_connection()
        except HttpResponseError:
            pass

        # Create
        created = client.create_ekm_connection(_build_connection())
        assert isinstance(created, KeyVaultEkmConnection)
        assert created.host == "ekm.contoso.com"
        assert created.path_prefix == "/api"

        # Get
        fetched = client.get_ekm_connection()
        assert isinstance(fetched, KeyVaultEkmConnection)
        assert fetched.host == created.host
        assert fetched.path_prefix == created.path_prefix

        # Update
        updated_input = _build_connection()
        updated_input.path_prefix = "/v2"
        updated = client.update_ekm_connection(updated_input)
        assert updated.path_prefix == "/v2"

        # Delete
        deleted = client.delete_ekm_connection()
        assert isinstance(deleted, KeyVaultEkmConnection)
        assert deleted.host == created.host

    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_get_ekm_certificate(self, client: KeyVaultEkmClient, **kwargs):
        """The EKM proxy client certificate info should always be retrievable."""
        info = client.get_ekm_certificate()
        assert isinstance(info, KeyVaultEkmProxyClientCertificateInfo)
        # The service may return either populated certificate info or an empty payload
        # depending on EKM provisioning state. Both are valid response shapes.

    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_check_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        """Verify check_ekm_connection returns proxy info when an EKM proxy is reachable."""
        try:
            client.create_ekm_connection(_build_connection())
        except HttpResponseError:
            # An EKM connection may already exist from a previous test/recording
            pass

        try:
            info = client.check_ekm_connection()
            assert isinstance(info, KeyVaultEkmProxyInfo)
        finally:
            try:
                client.delete_ekm_connection()
            except HttpResponseError:
                pass
