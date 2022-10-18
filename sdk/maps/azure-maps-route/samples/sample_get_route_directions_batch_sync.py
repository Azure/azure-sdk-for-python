# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_directions_batch_sync.py
DESCRIPTION:
    This sample demonstrates how to perform get route directions batch job synchronously with given query strings.
USAGE:
    python sample_get_route_directions_batch_sync.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_route_directions_batch_sync():
    # [START get_route_directions_batch_sync]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    result = maps_route_client.get_route_directions_batch_sync(
        queries=[
            "47.620659,-122.348934:47.610101,-122.342015&travelMode=bicycle&routeType=eco&traffic=false"
        ]
    )

    print("Get route directions batch sync")
    print(result.summary.total_requests)
    print(result.items[0].response.routes[0].sections[0])
    # [END get_route_directions_batch_sync]

if __name__ == '__main__':
    get_route_directions_batch_sync()