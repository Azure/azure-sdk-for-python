# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_geocode_async.py
DESCRIPTION:
    This sample demonstrates how to perform search by location.
USAGE:
    python sample_geocode_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def geocode_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        result = await maps_search_client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")

    if (result.features and len(result.features) > 0):
        coordinates = result.features[0].geometry.coordinates
        longitude = coordinates[0]
        latitude = coordinates[1]

        print(longitude, latitude)
    else:
        print("No results")

if __name__ == '__main__':
    asyncio.run(geocode_async())
