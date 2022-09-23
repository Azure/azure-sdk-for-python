# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_iana_version.py
DESCRIPTION:
    This sample demonstrates how to get timezone by IANA ID
USAGE:
    python get_iana_version.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import asyncio
import os
import sys

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

async def get_iana_version():
    # [START get_iana_version_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    async with maps_timezone_client:
        version = await maps_timezone_client.get_iana_version()

    print("Current IANA version is: {}".format(version.version))
    # [END get_iana_version_async]

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_iana_version())