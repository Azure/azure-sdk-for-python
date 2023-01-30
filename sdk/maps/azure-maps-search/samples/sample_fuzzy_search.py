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

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def fuzzy_search():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient
    from azure.maps.search.models import BoundingBox

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.fuzzy_search(query="starbucks", bounding_box=BoundingBox(-122.4594, 25.105497, 121.597366, 121.597366))

    print("Get Search Fuzzy with coordinates with search query: " + result.query)
    print("Fuzzy level: {}".format(result.fuzzy_level))
    print("Total results: {}".format(result.num_results))
    print("Address from the first item in results: ")
    print(result.results[0].address)

if __name__ == '__main__':
    fuzzy_search()