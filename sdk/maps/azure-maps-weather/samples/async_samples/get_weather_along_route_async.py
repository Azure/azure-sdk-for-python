# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_weather_along_route_async.py
DESCRIPTION:
    This API returns a locationally precise, up-to-the-minute forecast that includes weather hazard assessments and notifications along a route.
USAGE:
    python get_weather_along_route_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

async def get_weather_along_route():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather.aio import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        async with maps_weather_client:
            result = await maps_weather_client.get_weather_along_route(
                query='25.033075,121.525694,0:25.0338053,121.5640089,2'
            )
            print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    asyncio.run(get_weather_along_route())

