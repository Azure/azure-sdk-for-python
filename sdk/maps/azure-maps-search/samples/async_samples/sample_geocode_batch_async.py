# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_geocode_batch_async.py
DESCRIPTION:
    This sample demonstrates how to perform batch search by location.
USAGE:
    python sample_geocode_batch_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

from azure.maps.search._generated.models import GeocodingBatchRequestItem, GeocodingBatchRequestBody

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def geocode_batch_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        request_item1 = GeocodingBatchRequestItem(query="15127 NE 24th Street, Redmond, WA 98052", top=5)
        request_item2 = GeocodingBatchRequestItem(query="15127 NE 24th Street, Redmond, WA 98052", top=5)

        batch_request_body = GeocodingBatchRequestBody(batch_items=[request_item1, request_item2])

        result = await maps_search_client.get_geocoding_batch(batch_request_body)

    result1 = result.batch_items[0]

    coordinates1 = result1.features[0].geometry.coordinates
    longitude1 = coordinates1[0]
    latitude1 = coordinates1[1]

    print(longitude1, latitude1)

    result2 = result.batch_items[1]

    coordinates2 = result2.features[0].geometry.coordinates
    longitude2 = coordinates2[0]
    latitude2 = coordinates2[1]

    print(longitude2, latitude2)

if __name__ == '__main__':
    asyncio.run(geocode_batch_async())
