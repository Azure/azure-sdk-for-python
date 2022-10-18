# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_begin_get_route_directions_batch_async.py
DESCRIPTION:
    This sample demonstrates how to sends batches of route direction queries.
USAGE:
    python begin_get_route_directions_batch_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def begin_get_route_directions_batch_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route.aio import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))
    async with maps_route_client:
        result = await maps_route_client.begin_get_route_directions_batch(
            queries=[
                "47.620659,-122.348934:47.610101,-122.342015&travelMode=bicycle&routeType=eco&traffic=false"
            ],
            polling=True,
        )

    print("Get route directions batch batch_id to fetch the result later")
    print(result.batch_id)

if __name__ == '__main__':
    asyncio.run(begin_get_route_directions_batch_async())