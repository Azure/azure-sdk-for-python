# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import base64
import pytest

from azure.core.exceptions import HttpResponseError
from azure.keyvault.administration import (
    KeyVaultEkmClient,
    KeyVaultEkmConnection,
    KeyVaultEkmPrivateEndpointOperationStatus,
    KeyVaultEkmPrivateEndpointOperationType,
)
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION

from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultEkmClientPreparer, get_decorator

only_latest = get_decorator(api_versions=[DEFAULT_VERSION])

# Note: These tests require an EKM connection to be established with an EKM Sample Proxy.


class TestEkm(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_ekm_connection(self, client: KeyVaultEkmClient, **kwargs):
        ekm_host = kwargs.pop("ekm_host")
        server_ca_certificate = kwargs.pop("ekm_certificate")
        if not server_ca_certificate or not ekm_host:
            pytest.skip(
                "EKM CA certificate is required for live tests. Please set the EKM_PROXY_HOST and EKM_SERVER_CA_CERTIFICATE environment variables."
            )

        # Cleanup
        try:
            client.delete_ekm_connection()
        except HttpResponseError:
            pass

        # Create an EKM connection
        ekm_connection = KeyVaultEkmConnection(
            host=ekm_host,
            server_ca_certificates=[base64.b64decode(server_ca_certificate)],
            path_prefix="/api/v1",
        )
        created_ekm_connection = client.create_ekm_connection(connection=ekm_connection)
        assert created_ekm_connection is not None
        assert created_ekm_connection.host == ekm_host
        assert created_ekm_connection.server_ca_certificates is not None
        assert len(created_ekm_connection.server_ca_certificates) == 1
        assert created_ekm_connection.path_prefix == ekm_connection.path_prefix
        assert created_ekm_connection.server_subject_common_name == ekm_connection.server_subject_common_name

        # Get the EKM connection
        retrieved_ekm_connection = client.get_ekm_connection()
        assert retrieved_ekm_connection is not None
        assert retrieved_ekm_connection.host == ekm_host
        assert retrieved_ekm_connection.server_ca_certificates is not None
        assert len(retrieved_ekm_connection.server_ca_certificates) == 1
        assert retrieved_ekm_connection.path_prefix == ekm_connection.path_prefix
        assert retrieved_ekm_connection.server_subject_common_name == created_ekm_connection.server_subject_common_name

        # Get the EKM certificate
        ekm_certificate = client.get_ekm_certificate()
        assert ekm_certificate is not None
        assert ekm_certificate.ca_certificates is not None
        assert len(ekm_certificate.ca_certificates) == 1

        # Check the EKM connection status
        connection_status = client.check_ekm_connection()
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
        result = client.update_ekm_connection(connection=updated_ekm_connection)
        assert result is not None
        assert result.host == updated_ekm_connection.host
        assert result.server_ca_certificates is not None
        assert len(result.server_ca_certificates) == 1
        assert result.path_prefix == updated_ekm_connection.path_prefix
        assert result.server_subject_common_name == updated_ekm_connection.server_subject_common_name

        # Delete the EKM connection
        result = client.delete_ekm_connection()
        assert result is not None
        assert result.host == updated_ekm_connection.host
        assert result.server_ca_certificates is not None
        assert len(result.server_ca_certificates) == 1
        assert result.path_prefix == updated_ekm_connection.path_prefix
        assert result.server_subject_common_name == updated_ekm_connection.server_subject_common_name

    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultEkmClientPreparer()
    @recorded_by_proxy
    def test_ekm_private_endpoint(self, client: KeyVaultEkmClient, **kwargs):
        private_link_service_id = kwargs.pop("private_link_service_id")
        if not private_link_service_id:
            pytest.skip(
                "An EKM Private Link Service is required for live tests. Please set the EKM_PRIVATE_LINK_SERVICE_ID environment variable."
            )
        private_endpoint_name = self.get_resource_name("ekm-pe")

        # Cleanup
        try:
            client.begin_delete_ekm_private_endpoint(private_endpoint_name).wait()
        except HttpResponseError:
            pass

        # Create a private endpoint
        create_operation = client.begin_create_ekm_private_endpoint(
            private_endpoint_name, private_link_service_id, request_message="Please approve"
        ).result()
        assert create_operation is not None
        assert create_operation.private_endpoint_name == private_endpoint_name
        assert create_operation.operation_type == KeyVaultEkmPrivateEndpointOperationType.CREATE
        assert create_operation.status == KeyVaultEkmPrivateEndpointOperationStatus.SUCCEEDED

        # Get the private endpoint
        private_endpoint = client.get_ekm_private_endpoint(private_endpoint_name)
        assert private_endpoint is not None
        assert private_endpoint.name == private_endpoint_name
        assert private_endpoint.provisioning_state is not None
        assert private_endpoint.properties is not None
        assert private_endpoint.properties.private_link_service_id == private_link_service_id
        assert private_endpoint.private_link_service_connection_state is not None
        assert private_endpoint.private_link_service_connection_state.status is not None

        # List the private endpoints
        private_endpoints = list(client.list_ekm_private_endpoints())
        assert any(endpoint.name == private_endpoint_name for endpoint in private_endpoints)

        # Delete the private endpoint
        delete_operation = client.begin_delete_ekm_private_endpoint(private_endpoint_name).result()
        assert delete_operation is not None
        assert delete_operation.private_endpoint_name == private_endpoint_name
        assert delete_operation.operation_type == KeyVaultEkmPrivateEndpointOperationType.DELETE
        assert delete_operation.status == KeyVaultEkmPrivateEndpointOperationStatus.SUCCEEDED

        # The delete operation's status can still be retrieved by its job ID
        if delete_operation.job_id:
            operation_status = client.get_ekm_private_endpoint_operation_status(delete_operation.job_id)
            assert operation_status.job_id == delete_operation.job_id
            assert operation_status.status == KeyVaultEkmPrivateEndpointOperationStatus.SUCCEEDED
