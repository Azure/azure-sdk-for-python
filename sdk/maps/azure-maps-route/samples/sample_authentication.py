# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py
DESCRIPTION:
    This sample demonstrates how to authenticate with the Azure Maps Route
    service with an Subscription key. See more details about authentication here:
    https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys
USAGE:
    python sample_authentication.py
    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
    - TENANT_ID - your tenant ID that wants to access Azure Maps account
    - CLIENT_ID - your client ID that wants to access Azure Maps account
    - CLIENT_SECRET - your client secret that wants to access Azure Maps account
    - AZURE_MAPS_CLIENT_ID - your Azure Maps client ID
"""

import os

def authentication_maps_service_client_with_subscription_key_credential():
    # [START create_maps_route_service_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))
    # [END create_maps_route_service_client_with_key]

    result = maps_route_client.get_route_range(coordinates=(52.50931,13.42936), time_budget_in_sec=6000)

    print(result)


def authentication_maps_service_client_with_aad_credential():
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, AZURE_MAPS_CLIENT_ID
    """
    # [START create_maps_route_service_client_with_aad]
    from azure.identity import DefaultAzureCredential
    from azure.maps.route import MapsRouteClient

    credential = DefaultAzureCredential()
    maps_client_id = os.getenv("AZURE_MAPS_CLIENT_ID")

    maps_route_client = MapsRouteClient(client_id=maps_client_id, credential=credential)
    # [END create_maps_route_service_client_with_aad]

    result = maps_route_client.get_route_range(coordinates=(52.50931,13.42936), time_budget_in_sec=6000)

    print(result)


if __name__ == '__main__':
    authentication_maps_service_client_with_subscription_key_credential()
    authentication_maps_service_client_with_aad_credential()