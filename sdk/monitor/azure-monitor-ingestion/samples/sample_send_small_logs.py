"""
Usage: python sample_send_small_logs.py
"""

import os
from azure.monitor.ingestion import LogsIngestionClient, SendLogsStatus
from azure.identity import DefaultAzureCredential

endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential)

rule_id = os.environ['LOGS_DCR_RULE_ID']
body = [
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer1",
        "AdditionalContext": {
          "InstanceName": "user1",
          "TimeZone": "Pacific Time",
          "Level": 4,
          "CounterName": "AppMetric1",
          "CounterValue": 15.3
        }
      },
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer2",
        "AdditionalContext": {
          "InstanceName": "user2",
          "TimeZone": "Central Time",
          "Level": 3,
          "CounterName": "AppMetric1",
          "CounterValue": 23.5
        }
      }
    ]

response = client.send_logs(rule_id=rule_id, stream='test-rg', body=body, max_concurrency=1)
if response.status != SendLogsStatus.SUCCESS:
    failed_logs = response.failed_logs_index
    print(failed_logs)
