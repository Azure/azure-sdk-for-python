"""
Usage: python sample_send_small_logs_async.py
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
