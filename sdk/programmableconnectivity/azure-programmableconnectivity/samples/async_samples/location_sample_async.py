# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.programmableconnectivity.aio import ProgrammableConnectivityClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.programmableconnectivity.models import (
    NetworkIdentifier,
    DeviceLocationVerificationContent,
    LocationDevice,
)
import asyncio

async def main():
    client = ProgrammableConnectivityClient(endpoint="<endpoint>", credential=DefaultAzureCredential())
    APC_GATEWAY_ID = "/subscriptions/<subscription_id>/resourceGroups/.../.../..."

    try:
        network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Telefonica_Brazil")
        location_device = LocationDevice(phone_number="+5547865461235")
        content = DeviceLocationVerificationContent(
            longitude=12.12, latitude=45.11, accuracy=10, device=location_device, network_identifier=network_identifier
        )
        async with client:
            location_response = client.device_location.verify(body=content, apc_gateway_id=APC_GATEWAY_ID)
    except HttpResponseError as e:
        print("service responds error: {}".format(e.response.json()))

if __name__ == "__main__":
    asyncio.run(main())
