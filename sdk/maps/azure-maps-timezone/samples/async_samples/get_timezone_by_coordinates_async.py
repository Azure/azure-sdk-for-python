# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_timezone_by_coordinates_async.py
DESCRIPTION:
     This API returns current, historical, and future time zone information for a specified latitude-longitude pair.
USAGE:
    python get_timezone_by_coordinates_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_timezone_by_coordinates_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone.aio import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        async with timezone_client:
            result = await timezone_client.get_timezone_by_coordinates(coordinates=[25.0338053, 121.5640089])
            print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    asyncio.run(get_timezone_by_coordinates_async())
