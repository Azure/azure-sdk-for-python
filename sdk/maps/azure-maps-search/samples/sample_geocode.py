# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_geocode.py
DESCRIPTION:
    This sample demonstrates how to perform search address
USAGE:
    python sample_geocode.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = "xxxxxxxx-xxxx-xxxx"

def geocode():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")
    coordinates = result.features[0].geometry.coordinates
    longitude = coordinates[0]
    latitude = coordinates[1]

    print(longitude, latitude)

if __name__ == '__main__':
    geocode()