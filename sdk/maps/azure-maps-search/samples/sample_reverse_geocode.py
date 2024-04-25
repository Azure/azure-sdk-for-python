# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_geocode.py
DESCRIPTION:
    This sample demonstrates how to perform reverse search by given coordinates.
USAGE:
    python sample_reverse_geocode.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def reverse_geocode():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
    address = result.features[0].properties.address
    print(address.formatted_address)

if __name__ == '__main__':
   reverse_geocode()