# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_geometries.py
DESCRIPTION:
    This sample demonstrates how to perform fuzzy search by location and lat/lon.
USAGE:
    python sample_get_geometries.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_geometries():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.get_geometries(geometry_ids=["8bceafe8-3d98-4445-b29b-fd81d3e9adf5"])

    print(result[0].geometry_data)

if __name__ == '__main__':
    get_geometries()