"""
Usage: python sample_custom_error_callback.py
"""
import os

from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient, UploadLogsError


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

failed_logs = []

# Sample callback that stores the logs that failed to upload.
def on_error(error: UploadLogsError) -> None:
    print("Log chunk failed to upload with error: ", error.error)
    failed_logs.extend(error.failed_logs)

# Sample callback that just ignores the error.
def on_error_pass(*_) -> None:
    pass

client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, on_error=on_error)

# Retry once with any failed logs, and this time ignore any errors.
if failed_logs:
    print("Retrying logs that failed to upload...")
    client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=failed_logs, on_error=on_error_pass)
