## ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.programmableconnectivity.aio import ProgrammableConnectivityClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.programmableconnectivity.models import (
    NetworkIdentifier,
    NumberVerificationWithCodeContent,
    NumberVerificationWithoutCodeContent,
)
import asyncio

# This flow involves 2 calls, with the user of the SDK needing to follow the redirect URI given in the `location` header value from the first call.
def create_client():
    return ProgrammableConnectivityClient(endpoint="<endpoint>", credential=DefaultAzureCredential())

async def main():
    APC_GATEWAY_ID = "/subscriptions/<subscription_id>/resourceGroups/.../.../..."

    location = None

    def callback(response):
        global location
        location = response.http_response.headers.get("location")

    network_identifier = NetworkIdentifier(identifier_type="NetworkCode", identifier="Telefonica_Brazil")

    content = NumberVerificationWithoutCodeContent(
        phone_number="<number>", redirect_uri="<redirect_uri>", network_identifier=network_identifier
    )
    async with create_client() as client:
        await client.number_verification.verify_without_code(body=content, apc_gateway_id=APC_GATEWAY_ID, raw_response_hook=callback)

    # The `location` variable must be followed by you, and is not used in the SDK.
    print(f"You have to follow the link: {location}")

    content = NumberVerificationWithCodeContent(apc_code="<code from step 1>")
    async with create_client() as client:
        verified_response = await client.number_verification.verify_with_code(body=content, apc_gateway_id=APC_GATEWAY_ID)

    print(f"verified_response: {verified_response}")

if __name__ == "__main__":
    asyncio.run(main())
