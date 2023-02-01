"""
Usage: python sample_send_small_logs.py
"""
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

rule_id = os.environ['LOGS_DCR_RULE_ID']
body = [
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer1",
        "AdditionalContext": "context-2"
      },
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer2",
        "AdditionalContext": "context"
      }
    ]

try:
    client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
except HttpResponseError as e:
    print(f"Upload failed: {e}")
