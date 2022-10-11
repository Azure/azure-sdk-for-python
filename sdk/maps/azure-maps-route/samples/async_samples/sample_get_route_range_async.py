# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_range_async.py
DESCRIPTION:
    This sample demonstrates how to perform get route range with list of lat/lon.
USAGE:
    python sample_get_route_range_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


async def get_route_range():
    # [START get_route_range_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route.aio import MapsRouteClient
    from azure.maps.route.models import LatLon

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    async with maps_route_client:
        result = await maps_route_client.get_route_range(
            coordinates=LatLon(52.50931,13.42936),
            time_budget_in_sec=6000
        )

    print("Get Route Range with coordinates and time budget:")
    print(result.reachable_range.center)
    print(result.reachable_range.boundary[0])
    # [END get_route_range_async]

if __name__ == '__main__':
    asyncio.run(get_route_range())