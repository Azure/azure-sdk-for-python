"""
Usage: python sample_custom_error_callback.py
"""
import os

from azure.core.exceptions import HttpResponseError
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
def on_error_save(error: UploadLogsError) -> None:
    print("Log chunk failed to upload with error: ", error.error)
    failed_logs.extend(error.failed_logs)

# Sample callback that just ignores the error.
def on_error_pass(_) -> None:
    pass

# Sample callback that raises the error if it corresponds to a specific HTTP error code.
# This aborts the rest of the upload.
def on_error_abort(error: UploadLogsError) -> None:
    if isinstance(error.error, HttpResponseError) and error.error.status_code in (400, 401, 403):
        print("Aborting upload...")
        raise error.error

client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, on_error=on_error_save)

# Retry once with any failed logs, and this time ignore any errors.
if failed_logs:
    print("Retrying logs that failed to upload...")
    client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=failed_logs, on_error=on_error_pass)
