# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.programmableconnectivity.aio import ProgrammableConnectivityClient
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, set_function_recording_options
from devtools_testutils.aio import recorded_by_proxy_async

from azure.programmableconnectivity.models import (
    SimSwapVerificationContent,
    NetworkIdentifier,
    DeviceLocationVerificationContent,
    LocationDevice,
    SimSwapRetrievalContent,
    NumberVerificationWithoutCodeContent,
    NumberVerificationWithCodeContent,
)

subscription_id = os.environ.get("SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")

APC_GATEWAY_ID = f"/subscriptions/{subscription_id}/resourceGroups/dev-testing-eastus/providers/Microsoft.programmableconnectivity/gateways/apcg-eastus"
APC_GATEWAY_ID_BAD = f"/subscriptions/{subscription_id}/resourceGroups/dev-testing-eastus/providers/Microsoft.programmableconnectivity/gateways/non-existent"


# The numbers are fake.
class TestAzureProgrammableConnectivity(AzureRecordedTestCase):
    response_id = None
    client_response_id = None
    location_redirect = None

    def get_client_from_credentials(self):
        token = self.get_credential(ProgrammableConnectivityClient)
        client = ProgrammableConnectivityClient(
            endpoint="https://eastus.prod.apcgatewayapi.azure.com",
            credential=token,
        )
        return client

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_number_verification_without_code(self, **kwargs):
        set_function_recording_options(handle_redirects=False)

        def callback(response):
            self.location_redirect = response.http_response.headers.get("location")

        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")

        content = NumberVerificationWithoutCodeContent(
            phone_number="+34000000000", redirect_uri="https://somefakebackend.com", network_identifier=network_identifier
        )

        async with self.get_client_from_credentials() as client:
            await client.number_verification.verify_without_code(
                body=content, apc_gateway_id=APC_GATEWAY_ID, raw_response_hook=callback
                )
        
        print(f"self.location_redirect: {self.location_redirect}")

        assert self.location_redirect is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_number_verification_with_code(self, **kwargs):
        content = NumberVerificationWithCodeContent(apc_code="apc_1231231231232")

        async with self.get_client_from_credentials() as client:
            verified_response = await client.number_verification.verify_with_code(
                body=content, apc_gateway_id=APC_GATEWAY_ID
                )

        assert verified_response.verification_result is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_correlation_id(self, **kwargs):
        def callback(response):
            self.response_id = response.http_response.headers.get("x-ms-response-id")
            self.client_response_id = response.http_response.headers.get("x-ms-client-request-id")

        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+34000000000", max_age_hours=240, network_identifier=network_identifier
        )

        async with self.get_client_from_credentials() as client:
            await client.sim_swap.verify(
                body=content,
                apc_gateway_id=APC_GATEWAY_ID,
                raw_response_hook=callback,
                headers={"x-ms-client-request-id": "test_custom_id"},
            )

        assert self.response_id is not None
        assert self.client_response_id is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_sim_swap_mainline(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+34000000000", max_age_hours=240, network_identifier=network_identifier
        )
        async with self.get_client_from_credentials() as client:
            sim_swap_response = await client.sim_swap.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert sim_swap_response.verification_result is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_sim_swap_bad_response(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+34000000000", max_age_hours=-10, network_identifier=network_identifier
        )

        with pytest.raises(HttpResponseError) as exc_info:
            async with self.get_client_from_credentials() as client:
                await client.sim_swap.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_sim_swap_retrieval_success(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapRetrievalContent(phone_number="+34000000000", network_identifier=network_identifier)

        async with self.get_client_from_credentials() as client:
            sim_swap_retrieve_response = await client.sim_swap.retrieve(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert sim_swap_retrieve_response.date is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_device_location_verification_failure(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Telefonica_Brazil")
        location_device = LocationDevice(phone_number="+5500000000000")
        content = DeviceLocationVerificationContent(
            longitude=12.12, latitude=45.11, accuracy=10, device=location_device, network_identifier=network_identifier
        )

        async with self.get_client_from_credentials() as client:
            location_response = await client.device_location.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)

        assert location_response.verification_result is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_device_network_retrieval_success(self, **kwargs):
        network_content = NetworkIdentifier(identifier_type="IPv4", identifier="189.20.1.1")

        async with self.get_client_from_credentials() as client:
            network_response = await client.device_network.retrieve(body=network_content, apc_gateway_id=APC_GATEWAY_ID)

        assert network_response.network_code is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_device_network_retrieval_invalid_identifier_type(self, **kwargs):
        network_content = NetworkIdentifier(identifier_type="IPv5", identifier="189.20.1.1")
        with pytest.raises(HttpResponseError) as exc_info:
            async with self.get_client_from_credentials() as client:
                await client.device_network.retrieve(body=network_content, apc_gateway_id=APC_GATEWAY_ID)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_sim_swap_retrieval_with_bad_gateway_id(self, **kwargs):
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapRetrievalContent(phone_number="+34000000000", network_identifier=network_identifier)

        with pytest.raises(HttpResponseError) as exc_info:
            async with self.get_client_from_credentials() as client:
                await client.sim_swap.retrieve(body=content, apc_gateway_id=APC_GATEWAY_ID_BAD)

        assert exc_info.value.status_code == 400
