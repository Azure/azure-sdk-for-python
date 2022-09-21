# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_timezone_by_coordinates.py
DESCRIPTION:
    This sample demonstrates how to get timezone by coordinate
USAGE:
    python get_timezone_by_coordinates.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_timezone_by_coordinates():
    # [START get_timezone_by_coordinates]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    coordinates = (52.5069,13.2843,)
    timezone = maps_timezone_client.get_timezone_by_coordinates(coordinates=coordinates)

    print("Timzone for coordinate {} is : {}".format(
        coordinates, timezone.time_zones[0].names.generic))
    print("  Tag: {}".format(timezone.time_zones[0].names.standard))
    print("  Standard name: {}".format(timezone.time_zones[0].reference_time.tag))
    print("  Standard offset: {}".format(timezone.time_zones[0].reference_time.standard_offset))
    # [END get_timezone_by_coordinates]

if __name__ == '__main__':
    get_timezone_by_coordinates()