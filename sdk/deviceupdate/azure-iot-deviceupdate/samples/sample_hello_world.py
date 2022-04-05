# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import os

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID
try:
    endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
except KeyError:
    LOG.error("Missing environment variable 'DEVICEUPDATE_ENDPOINT' or 'DEVICEUPDATE_INSTANCE_ID' - please set if before running the example")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    # Raise an exception if the service rejected the call
    response = client.device_management.list_device_classes()
    result = [item for item in response]
    print(result)
except HttpResponseError as e:
    print('Failed to get device message: {}'.format(e.response.json()))
