# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
import uuid
from datetime import datetime, timezone

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

# Set the following environment variables for this particular sample:
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE_GROUP,
# DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION
try:
    endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
    update_provider = os.environ["DEVICEUPDATE_UPDATE_PROVIDER"]
    update_name = os.environ["DEVICEUPDATE_UPDATE_NAME"]
    update_version = os.environ["DEVICEUPDATE_UPDATE_VERSION"]
    group = os.environ["DEVICEUPDATE_DEVICE_GROUP"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, ")
    print("DEVICEUPDATE_DEVICE_GROUP, DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    deployment_id = uuid.uuid4().hex
    deployment = {
        "deploymentId": deployment_id,
        "startDateTime": str(datetime.now(timezone.utc)),
        "update": {
            "updateId": {
                "provider": update_provider,
                "name": update_name,
                "version": update_version
            }
        },
        "groupId": group
    }

    response = client.device_management.create_or_update_deployment(group, deployment_id, deployment)
    response = client.device_management.get_deployment_status(group, deployment_id)
    print(response)
except HttpResponseError as e:
    print('Failed to deploy update: {}'.format(e.response.json()))
