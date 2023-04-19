from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.iot.deviceprovisioningservice import (
    ProvisioningServiceClient,
    parse_connection_string,
)
from conftest import ProvisioningServicePreparer
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy


class TestIndividualEnrollments(AzureRecordedTestCase):
    def create_provisioning_service_client_default_credentials(self, endpoint):
        credential = self.get_credential(ProvisioningServiceClient)
        client = ProvisioningServiceClient(endpoint=endpoint, credential=credential)
        return client

    def create_provisioning_service_client_namedkey(self, endpoint, name, key):
        credential = AzureNamedKeyCredential(name=name, key=key)
        client = ProvisioningServiceClient(endpoint=endpoint, credential=credential)
        return client

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_default_credentials(self, deviceprovisioningservices_endpoint):
        client = self.create_provisioning_service_client_default_credentials(
            deviceprovisioningservices_endpoint
        )

        enrollments = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        assert len(enrollments) == 0

    @ProvisioningServicePreparer()
    @recorded_by_proxy
    def test_named_key(
        self, deviceprovisioningservices_endpoint, deviceprovisioningservices_conn_str
    ):
        # get name and key from token
        cs_parts = parse_connection_string(deviceprovisioningservices_conn_str)
        name = cs_parts["SharedAccessKeyName"]
        key = cs_parts["SharedAccessKey"]
        client = self.create_provisioning_service_client_namedkey(
            deviceprovisioningservices_endpoint, name, key
        )

        enrollments = client.individual_enrollment.query(
            query_specification={"query": "SELECT *"}
        )

        assert len(enrollments) == 0
