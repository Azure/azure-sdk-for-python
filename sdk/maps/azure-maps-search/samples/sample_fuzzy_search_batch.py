# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_fuzzy_search_batch.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_fuzzy_search_batch.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def fuzzy_search_batch():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.fuzzy_search_batch(
        search_queries=[
            "350 5th Ave, New York, NY 10118&limit=1",
            "400 Broad St, Seattle, WA 98109&limit=3"
        ]
    )

    print(result.summary)
    for item in result.items:
        print(item.response.results[0].address)

if __name__ == '__main__':
    fuzzy_search_batch()