# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_structured_address.py
DESCRIPTION:
    This sample demonstrates how to perform search structured address.
USAGE:
    python sample_search_structured_address.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

# cSpell:disable
def search_structured_address():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient
    from azure.maps.search.models import StructuredAddress

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    addr = StructuredAddress(
        street_number="221",
        street_name="Sec. 2, Zhishan Rd.",
        municipality_subdivision="Shilin Dist.",
        municipality="Taipei City",
        country_code="TW")
    result = maps_search_client.search_structured_address(addr)

    print("Get Search Address Structured:")
    print(result)

if __name__ == '__main__':
    search_structured_address()
