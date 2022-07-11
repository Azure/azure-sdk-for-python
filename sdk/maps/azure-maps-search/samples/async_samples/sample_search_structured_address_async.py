# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_structured_address_async.py
DESCRIPTION:
    This sample demonstrates how to perform search structured address.
USAGE:
    python sample_search_structured_address_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import json
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def to_json(self):
    return json.dumps(
        self,
        default=lambda o: o.__dict__,
        sort_keys=True,
        indent=4
    )

# cSpell:disable
async def search_structured_address_async():
    # [START search_structured_address_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search.aio import MapsSearchClient
    from azure.maps.search.models import StructuredAddress

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    addr = StructuredAddress(
        street_number="221",
        street_name="Sec. 2, Zhishan Rd.",
        municipality_subdivision="Shilin Dist.",
        municipality="Taipei City",

    async with maps_search_client:
        result = await maps_search_client.search_structured_address(addr)

    print("Get Search Address Structured:")
    print(result)
    print("------------------------------")
    print("Get Search Address Structured result in Json format:")
    print(to_json(result))
    # [END search_structured_address_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_structured_address_async())
