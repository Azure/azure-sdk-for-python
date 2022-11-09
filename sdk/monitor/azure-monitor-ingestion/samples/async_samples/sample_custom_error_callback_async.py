"""
Usage: python sample_custom_error_callback_async.py
"""

import os
import asyncio
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity.aio import DefaultAzureCredential


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

    failed_logs = []
    async def on_error(**kwargs):
        print("Log chunk failed to upload with error: ", kwargs.get("error"))
        failed_logs.extend(kwargs.get("logs", []))

    async def on_error_pass(**kwargs):
        return

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
    async with client:
      await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, on_error=on_error)

      # Retry once with any failed logs, and this time ignore any errors.
      print("Retrying logs that failed to upload...")
      if failed_logs:
        await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=failed_logs, on_error=on_error_pass)
    await credential.close()


if __name__ == '__main__':
    asyncio.run(send_logs())
