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

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def reverse_geocode_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import AzureMapsSearchClient

    maps_search_client = AzureMapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        try:
            result = await maps_search_client.get_reverse_geocoding_batch({
                "batchItems": [
                    {"coordinates": [-122.349309, 47.620498]},
                    {"coordinates": [-122.138679, 47.630356]},
                ],
            }, )

            if 'batchItems' in result and result['batchItems']:
                # item 1
                features = result['batchItems'][0]['features']
                if features:
                    props = features[0].get('properties', {})
                    if props and 'address' in props and props['address']:
                        print(props['address'].get('formattedAddress', 'No formatted address for item 1 found'))
                    else:
                        print("Address 1 is None")
                else:
                    print("No features available for item 1")

                # item 2
                features = result['batchItems'][1]['features']
                if features:
                    props = features[0].get('properties', {})
                    if props and 'address' in props and props['address']:
                        print(props['address'].get('formattedAddress', 'No formatted address for item 2 found'))
                    else:
                        print("Address 2 is None")
                else:
                    print("No features available for item 2")
            else:
                print("No batch items found")
        except HttpResponseError as exception:
            if exception.error is not None:
                print(f"Error Code: {exception.error.code}")
                print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    asyncio.run(reverse_geocode_async())