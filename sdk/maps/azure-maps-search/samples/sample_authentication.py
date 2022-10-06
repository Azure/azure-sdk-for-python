# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Maps Search
    service with an Subscription key. See more details about authentication here:
    https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys
USAGE:
    python sample_authentication.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

def authentication_maps_service_client_with_subscription_key_credential():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    result = maps_search_client.get_point_of_interest_categories()

    print(result)

if __name__ == '__main__':
    authentication_maps_service_client_with_subscription_key_credential()