# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_along_route.py
DESCRIPTION:
    This sample demonstrates how to perform search along route
USAGE:
    python sample_search_along_route.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def search_along_route():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    route_obj = {
        "route": {
            "type": "LineString",
            "coordinates": [
                [-122.143035,47.653536],
                [-122.187164,47.617556],
                [-122.114981,47.570599],
                [-122.132756,47.654009]
            ]
        }
    }
    result = maps_search_client.search_along_route(
        query="burger",
        route=route_obj,
        max_detour_time=1000
    )

    print(result.results[0].address.__dict__)

if __name__ == '__main__':
    search_along_route()