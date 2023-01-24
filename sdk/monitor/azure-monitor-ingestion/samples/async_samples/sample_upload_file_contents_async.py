"""
Upload a file containing a list of JSON objects to Azure Monitor.

Usage: python sample_upload_file_contents_async.py
"""
import asyncio
from datetime import datetime
import json
import os

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient


async def upload_file_contents() -> None:
    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    credential = DefaultAzureCredential()

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

    # Update this to point to a file containing a list of JSON objects.
    FILE_PATH ="../../test-logs.json"

    async with client:
        # Option 1: Upload the file contents by passing in the file stream. With this option, no chunking is done, and the
        # file contents are uploaded as is through one request. Subject to size service limits.
        with open(FILE_PATH, "r") as f:
            try:
                await client.upload(
                    rule_id=os.environ['LOGS_DCR_RULE_ID'],
                    stream_name=os.environ['LOGS_DCR_STREAM_NAME'],
                    logs=f)
            except HttpResponseError as e:
                print(f"Upload failed: {e}")

        # Option 2: Upload the file contents by passing in the list of JSON objects. Chunking is done automatically, and the
        # file contents are uploaded through multiple requests.
        with open(FILE_PATH, "r") as f:
            logs = json.load(f)
            try:
                await client.upload(
                    rule_id=os.environ['LOGS_DCR_RULE_ID'],
                    stream_name=os.environ['LOGS_DCR_STREAM_NAME'],
                    logs=logs)
            except HttpResponseError as e:
                print(f"Upload failed: {e}")

    await credential.close()


if __name__ == '__main__':
    asyncio.run(upload_file_contents())
