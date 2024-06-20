    # ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.programmableconnectivity.aio import ProgrammableConnectivityClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.programmableconnectivity.models import (
    SimSwapVerificationContent,
    NetworkIdentifier,
    SimSwapRetrievalContent,
)
import asyncio

def create_client():
    return ProgrammableConnectivityClient(endpoint="<endpoint>", credential=DefaultAzureCredential())

async def main():
    APC_GATEWAY_ID = "/subscriptions/<subscription_id>/resourceGroups/.../.../..."

    # Verify
    try:
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapVerificationContent(
            phone_number="+14587443214", max_age_hours=240, network_identifier=network_identifier
        )
        async with create_client() as client:
            sim_swap_response = await client.sim_swap.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)
            print(sim_swap_response.verification_result)
    except HttpResponseError as e:
        print("service responds error: {}".format(e.response.json()))

    # Retrieve
    try:
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Orange_Spain")
        content = SimSwapRetrievalContent(phone_number="+14587443214", network_identifier=network_identifier)
        async with create_client() as client:
            sim_swap_retrieve_response = await client.sim_swap.retrieve(body=content, apc_gateway_id=APC_GATEWAY_ID)
            print(sim_swap_retrieve_response.date)
    except HttpResponseError as e:
        print("service responds error: {}".format(e.response.json()))

if __name__ == "__main__":
    asyncio.run(main())
