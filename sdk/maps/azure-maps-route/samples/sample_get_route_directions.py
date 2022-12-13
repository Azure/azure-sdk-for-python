# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_directions.py
DESCRIPTION:
    This sample demonstrates how to perform get route directions with list of lat/lon.
USAGE:
    python sample_get_route_directions.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


def get_route_directions():
    # [START get_route_directions]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    result = maps_route_client.get_route_directions(
        route_points=[(52.50931,13.42936), (52.50274,13.43872)],
        avoid_vignette=["AUS", "CHE"]
    )

    print("Get Route Directions with list of coordinates:")
    print(result.routes[0].summary)
    print(result.routes[0].sections[0])
    # [END get_route_directions]

if __name__ == '__main__':
    get_route_directions()