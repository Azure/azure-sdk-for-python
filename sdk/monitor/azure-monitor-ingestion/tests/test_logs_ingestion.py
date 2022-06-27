import os
import pytest
from azure.monitor.ingestion import LogsIngestionClient, SendLogsStatus
from azure.identity import DefaultAzureCredential

@pytest.mark.live
def test_send_logs():
    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    credential = DefaultAzureCredential()

    client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

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

    response = client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
