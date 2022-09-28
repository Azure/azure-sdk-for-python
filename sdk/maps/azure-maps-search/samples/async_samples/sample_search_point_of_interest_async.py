# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_point_of_interest_async.py
DESCRIPTION:
    This sample demonstrates how to perform search POI by given target such as `juice bars`.
USAGE:
    python sample_search_point_of_interest_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def search_point_of_interest_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        result = await maps_search_client.search_point_of_interest("juice bars")

    print("Get Search POI:")
    print(result)

if __name__ == '__main__':
    asyncio.run(search_point_of_interest_async())
