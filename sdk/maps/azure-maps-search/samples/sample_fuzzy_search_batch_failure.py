# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_fuzzy_search_batch_failure.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_fuzzy_search_batch_failure.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

# cSpell:disable
def fuzzy_search_batch_failure():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.fuzzy_search_batch(
        search_queries=[
            "350 5th Ave, New York, NY 10118&limit=1",
            "400 Broad St, Seattle, WA 98109&limi"
        ]
    )

    print(result.summary)
    print(result.items[0].response.summary)
    print("--------------------------")
    for item in result.items:
        count = 0
        if item.response.error is not None:
            count = count+1
            print(f"Error: {item.response.error.message}")
    print(f"There are total of {count} search queries failed.")

if __name__ == '__main__':
    fuzzy_search_batch_failure()
