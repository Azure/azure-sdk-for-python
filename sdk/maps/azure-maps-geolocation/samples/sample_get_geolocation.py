# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_geolocation.py
DESCRIPTION:
    This sample demonstrates return the ISO country code for the provided IP address.
USAGE:
    python sample_get_geolocation.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_geolocation():
    # [START get_geolocation]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.geolocation import MapsGeolocationClient

    maps_geolocation_client = MapsGeolocationClient(credential=AzureKeyCredential(subscription_key))

    result = maps_geolocation_client.get_geolocation(ip_address="2001:4898:80e8:b::189")

    print("Get Geolocation:")
    print(result)

    # [END get_geolocation]


if __name__ == '__main__':
    get_geolocation()