# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_windows_timezone_ids.py
DESCRIPTION:
    This sample demonstrates how to get timezone by IANA ID
USAGE:
    python get_windows_timezone_ids.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import asyncio
import os
import sys

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_windows_timezone_ids():
    # [START get_windows_timezone_ids_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    async with maps_timezone_client:
        timezone_ids = await maps_timezone_client.get_windows_timezone_ids()

    print("There are {} timezone IDs in total".format(len(timezone_ids)))
    for timezone in timezone_ids:
        if timezone.territory == "001":
            continue
        print("Windows ID: {:30} => IANA ID: {:25}, territory: {}".format(
            timezone.windows_id, timezone.iana_ids[0], timezone.territory))
    # [END get_windows_timezone_ids_async]

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_windows_timezone_ids())