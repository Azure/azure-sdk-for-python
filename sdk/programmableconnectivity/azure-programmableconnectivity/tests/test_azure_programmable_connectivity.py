import os
import pytest
import logging
from azure.programmableconnectivity import ProgrammableConnectivityClient
from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

# logging.basicConfig(level=logging.DEBUG)

from azure.programmableconnectivity.models import (
    SimSwapVerificationContent,
    NetworkIdentifier,
    DeviceLocationVerificationContent,
    LocationDevice,
    SimSwapRetrievalContent,
)

tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
client_id = os.environ.get("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
client_secret = os.environ.get("AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
subscription_id = os.environ.get("SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret,
)

APC_GATEWAY_ID = f"/subscriptions/{subscription_id}/resourceGroups/dev-testing-eastus/providers/Microsoft.programmableconnectivity/gateways/apcg-eastus"
APC_GATEWAY_ID_BAD = f"/subscriptions/{subscription_id}/resourceGroups/dev-testing-eastus/providers/Microsoft.programmableconnectivity/gateways/non-existent"

# The api_version is given as a default in the SDK, so it is not necessary to specify it here.
client = ProgrammableConnectivityClient(
    endpoint="https://eastus.prod.apcgatewayapi.azure.com",
    credential=credential,
    # connection_verify=False,
)

# The numbers 14587443214 and 5547865461235 are fake.
class TestAzureProgrammableConnectivity(AzureRecordedTestCase):
    response_id = None
    client_response_id = None
    location_redirect = None

    @recorded_by_proxy
    def test_correlation_id(self, **kwargs):
        def callback(response):
            self.response_id = response.http_response.headers.get("x-ms-response-id")
            self.client_response_id = response.http_response.headers.get("x-ms-client-request-id")

        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+14587443214", max_age_hours=240, network_identifier=network_identifier
        )

        client.sim_swap.verify(
            body=content,
            apc_gateway_id=APC_GATEWAY_ID,
            raw_response_hook=callback,
            headers={"x-ms-client-request-id": "test_custom_id"},
        )

        assert self.response_id is not None
        assert self.client_response_id is not None

    @recorded_by_proxy
    def test_sim_swap_mainline(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+14587443214", max_age_hours=240, network_identifier=network_identifier
        )

        sim_swap_response = client.sim_swap.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert sim_swap_response.verification_result is not None

    @recorded_by_proxy
    def test_sim_swap_bad_response(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+14587443214", max_age_hours=-10, network_identifier=network_identifier
        )

        with pytest.raises(HttpResponseError) as exc_info:
            client.sim_swap.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert exc_info.value.status_code == 400

    @recorded_by_proxy
    def test_sim_swap_retrieval_success(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapRetrievalContent(phone_number="+14587443214", network_identifier=network_identifier)

        sim_swap_retrieve_response = client.sim_swap.retrieve(body=content, apc_gateway_id=APC_GATEWAY_ID)
        assert sim_swap_retrieve_response.date is not None

    @recorded_by_proxy
    def test_device_location_verification_failure(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Telefonica_Brazil")
        location_device = LocationDevice(phone_number="+5547865461235")
        content = DeviceLocationVerificationContent(
            longitude=12.12, latitude=45.11, accuracy=10, device=location_device, network_identifier=network_identifier
        )

        location_response = client.device_location.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)
        assert location_response.verification_result is not None

    @recorded_by_proxy
    def test_device_network_retrieval_success(self, **kwargs):
        network_content = NetworkIdentifier(identifier_type="IPv4", identifier="189.20.1.1")
        network_response = client.device_network.retrieve(body=network_content, apc_gateway_id=APC_GATEWAY_ID)

        assert network_response.network_code is not None

    @recorded_by_proxy
    def test_device_network_retrieval_invalid_identifier_type(self, **kwargs):
        network_content = NetworkIdentifier(identifier_type="IPv5", identifier="189.20.1.1")
        with pytest.raises(HttpResponseError) as exc_info:
            client.device_network.retrieve(body=network_content, apc_gateway_id=APC_GATEWAY_ID)

        assert exc_info.value.status_code == 400

    @recorded_by_proxy
    def test_sim_swap_retrieval_with_bad_gateway_id(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapRetrievalContent(phone_number="+14587443214", network_identifier=network_identifier)

        with pytest.raises(HttpResponseError) as exc_info:
            client.sim_swap.retrieve(body=content, apc_gateway_id=APC_GATEWAY_ID_BAD)

        assert exc_info.value.status_code == 400
