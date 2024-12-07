# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_daily_historical_normals.py
DESCRIPTION:
    This API returns climatology data such as past daily normal temperatures, precipitation and cooling/heating degree day information for a given location.
USAGE:
    python get_daily_historical_normals.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os
import json
import datetime

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_daily_historical_normals():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.weather import MapsWeatherClient

    maps_weather_client = MapsWeatherClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_weather_client.get_daily_historical_normals(
            coordinates=[40.760139, -73.961968],
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31),
        )
        print(json.dumps(result, indent=4))
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    get_daily_historical_normals()
