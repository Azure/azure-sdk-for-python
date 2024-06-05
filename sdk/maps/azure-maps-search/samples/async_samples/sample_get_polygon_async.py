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
from azure.maps.search.models import ResolutionEnum
from azure.maps.search.models import BoundaryResultTypeEnum
from azure.maps.search.models import LatLon

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def get_polygon_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    async with maps_search_client:
        result = await maps_search_client.get_polygon(
            coordinates=LatLon(47.61256, -122.204141),
            result_type=BoundaryResultTypeEnum.LOCALITY,
            resolution=ResolutionEnum.SMALL
        )

    print(result.geometry)

if __name__ == '__main__':
    asyncio.run(get_polygon_async())
