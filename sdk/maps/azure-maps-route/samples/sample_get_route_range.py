# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_range.py
DESCRIPTION:
    This sample demonstrates how to perform get route range with given lat/lon.
USAGE:
    python sample_get_route_range.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_route_range():
    # [START get_route_range]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    result = maps_route_client.get_route_range(coordinates=(52.50931,13.42936), time_budget_in_sec=6000)

    print("Get Route Range with coordinates and time budget:")
    print(result.reachable_range.center)
    print(result.reachable_range.boundary[0])
    # [END get_route_range]

if __name__ == '__main__':
    get_route_range()