# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_iana_timezone_ids.py
DESCRIPTION:
    This sample demonstrates how to get timezone by IANA ID
USAGE:
    python get_iana_timezone_ids.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your Azure Maps subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_iana_timezone_ids():
    # [START get_iana_timezone_ids]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    timezone_ids = maps_timezone_client.get_iana_timezone_ids()

    print("There are {} IANA timezone IDs in total".format(len(timezone_ids)))
    for timezone in timezone_ids:
        print("IANA ID: {}".format(timezone.id))
    # [END get_iana_timezone_ids]

if __name__ == '__main__':
    get_iana_timezone_ids()