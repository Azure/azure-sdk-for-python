# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_polygon_async.py
DESCRIPTION:
    This sample demonstrates how to search polygons.
USAGE:
    python sample_get_polygon_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

from azure.core.exceptions import HttpResponseError
from azure.maps.search import Resolution
from azure.maps.search import BoundaryResultType

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_polygon_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        try:
            result = await maps_search_client.get_polygon(
                coordinates=[-122.204141, 47.61256],
                result_type=BoundaryResultType.LOCALITY,
                resolution=Resolution.SMALL,
            )

            if not result.get("geometry", False):
                print("No geometry found")
                return

            print(result["geometry"])
        except HttpResponseError as exception:
            if exception.error is not None:
                print(f"Error Code: {exception.error.code}")
                print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    asyncio.run(get_polygon_async())
