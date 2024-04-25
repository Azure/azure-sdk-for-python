# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_geocode_batch_async.py
DESCRIPTION:
    This sample demonstrates how to perform reverse search by given coordinates in a batch.
USAGE:
    python sample_reverse_geocode_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

from azure.maps.search._generated.models import ReverseGeocodingBatchRequestItem, ReverseGeocodingBatchRequestBody

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def reverse_geocode_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        coordinates1 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
        coordinates2 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
        reverse_geocode_batch_request = ReverseGeocodingBatchRequestBody(batch_items=[coordinates1, coordinates2])

        result = await maps_search_client.get_reverse_geocoding_batch(reverse_geocode_batch_request)

    if result.batch_items and len(result.batch_items) > 0:
        features = result.batch_items[0].features
        if features and len(features) > 0:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 1 is None")
        else:
            print("No features available for item 1")

        features = result.batch_items[1].features
        if features and len(features) > 0:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 2 is None")
        else:
            print("No features available for item 2")
    else:
        print("No batch items found")

if __name__ == '__main__':
    asyncio.run(reverse_geocode_async())