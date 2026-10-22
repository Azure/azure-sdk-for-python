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

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def geocode():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")
        if result.get("features", False):
            coordinates = result["features"][0]["geometry"]["coordinates"]
            longitude = coordinates[0]
            latitude = coordinates[1]

            print(longitude, latitude)
        else:
            print("No results")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    geocode()
