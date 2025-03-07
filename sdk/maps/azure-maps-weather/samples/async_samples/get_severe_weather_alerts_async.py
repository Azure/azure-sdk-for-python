# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_severe_weather_alerts_async.py
DESCRIPTION:
    This API returns information about severe weather conditions such as hurricanes, thunderstorms, flooding, lightning, heat waves or forest fires for a given location.
USAGE:
    python get_severe_weather_alerts_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os
import json

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


async def get_severe_weather_alerts():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather.aio import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        async with maps_weather_client:
            result = await maps_weather_client.get_severe_weather_alerts(coordinates=[39.793451, -104.944511])
            print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    asyncio.run(get_severe_weather_alerts())
