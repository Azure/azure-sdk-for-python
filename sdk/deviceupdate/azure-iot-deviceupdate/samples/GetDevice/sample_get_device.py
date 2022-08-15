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
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE_GROUP
try:
    endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
    group = os.environ["DEVICEUPDATE_DEVICE_GROUP"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE_GROUP")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    print("Get various device management information from Device Update for IoT Hub...")

    print("\nDevices:")
    response = client.device_management.list_devices()
    for item in response:
        print(f"  {item['deviceId']}")

    print("\nDevice groups:")
    response = client.device_management.list_groups()
    for item in response:
        print(f"  {item['groupId']}")

    print("\nDevice classes:")
    response = client.device_management.list_device_classes()
    for item in response:
        print(f"  {item['deviceClassId']}")

    print(f"\nFor group '{group}', best updates are:")
    response = client.device_management.list_best_updates_for_group(group)
    for item in response:
        print(f" Device class '{item['deviceClassId']}':")
        print(f"  {item['update']['updateId']['provider']}")
        print(f"  {item['update']['updateId']['name']}")
        print(f"  {item['update']['updateId']['version']}")
except HttpResponseError as e:
    print('Failed to get device message: {}'.format(e.response.json()))
