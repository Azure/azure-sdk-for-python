# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

# Set the following environment variables for this particular sample:
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID,
# DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION
try:
    endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
    update_provider = os.environ["DEVICEUPDATE_UPDATE_PROVIDER"]
    update_name = os.environ["DEVICEUPDATE_UPDATE_NAME"]
    update_version = os.environ["DEVICEUPDATE_UPDATE_VERSION"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, "
          "DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    print("List providers, names and versions of updates in Device Update for IoT Hub...")

    print("\nProviders:")
    response = client.device_update.list_providers()
    for item in response:
        print(f"  {item}")

    print(f"\nNames in '{update_provider}'")
    response = client.device_update.list_names(update_provider)
    for item in response:
        print(f"  {item}")

    print(f"\nVersions in provider '{update_provider}' and name '{update_name}'")
    response = client.device_update.list_versions(update_provider, update_name)
    for item in response:
        print(f"  {item}")
except HttpResponseError as e:
    print('Failed to get data: {}'.format(e.response.json()))
