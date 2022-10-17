# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_matrix_async.py
DESCRIPTION:
    This sample demonstrates how to perform get route matrix result with given request object.
USAGE:
    python sample_get_route_matrix_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


async def get_route_matrix_async():
    # [START get_route_matrix_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route.aio import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    request_obj = {
        "origins": {
            "type": "MultiPoint",
            "coordinates": [
                [
                    4.85106,
                    52.36006
                ],
                [
                    4.85056,
                    52.36187
                ]
            ]
        },
        "destinations": {
            "type": "MultiPoint",
            "coordinates": [
                [
                    4.85003,
                    52.36241
                ],
                [
                    13.42937,
                    52.50931
                ]
            ]
        }
    }

    async with maps_route_client:
        result = await maps_route_client.get_route_matrix(query=request_obj)

    print("Get Route Matrix with given request object:")
    print(result.matrix[0][0].response.summary.length_in_meters)
    print(result.summary)
    # [END get_route_matrix_async]

if __name__ == '__main__':
    asyncio.run(get_route_matrix_async())