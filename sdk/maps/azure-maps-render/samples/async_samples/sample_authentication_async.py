# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py
DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Maps Render
    service with an Subscription key. See more details about authentication here:
    https://learn.microsoft.com/azure/azure-maps/how-to-manage-account-keys
USAGE:
    python sample_authentication_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
    - TENANT_ID - your tenant ID that wants to access Azure Maps account
    - CLIENT_ID - your client ID that wants to access Azure Maps account
    - CLIENT_SECRET - your client secret that wants to access Azure Maps account
    - AZURE_MAPS_CLIENT_ID - your Azure Maps client ID
"""

import asyncio
import os
import sys


async def authentication_maps_service_client_with_subscription_key_credential_async():
    # [START create_maps_render_service_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))
    # [END create_maps_render_service_client_with_key_async]

    async with maps_render_client:
        result = await maps_render_client.get_copyright_caption()

    print(result)


async def authentication_maps_service_client_with_aad_credential_async():
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, AZURE_MAPS_CLIENT_ID
    """
    # [START create_maps_render_service_client_with_aad_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.maps.render.aio import MapsRenderClient

    credential = DefaultAzureCredential()
    maps_client_id = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

    maps_render_client = MapsRenderClient(client_id=maps_client_id, credential=credential)
    # [END create_maps_render_service_client_with_aad_async]

    async with maps_render_client:
        result = await maps_render_client.get_copyright_caption()

    print(result)


async def main():
    await authentication_maps_service_client_with_subscription_key_credential_async()
    await authentication_maps_service_client_with_aad_credential_async()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
