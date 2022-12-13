# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_point_of_interest_categories.py
DESCRIPTION:
    This sample demonstrates get POI categories.
USAGE:
    python sample_get_point_of_interest_categories.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_point_of_interest_categories():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.get_point_of_interest_categories()

    print("Get Search POI Categories:")
    print(result[0])


if __name__ == '__main__':
    get_point_of_interest_categories()