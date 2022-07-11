# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_point_of_interest_category_async.py
DESCRIPTION:
    This sample demonstrates search POI by given target such as `RESTAURANT` and coordinates.
USAGE:
    python sample_search_point_of_interest_category_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import json
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def to_json(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=4
    )

async def search_point_of_interest_category_async():
    # [START search_point_of_interest_category_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient
    from azure.maps.search.models import LatLon

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        result = await maps_search_client.search_point_of_interest_category("RESTAURANT", coordinates=LatLon(25.0338053, 121.5640089))

    print("Get Search POI Category:")
    print(result)
    print("------------------------------")
    print("Get Search POI Category result in Json format:")
    print(to_json(result))
    # [END search_point_of_interest_category_async]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_point_of_interest_category_async())