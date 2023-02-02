# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_send_small_logs_async.py

DESCRIPTION:
    This sample demonstrates how to send a small number of logs to a Log Analytics workspace.

    Note: This sample requires the azure-identity library.

USAGE:
    python sample_send_small_logs_async.py

    Set the environment variables with your own values before running the sample:
    1) DATA_COLLECTION_ENDPOINT - your data collection endpoint
    2) LOGS_DCR_RULE_ID - your data collection rule immutable ID
    3) LOGS_DCR_STREAM_NAME - your data collection rule stream name

    If using an application service principal for authentication, set the following:
    1) AZURE_TENANT_ID - your Azure AD tenant (directory) ID
    2) AZURE_CLIENT_ID - your Azure AD client (application) ID
    3) AZURE_CLIENT_SECRET - your Azure AD client secret
"""

import asyncio
import os

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient


async def send_logs():
    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    rule_id = os.environ['LOGS_DCR_RULE_ID']
    body = [
          {
            "Time": "2021-12-08T23:51:14.1104269Z",
            "Computer": "Computer1",
            "AdditionalContext": "sabhyrav-2"
          },
          {
            "Time": "2021-12-08T23:51:14.1104269Z",
            "Computer": "Computer2",
            "AdditionalContext": "sabhyrav"
          }
        ]
    credential = DefaultAzureCredential()

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
    async with client:
      try:
          await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
      except HttpResponseError as e:
          print(f"Upload failed: {e}")
    await credential.close()


if __name__ == '__main__':
    asyncio.run(send_logs())
