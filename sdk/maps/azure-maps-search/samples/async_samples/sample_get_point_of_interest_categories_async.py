# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_point_of_interest_categories_async.py
DESCRIPTION:
    This sample demonstrates get POI categories.
USAGE:
    python sample_get_point_of_interest_categories_async.py

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

async def get_point_of_interest_categories_async():
    # [START get_point_of_interest_categories_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        result = await maps_search_client.get_point_of_interest_categories()

    print("Get Search POI Categories:")
    print(result)
    print("------------------------------")
    print("Get Search POI Categories result in Json format:")
    print(to_json(result))
    # [END get_point_of_interest_categories_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_point_of_interest_categories_async())
