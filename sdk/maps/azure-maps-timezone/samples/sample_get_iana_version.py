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
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

def get_iana_version():
    # [START get_iana_version]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.timezone import MapsTimezoneClient

    maps_timezone_client = MapsTimezoneClient(credential=AzureKeyCredential(subscription_key))

    version = maps_timezone_client.get_iana_version()

    print("Current IANA version is: {}".format(version.version))
    # [END get_iana_version]

if __name__ == '__main__':
    get_iana_version()