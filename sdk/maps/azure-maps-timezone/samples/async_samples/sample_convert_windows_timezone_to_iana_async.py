# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_convert_windows_timezone_to_iana.py
DESCRIPTION:
    This sample demonstrates how to get timezone by IANA ID
USAGE:
    python convert_windows_timezone_to_iana.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def convert_windows_timezone_to_iana_async():
    # [START convert_windows_timezone_to_iana_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    windows_timezone_id = "pacific standard time"
    async with maps_timezone_client:
        iana_ids = await maps_timezone_client.convert_windows_timezone_to_iana(
            windows_timezone_id=windows_timezone_id)

    print("Windows timezone {} contains the following IANA timezones:".format(
        windows_timezone_id))
    for iana in iana_ids:
        print(iana.id)
    # [END convert_windows_timezone_to_iana_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(convert_windows_timezone_to_iana_async())
