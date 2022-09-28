# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_fuzzy_search_async.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_fuzzy_search_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def fuzzy_search_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        result = await maps_search_client.fuzzy_search("seattle", coordinates=(47.60323, -122.33028))

    print("Get Search Fuzzy with coordinates with search query: " + result.query)
    print("Fuzzy level: {}".format(result.fuzzy_level))
    print("Total results: {}".format(result.num_results))
    print("Address from the first item in results: ")
    print(result.results[0].address)

if __name__ == '__main__':
    asyncio.run(fuzzy_search_async())
