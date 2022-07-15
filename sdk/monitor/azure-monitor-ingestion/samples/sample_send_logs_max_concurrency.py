"""
Usage: python sample_send_logs_max_concurrency.py
"""

import os
from azure.monitor.ingestion import LogsIngestionClient, UploadLogsStatus
from azure.identity import DefaultAzureCredential

endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential)

rule_id = os.environ['LOGS_DCR_RULE_ID']
body = []

for i in range(50000):
    body.append(
      {
          "Time": "2021-12-08T23:51:14.1104269Z",
          "Computer": "Computer1",
          "AdditionalContext": "sabhyrav-" + str(i)
        }
    )

response = client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, max_concurrency=3)
if response.status != UploadLogsStatus.SUCCESS:
    failed_logs = response.failed_logs_index
    print(failed_logs)
