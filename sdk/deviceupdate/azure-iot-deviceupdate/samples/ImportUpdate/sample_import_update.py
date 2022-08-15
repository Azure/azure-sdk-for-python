# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import base64
import hashlib
import json

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

# Set the following environment variables for this particular sample:
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID,
# DEVICEUPDATE_PAYLOAD_FILE, DEVICEUPDATE_PAYLOAD_URL, DEVICEUPDATE_MANIFEST_FILE, DEVICEUPDATE_MANIFEST_URL
try:
    endpoint = os.environ["DEVICEUPDATE_ENDPOINT"]
    instance = os.environ["DEVICEUPDATE_INSTANCE_ID"]
    payload_file = os.environ["DEVICEUPDATE_PAYLOAD_FILE"]
    payload_url = os.environ["DEVICEUPDATE_PAYLOAD_URL"]
    manifest_file = os.environ["DEVICEUPDATE_MANIFEST_FILE"]
    manifest_url = os.environ["DEVICEUPDATE_MANIFEST_URL"]
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, "
          "DEVICEUPDATE_PAYLOAD_FILE, DEVICEUPDATE_PAYLOAD_URL, DEVICEUPDATE_MANIFEST_FILE, DEVICEUPDATE_MANIFEST_URL")
    exit()


def get_file_size(file_path):
    return os.path.getsize(file_path)


def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        return base64.b64encode(hashlib.sha256(bytes).digest()).decode("utf-8")


# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    content = [{
        "importManifest": {
            "url": manifest_url,
            "sizeInBytes": get_file_size(manifest_file),
            "hashes": {
                "sha256": get_file_hash(manifest_file)
            }
        },
        "files": [{
            "fileName": os.path.basename(payload_file),
            "url": payload_url
        }]
    }]

    response = client.device_update.begin_import_update(content)
    response.wait

except HttpResponseError as e:
    print('Failed to import update: {}'.format(e.response.json()))


