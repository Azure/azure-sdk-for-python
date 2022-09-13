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
    print(f"Get update data for provider '{update_provider}', name '{update_name}' and version '{update_version}'...")
    response = client.device_update.get_update(update_provider, update_name, update_version)

    print("Update:")
    print(f"  Provider: {response['updateId']['provider']}")
    print(f"  Name: {response['updateId']['name']}")
    print(f"  Version: {response['updateId']['version']}")
    print("Metadata:")
    print(response)

    print(f"\nEnumerate update files:")
    response = client.device_update.list_files(update_provider, update_name, update_version)
    file_ids = []
    for item in response:
        file_ids.append(item)
        print(item)

    for file_id in file_ids:
        response = client.device_update.get_file(update_provider, update_name, update_version, file_id)
        print("\nFile:")
        print(f"  FileId: {response['fileId']}")
        print("Metadata:")
        print(response)

except HttpResponseError as e:
    print('Failed to get update: {}'.format(e))
