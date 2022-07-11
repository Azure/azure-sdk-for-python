# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_nearby_point_of_interest.py
DESCRIPTION:
    This sample demonstrates how to perform search nearby POI by given coordinates.
USAGE:
    python sample_search_nearby_point_of_interest.py

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

def search_nearby_point_of_interest():
    # [START search_nearby_point_of_interest]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient
    from azure.maps.search.models import LatLon

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.search_nearby_point_of_interest(coordinates=LatLon(25.0338053, 121.5640089))

    print("Get Search Nearby point of interest:")
    print(result)
    print("------------------------------")
    print("Get Search Nearby point of interest result in Json format:")
    print(to_json(result))
    # [END search_nearby_point_of_interest]

if __name__ == '__main__':
    search_nearby_point_of_interest()