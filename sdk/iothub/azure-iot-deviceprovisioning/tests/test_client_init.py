import pytest
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.utils import parse_connection_string
from azure.iot.deviceprovisioning import DeviceProvisioningClient, generate_sas_token
from conftest import ProvisioningServicePreparer
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy


class TestIndividualEnrollments(AzureRecordedTestCase):
    def create_provisioning_service_client_default_credentials(self, endpoint):
        credential = self.get_credential(DeviceProvisioningClient)
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

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_default_credentials(self, iothub_dps_endpoint):
        client = self.create_provisioning_service_client_default_credentials(
            iothub_dps_endpoint
        )

        enrollments = client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )
        with pytest.raises(StopIteration):
            enrollments.next()

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_named_key(
        self, iothub_dps_endpoint, iothub_dps_conn_str
    ):
        # get name and key from token
        cs_parts = parse_connection_string(iothub_dps_conn_str)
        name = cs_parts["sharedaccesskeyname"]
        key = cs_parts["sharedaccesskey"]
        client = self.create_provisioning_service_client_namedkey(
            iothub_dps_endpoint, name, key
        )

        enrollments = client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        with pytest.raises(StopIteration):
            enrollments.next()

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_sas_creds(
        self, iothub_dps_endpoint, iothub_dps_conn_str
    ):
        cs_parts = parse_connection_string(iothub_dps_conn_str)

        name = cs_parts["sharedaccesskeyname"]
        key = cs_parts["sharedaccesskey"]

        sas = generate_sas_token(iothub_dps_endpoint, name, key)
        client = self.create_provisioning_service_client_sas(
            iothub_dps_endpoint, sas
        )

        enrollments = client.enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        with pytest.raises(StopIteration):
            enrollments.next()
