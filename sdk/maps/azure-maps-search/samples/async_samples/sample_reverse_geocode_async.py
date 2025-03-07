# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_geocode_async.py
DESCRIPTION:
    This sample demonstrates how to perform reverse search by given coordinates.
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
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    async with maps_search_client:
        try:
            result = await maps_search_client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
            if result.get("features", False):
                props = result["features"][0].get("properties", {})
                if props and props.get("address", False):
                    print(props["address"].get("formattedAddress", "No formatted address found"))
                else:
                    print("Address is None")
            else:
                print("No features available")
        except HttpResponseError as exception:
            if exception.error is not None:
                print(f"Error Code: {exception.error.code}")
                print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    asyncio.run(reverse_geocode_async())
