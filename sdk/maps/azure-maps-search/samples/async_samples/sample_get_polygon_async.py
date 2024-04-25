# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_polygon_async.py
DESCRIPTION:
    This sample demonstrates how to search polygons.
USAGE:
    python get_polygon_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def get_polygon_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        result = await maps_search_client.get_polygon(
            coordinates=[-122.204141, 47.61256],
            result_type="locality",
            resolution="small",
        )

    print(result.geometry)

if __name__ == '__main__':
    asyncio.run(get_polygon_async())
