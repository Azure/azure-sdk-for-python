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

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def geocode_batch_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import AzureMapsSearchClient

    maps_search_client = AzureMapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        async with maps_search_client:
            result = await maps_search_client.get_geocoding_batch({
                "batchItems": [
                    {"query": "400 Broad St, Seattle, WA 98109"},
                    {"query": "15127 NE 24th Street, Redmond, WA 98052"},
                ],
            }, )

            if 'batchItems' not in result or not result['batchItems']:
                print("No geocoding")
                return

            item1, item2 = result['batchItems']

            if not item1.get('features'):
                print("No geocoding1")
                return

            if not item2.get('features'):
                print("No geocoding2")
                return

            coordinates1 = item1['features'][0]['geometry']['coordinates']
            coordinates2 = item2['features'][0]['geometry']['coordinates']

            longitude1, latitude1 = coordinates1
            longitude2, latitude2 = coordinates2

            print(longitude1, latitude1)
            print(longitude2, latitude2)

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    asyncio.run(geocode_batch_async())
