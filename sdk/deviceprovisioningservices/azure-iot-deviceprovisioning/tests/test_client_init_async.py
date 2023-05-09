import pytest
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.utils import parse_connection_string
from azure.iot.deviceprovisioning.aio import DeviceProvisioningClient

from azure.iot.deviceprovisioning import (
    generate_sas_token,
)
from conftest import ProvisioningServicePreparer
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async


class TestIndividualEnrollments(AzureRecordedTestCase):
    def create_provisioning_service_client_default_credentials(self, endpoint):
        credential = self.get_credential(DeviceProvisioningClient, is_async=True)
        client = DeviceProvisioningClient(endpoint=endpoint, credential=credential)
        return client

    def create_provisioning_service_client_namedkey(self, endpoint, name, key):
        credential = AzureNamedKeyCredential(name=name, key=key)
        client = DeviceProvisioningClient(endpoint=endpoint, credential=credential)
        return client

    def create_provisioning_service_client_sas(self, endpoint, sas_token):
        credential = AzureSasCredential(signature=sas_token)
        client = DeviceProvisioningClient(endpoint=endpoint, credential=credential)
        return client

    @pytest.mark.asyncio
    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_default_credentials(self, deviceprovisioningservices_endpoint):
        client = self.create_provisioning_service_client_default_credentials(
            deviceprovisioningservices_endpoint
        )

        enrollments = await client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        assert len(enrollments) == 0

    @pytest.mark.asyncio
    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_named_key(
        self, deviceprovisioningservices_endpoint, deviceprovisioningservices_conn_str
    ):
        # get name and key from token
        cs_parts = parse_connection_string(deviceprovisioningservices_conn_str)
        name = cs_parts["sharedaccesskeyname"]
        key = cs_parts["sharedaccesskey"]
        client = self.create_provisioning_service_client_namedkey(
            deviceprovisioningservices_endpoint, name, key
        )

        enrollments = await client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        assert len(enrollments) == 0

    @pytest.mark.asyncio
    @ProvisioningServicePreparer()
    @recorded_by_proxy_async
    async def test_sas_creds(self, deviceprovisioningservices_endpoint, deviceprovisioningservices_conn_str):
        cs_parts = parse_connection_string(deviceprovisioningservices_conn_str)
        
        name = cs_parts["sharedaccesskeyname"]
        key = cs_parts["sharedaccesskey"]
        
        sas = generate_sas_token(deviceprovisioningservices_endpoint, name, key)
        client = self.create_provisioning_service_client_sas(
            deviceprovisioningservices_endpoint,
            sas
        )

        enrollments = await client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        assert len(enrollments) == 0
