"""
Usage: python sample_custom_error_callback_async.py
"""
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion import UploadLogsError
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

    failed_logs = []

    # Sample callback that stores the logs that failed to upload.
    async def on_error(error: UploadLogsError) -> None:
        print("Log chunk failed to upload with error: ", error.error)
        failed_logs.extend(error.failed_logs)

    # Sample callback that just ignores the error.
    async def on_error_pass(_) -> None:
        pass

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
    async with client:
      await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, on_error=on_error)

      # Retry once with any failed logs, and this time ignore any errors.
      if failed_logs:
        print("Retrying logs that failed to upload...")
        await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=failed_logs, on_error=on_error_pass)
    await credential.close()


if __name__ == '__main__':
    asyncio.run(send_logs())
