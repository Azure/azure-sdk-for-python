# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py
DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Maps Search
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
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        result = await maps_search_client.get_point_of_interest_categories()

    print(result)

if __name__ == '__main__':
    asyncio.run(authentication_maps_service_client_with_subscription_key_credential_async())