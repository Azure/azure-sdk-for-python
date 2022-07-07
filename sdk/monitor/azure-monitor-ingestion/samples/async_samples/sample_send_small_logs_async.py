"""
Usage: python sample_send_small_logs_async.py
"""

import os
import asyncio
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.monitor.ingestion import UploadLogsStatus
from azure.identity.aio import DefaultAzureCredential

async def send_logs():
    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    credential = DefaultAzureCredential()

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

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

    response = await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
    if response.status != UploadLogsStatus.SUCCESS:
        failed_logs = response.failed_logs_index
        print(failed_logs)


if __name__ == '__main__':
    asyncio.run(await send_logs())
