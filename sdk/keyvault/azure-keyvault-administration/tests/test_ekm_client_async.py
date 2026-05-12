# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError
from azure.keyvault.administration import (
    KeyVaultEkmConnection,
    KeyVaultEkmProxyClientCertificateInfo,
    KeyVaultEkmProxyInfo,
)
from azure.keyvault.administration.aio import KeyVaultEkmClient

from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultEkmClientPreparer
from _test_case import get_decorator
from _shared.test_case_async import KeyVaultTestCase


ekm_api_versions = get_decorator(api_versions=["2026-01-01-preview"])

_PROXY_CA_BYTES = b"\x30\x82\x01\x00"


def _build_connection(host: str = "ekm.contoso.com") -> KeyVaultEkmConnection:
    return KeyVaultEkmConnection(
        host=host,
        server_ca_certificates=[_PROXY_CA_BYTES],
        path_prefix="/api",
        server_subject_common_name="ekm.contoso.com",
    )


class TestEkmClient(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy_async
    async def test_ekm_connection_lifecycle(self, client: KeyVaultEkmClient, **kwargs):
        """Exercise create -> get -> update -> delete on an EKM connection."""
        try:
            await client.delete_ekm_connection()
        except HttpResponseError:
            pass

        created = await client.create_ekm_connection(_build_connection())
        assert isinstance(created, KeyVaultEkmConnection)
        assert created.host == "ekm.contoso.com"
        assert created.path_prefix == "/api"

        fetched = await client.get_ekm_connection()
        assert isinstance(fetched, KeyVaultEkmConnection)
        assert fetched.host == created.host
        assert fetched.path_prefix == created.path_prefix

        updated_input = _build_connection()
        updated_input.path_prefix = "/v2"
        updated = await client.update_ekm_connection(updated_input)
        assert updated.path_prefix == "/v2"

        deleted = await client.delete_ekm_connection()
        assert isinstance(deleted, KeyVaultEkmConnection)
        assert deleted.host == created.host

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy_async
    async def test_get_ekm_certificate(self, client: KeyVaultEkmClient, **kwargs):
        info = await client.get_ekm_certificate()
        assert isinstance(info, KeyVaultEkmProxyClientCertificateInfo)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", ekm_api_versions)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy_async
    async def test_check_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        try:
            await client.create_ekm_connection(_build_connection())
        except HttpResponseError:
            pass

        try:
            info = await client.check_ekm_connection()
            assert isinstance(info, KeyVaultEkmProxyInfo)
        finally:
            try:
                await client.delete_ekm_connection()
            except HttpResponseError:
                pass
