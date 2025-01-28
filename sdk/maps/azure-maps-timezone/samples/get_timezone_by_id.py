# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_timezone_by_id.py
DESCRIPTION:
    This API returns current, historical, and future time zone information for the specified IANA time zone ID.
USAGE:
    python get_timezone_by_id.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")


def get_timezone_by_id():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimeZoneClient

    timezone_client = MapsTimeZoneClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = timezone_client.get_timezone(timezone_id="sr-Latn-RS")
        print(result)
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == "__main__":
    get_timezone_by_id()
