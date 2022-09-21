# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_iana_timezone_ids.py
DESCRIPTION:
    This sample demonstrates how to get timezone by IANA ID
USAGE:
    python get_iana_timezone_ids.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_iana_timezone_ids():
    # [START get_iana_timezone_ids_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    async with maps_timezone_client:
        timezone_ids = await maps_timezone_client.get_iana_timezone_ids()

    print("There are {} IANA timezone IDs in total".format(len(timezone_ids)))
    for timezone in timezone_ids:
        print("IANA ID: {}".format(timezone.id))
    # [END get_iana_timezone_ids_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_iana_timezone_ids())