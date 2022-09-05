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
import json

def to_json(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=4
    )

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


def get_route_directions():
    # [START get_route_directions]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient
    from azure.maps.route.models import LatLon

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    result = maps_route_client.get_route_directions(route_points=[LatLon(52.50931,13.42936), LatLon(52.50274,13.43872)])

    print("Get Route Directions with list of coordinates:")
    print(result)
    print("------------------------------")
    print("Get Route Directions with list of coordinates result in Json format:")
    print(to_json(result))
    # [END get_route_directions]

if __name__ == '__main__':
    get_route_directions()