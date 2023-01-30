# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_fuzzy_search_batch_async_with_batch_id.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_fuzzy_search_batch_async_with_batch_id.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


async def fuzzy_search_batch_with_search_queries():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        result = await maps_search_client.begin_fuzzy_search_batch(
            search_queries=[
                "350 5th Ave, New York, NY 10118&limit=1",
                "400 Broad St, Seattle, WA 98109&limit=6"
            ],
            polling=True,
        )

    print(result)
    print(result.batch_id)
    return result

async def fuzzy_search_batch_with_batch_id(batch_id=None):
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        result = await maps_search_client.begin_fuzzy_search_batch(
            batch_id=batch_id,
        )

    print(result.__dict__)
    print(result._polling_method._initial_response)

async def main():
    result = await fuzzy_search_batch_with_search_queries()
    await fuzzy_search_batch_with_batch_id(result.batch_id)

if __name__ == '__main__':
    asyncio.run(main())
