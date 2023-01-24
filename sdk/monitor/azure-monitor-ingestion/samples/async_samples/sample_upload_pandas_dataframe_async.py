"""
In some cases, a user might have data stored in a pandas dataframe (e.g. from the result of another query)
and want to upload it to Azure Monitor. This sample demonstrates how to do so.

Usage: python sample_upload_pandas_dataframe_async.py
"""
import asyncio
from datetime import datetime
import json
import os

import pandas as pd

from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient


async def upload_dataframe() -> None:

    # Set up example DataFrame.
    data = [
        {
            "Time": datetime.now().astimezone(),
            "Computer": "Computer1",
            "AdditionalContext": "context-2"
        },
        {
            "Time": datetime.now().astimezone(),
            "Computer": "Computer2",
            "AdditionalContext": "context"
        }
    ]
    df = pd.DataFrame.from_dict(data)

    # If you have a populated dataframe that you want to upload, one approach is to use the DataFrame `to_json` method
    # which will convert any datetime objects to ISO 8601 strings. The `json.loads` method will then convert the JSON string
    # into a Python object that can be used for upload.
    body = json.loads(df.to_json(orient='records', date_format='iso'))

    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    credential = DefaultAzureCredential()

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)
    async with client:
        try:
            await client.upload(
                rule_id=os.environ['LOGS_DCR_RULE_ID'],
                stream_name=os.environ['LOGS_DCR_STREAM_NAME'],
                logs=body)
        except HttpResponseError as e:
            print(f"Upload failed: {e}")
    await credential.close()


if __name__ == '__main__':
    asyncio.run(upload_dataframe())
