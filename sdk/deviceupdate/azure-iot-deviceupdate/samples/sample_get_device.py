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
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE
try:
    endpoint = os.environ["DEVICEUPDATE_ACCOUNT_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
    device = os.environ["DEVICEUPDATE_DEVICE"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ACCOUNT_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    response = client.device_management.get_device(device)
    print(response)
except HttpResponseError as e:
    print('Failed to get device message: {}'.format(e.response.json()))
