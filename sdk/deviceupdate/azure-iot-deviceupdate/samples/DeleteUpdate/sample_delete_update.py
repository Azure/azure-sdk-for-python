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
    update_version = "2022.812.234.42"  # os.environ["DEVICEUPDATE_UPDATE_VERSION"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, "
          "DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    response = client.device_update.begin_delete_update(update_provider, update_name, update_version)
    response.wait

except HttpResponseError as e:
    print('Failed to delete update: {}'.format(e.response.json()))
