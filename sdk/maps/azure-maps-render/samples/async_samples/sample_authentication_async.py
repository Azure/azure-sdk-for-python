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
    https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys
USAGE:
    python sample_authentication_async.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import asyncio
import os

async def authentication_maps_service_client_with_subscription_key_credential_async():
    # [START create_maps_render_service_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.render.aio import MapsRenderClient

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

    maps_render_client = MapsRenderClient(credential=AzureKeyCredential(subscription_key))
    # [END create_maps_render_service_client_with_key_async]

    async with maps_render_client:
        result = await maps_render_client.get_copyright_caption()

    print(result)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(authentication_maps_service_client_with_subscription_key_credential_async())