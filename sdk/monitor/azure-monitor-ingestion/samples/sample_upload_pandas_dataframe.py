# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_upload_pandas_dataframe.py

DESCRIPTION:
    This sample demonstrates how to upload data stored in a pandas dataframe to Azure Monitor. For example,
    a user might have the result of a query stored in a pandas dataframe and want to upload it to a Log Analytics
    workspace.

    Note: This sample requires the azure-identity and pandas libraries.

USAGE:
    python sample_upload_pandas_dataframe.py

    Set the environment variables with your own values before running the sample:
    1) DATA_COLLECTION_ENDPOINT - your data collection endpoint
    2) LOGS_DCR_RULE_ID - your data collection rule immutable ID
    3) LOGS_DCR_STREAM_NAME - your data collection rule stream name

    If using an application service principal for authentication, set the following:
    1) AZURE_TENANT_ID - your Azure AD tenant (directory) ID
    2) AZURE_CLIENT_ID - your Azure AD client (application) ID
    3) AZURE_CLIENT_SECRET - your Azure AD client secret
"""

from datetime import datetime
import json
import os

import pandas as pd

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

endpoint = os.environ["DATA_COLLECTION_ENDPOINT"]
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

# Set up example DataFrame.
data = [
    {"Time": datetime.now().astimezone(), "Computer": "Computer1", "AdditionalContext": "context-2"},
    {"Time": datetime.now().astimezone(), "Computer": "Computer2", "AdditionalContext": "context"},
]
df = pd.DataFrame.from_dict(data)

# If you have a populated dataframe that you want to upload, one approach is to use the DataFrame `to_json` method
# which will convert any datetime objects to ISO 8601 strings. The `json.loads` method will then convert the JSON string
# into a Python object that can be used for upload.
body = json.loads(df.to_json(orient="records", date_format="iso"))
try:
    client.upload(rule_id=os.environ["LOGS_DCR_RULE_ID"], stream_name=os.environ["LOGS_DCR_STREAM_NAME"], logs=body)
except HttpResponseError as e:
    print(f"Upload failed: {e}")
