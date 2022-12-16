# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_address.py
DESCRIPTION:
    This sample demonstrates how to perform search address
USAGE:
    python sample_search_address.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def search_address():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.search_address(query="15127 NE 24th Street, Redmond, WA 98052")

    print(result.results[0].address)

if __name__ == '__main__':
    search_address()