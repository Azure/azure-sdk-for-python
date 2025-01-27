# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_windows_timezone_ids_async.py
DESCRIPTION:
    This API returns a full list of Windows time zone IDs.
USAGE:
    python get_windows_timezone_ids_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_windows_timezone_ids_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        async with timezone_client:
            result = await timezone_client.get_windows_timezone_ids()
            print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    asyncio.run(get_windows_timezone_ids_async())
