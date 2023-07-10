# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_upload_file_contents.py

DESCRIPTION:
    This sample demonstrates how to upload the contents of a file to a Log Analytics workspace. The file is
    expected to contain a list of JSON objects.

    Note: This sample requires the azure-identity library.

USAGE:
    python sample_upload_file_contents.py

    Set the environment variables with your own values before running the sample:
    1) DATA_COLLECTION_ENDPOINT - your data collection endpoint
    2) LOGS_DCR_RULE_ID - your data collection rule immutable ID
    3) LOGS_DCR_STREAM_NAME - your data collection rule stream name

    If using an application service principal for authentication, set the following:
    1) AZURE_TENANT_ID - your Azure AD tenant (directory) ID
    2) AZURE_CLIENT_ID - your Azure AD client (application) ID
    3) AZURE_CLIENT_SECRET - your Azure AD client secret
"""

import json
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

endpoint = os.environ["DATA_COLLECTION_ENDPOINT"]
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

# Update this to point to a file containing a list of JSON objects.
FILE_PATH = "../test-logs.json"

# Option 1: Upload the file contents by passing in the file stream. With this option, no chunking is done, and the
# file contents are uploaded as is through one request. Subject to size service limits.
with open(FILE_PATH, "r") as f:
    try:
        client.upload(rule_id=os.environ["LOGS_DCR_RULE_ID"], stream_name=os.environ["LOGS_DCR_STREAM_NAME"], logs=f)
    except HttpResponseError as e:
        print(f"File stream upload failed: {e}")


# Option 2: Upload the file contents by passing in the list of JSON objects. Chunking is done automatically, and the
# file contents are uploaded through multiple requests.
with open(FILE_PATH, "r") as f:
    logs = json.load(f)
    try:
        client.upload(rule_id=os.environ["LOGS_DCR_RULE_ID"], stream_name=os.environ["LOGS_DCR_STREAM_NAME"], logs=logs)
    except HttpResponseError as e:
        print(f"List upload failed: {e}")
