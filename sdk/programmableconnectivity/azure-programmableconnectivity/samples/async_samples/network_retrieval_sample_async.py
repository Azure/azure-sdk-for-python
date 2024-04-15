# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.programmableconnectivity.aio import ProgrammableConnectivityClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.programmableconnectivity.models import NetworkIdentifier
import asyncio

def create_client():
    return ProgrammableConnectivityClient(endpoint="<endpoint>", credential=DefaultAzureCredential())

async def main():
    client = ProgrammableConnectivityClient(endpoint="<endpoint>", credential=DefaultAzureCredential())
    APC_GATEWAY_ID = "/subscriptions/<subscription_id>/resourceGroups/.../.../..."

    try:
        network_content = NetworkIdentifier(identifier_type="IPv4", identifier="189.20.1.1")
        async with create_client() as client:
            network_response = await client.device_network.retrieve(body=network_content, apc_gateway_id=APC_GATEWAY_ID)
            print(network_response.network_code)
    except HttpResponseError as e:
        print("service responds error: {}".format(e.response.json()))

if __name__ == "__main__":
    asyncio.run(main())
