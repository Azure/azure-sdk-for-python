# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_fuzzy_search.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_fuzzy_search.py

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

def fuzzy_search():
    # [START fuzzy_search]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient
    from azure.maps.search.models import LatLon

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.fuzzy_search("seattle", coordinates=LatLon(47.60323, -122.33028))

    print("Get Search Fuzzy with coordinates:")
    print(result)
    print("------------------------------")
    print("Get Search Fuzzy with coordinates result in Json format:")
    print(to_json(result))
    # [END fuzzy_search]

if __name__ == '__main__':
    fuzzy_search()