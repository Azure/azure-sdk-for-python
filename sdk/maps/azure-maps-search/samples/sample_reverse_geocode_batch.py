# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_geocode_batch.py
DESCRIPTION:
    This sample demonstrates how to perform reverse batch search by given coordinates.
USAGE:
    python sample_reverse_geocode_batch.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.maps.search.models import ReverseGeocodingBatchRequestItem, ReverseGeocodingBatchRequestBody, LatLon

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def reverse_geocode_batch():
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    coordinates1 = ReverseGeocodingBatchRequestItem(coordinates=LatLon(47.620498, -122.349309))
    coordinates2 = ReverseGeocodingBatchRequestItem(coordinates=LatLon(47.630356, -122.138679))
    reverse_geocode_batch_request = ReverseGeocodingBatchRequestBody(batch_items=[coordinates1, coordinates2])

    result = maps_search_client.get_reverse_geocoding_batch(reverse_geocode_batch_request)

    if result.batch_items:
        features = result.batch_items[0].features
        if features:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 1 is None")
        else:
            print("No features available for item 1")

        features = result.batch_items[1].features
        if features:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 2 is None")
        else:
            print("No features available for item 2")
    else:
        print("No batch items found")

if __name__ == '__main__':
   reverse_geocode_batch()
