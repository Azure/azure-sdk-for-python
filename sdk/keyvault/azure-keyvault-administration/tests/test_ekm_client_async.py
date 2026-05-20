# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import base64
import pytest

from azure.core.exceptions import HttpResponseError
from azure.keyvault.administration import KeyVaultEkmConnection
from azure.keyvault.administration.aio import KeyVaultEkmClient
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION

from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultEkmClientPreparer
from _test_case import get_decorator
from _shared.test_case_async import KeyVaultTestCase

only_latest = get_decorator(api_versions=[DEFAULT_VERSION])

# Note: These tests require an EKM connection to be established with an EKM Sample Proxy.


class TestEkm(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.live_test_only
    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy_async
    async def test_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        ekm_host = kwargs.pop("ekm_host")
        server_ca_certificate = kwargs.pop("ekm_certificate")
        if not server_ca_certificate or not ekm_host:
            pytest.skip(
                "EKM CA certificate is required for live tests. Please set the EKM_PROXY_HOST and EKM_SERVER_CA_CERTIFICATE environment variables."
            )

        # Cleanup
        try:
            await client.delete_ekm_connection()
        except HttpResponseError:
            pass

        # Create an EKM connection
        ekm_connection = KeyVaultEkmConnection(
            host=ekm_host,
            server_ca_certificates=[base64.b64decode(server_ca_certificate)],
            path_prefix="/api/v1",
        )
        created_ekm_connection = await client.create_ekm_connection(connection=ekm_connection)
        assert created_ekm_connection is not None
        assert created_ekm_connection.host == ekm_host
        assert created_ekm_connection.server_ca_certificates is not None
        assert len(created_ekm_connection.server_ca_certificates) == 1
        assert created_ekm_connection.path_prefix == ekm_connection.path_prefix
        assert created_ekm_connection.server_subject_common_name == ekm_connection.server_subject_common_name

        # Get the EKM connection
        retrieved_ekm_connection = await client.get_ekm_connection()
        assert retrieved_ekm_connection is not None
        assert retrieved_ekm_connection.host == ekm_host
        assert retrieved_ekm_connection.server_ca_certificates is not None
        assert len(retrieved_ekm_connection.server_ca_certificates) == 1
        assert retrieved_ekm_connection.path_prefix == ekm_connection.path_prefix
        assert retrieved_ekm_connection.server_subject_common_name == created_ekm_connection.server_subject_common_name

        # Get the EKM certificate
        ekm_certificate = await client.get_ekm_certificate()
        assert ekm_certificate is not None
        assert ekm_certificate.ca_certificates is not None
        assert len(ekm_certificate.ca_certificates) == 1

        # Check the EKM connection status
        connection_status = await client.check_ekm_connection()
        assert connection_status is not None
        assert connection_status.api_version is not None
        assert connection_status.proxy_vendor is not None
        assert connection_status.proxy_name is not None
        assert connection_status.ekm_vendor is not None
        assert connection_status.ekm_product is not None

        # Update the EKM connection
        updated_ekm_connection = KeyVaultEkmConnection(
            host=ekm_host,
            server_ca_certificates=[base64.b64decode(server_ca_certificate)],
            path_prefix="/api/v1",
        )
        result = await client.update_ekm_connection(connection=updated_ekm_connection)
        assert result is not None
        assert result.host == updated_ekm_connection.host
        assert result.server_ca_certificates is not None
        assert len(result.server_ca_certificates) == 1
        assert result.path_prefix == updated_ekm_connection.path_prefix
        assert result.server_subject_common_name == updated_ekm_connection.server_subject_common_name

        # Delete the EKM connection
        result = await client.delete_ekm_connection()
        assert result is not None
        assert result.host == updated_ekm_connection.host
        assert result.server_ca_certificates is not None
        assert len(result.server_ca_certificates) == 1
        assert result.path_prefix == updated_ekm_connection.path_prefix
        assert result.server_subject_common_name == updated_ekm_connection.server_subject_common_name
