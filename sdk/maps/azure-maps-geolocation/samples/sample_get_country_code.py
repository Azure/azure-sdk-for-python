# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_country_code.py
DESCRIPTION:
    This sample demonstrates return the ISO country code for the provided IP address.
USAGE:
    python sample_get_country_code.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""

import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_country_code():
    # [START get_country_code]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.geolocation import MapsGeolocationClient

    maps_geolocation_client = MapsGeolocationClient(credential=AzureKeyCredential(subscription_key))

    result = maps_geolocation_client.get_country_code(ip_address="2001:4898:80e8:b::189")

    print("Get Country code with Geolocation:")
    print(result.iso_code)

    # [END get_country_code]


if __name__ == "__main__":
    get_country_code()
