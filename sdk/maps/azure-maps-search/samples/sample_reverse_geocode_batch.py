# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_reverse_search_address.py
DESCRIPTION:
    This sample demonstrates how to perform reverse search by given coordinates.
USAGE:
    python sample_reverse_search_address.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

from azure.maps.search._generated.models import ReverseGeocodingBatchRequestItem, ReverseGeocodingBatchRequestBody

subscription_key = "xxxxxx-xxxx-xxxx"

def reverse_geocode_batch():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    coordinates1 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
    coordinates2 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
    reverse_geocode_batch_request = ReverseGeocodingBatchRequestBody(batch_items=[coordinates1, coordinates2])

    result = maps_search_client.get_reverse_geocoding_batch(reverse_geocode_batch_request)

    result1 = result.batch_items[0]
    address1 = result1.features[0].properties.address
    print(address1.formatted_address)

    result2 = result.batch_items[1]
    address2 = result2.features[0].properties.address
    print(address2.formatted_address)

if __name__ == '__main__':
   reverse_geocode_batch()