# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_geocode_batch.py
DESCRIPTION:
    This sample demonstrates how to perform batch search address
USAGE:
    python sample_geocode_batch.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def geocode_batch():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_geocoding_batch(
            {
                "batchItems": [
                    {"query": "400 Broad St, Seattle, WA 98109"},
                    {"query": "15127 NE 24th Street, Redmond, WA 98052"},
                ],
            },
        )

        if not result.get("batchItems", False):
            print("No batchItems in geocoding")
            return

        for item in result["batchItems"]:
            if not item.get("features", False):
                print(f"No features in item: {item}")
                continue

            coordinates = item["features"][0]["geometry"]["coordinates"]
            longitude, latitude = coordinates
            print(longitude, latitude)

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    geocode_batch()
