# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_country_code_async.py
DESCRIPTION:
    This sample demonstrates return the ISO country code for the provided IP address.
USAGE:
    python sample_get_country_code_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_country_code_async():
    # [START get_country_code_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.geolocation.aio import MapsGeolocationClient

    maps_geolocation_client = MapsGeolocationClient(credential=AzureKeyCredential(subscription_key))

    async with maps_geolocation_client:
        result = await maps_geolocation_client.get_country_code(ip_address="2001:4898:80e8:b::189")

    print("Get Country code with Geolocation:")
    print(result.iso_code)
    # [END get_country_code_async]


if __name__ == "__main__":
    asyncio.run(get_country_code_async())
