# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_search_cross_street_address.py
DESCRIPTION:
    This sample demonstrates how to perform reverse search cross street address.
USAGE:
    python sample_reverse_search_cross_street_address.py

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

def reverse_search_cross_street_address():
    # [START reverse_search_cross_street_address]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient
    from azure.maps.search.models import LatLon

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.reverse_search_cross_street_address(coordinates=LatLon(25.0338053, 121.5640089))
    print("Get Search Address Reverse Cross Street:")
    print(result)
    print("------------------------------")
    print("Get Search Address Reverse Cross Street result in Json format:")
    print(to_json(result))
    # [END reverse_search_cross_street_address]

if __name__ == '__main__':
    reverse_search_cross_street_address()