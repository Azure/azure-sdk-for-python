import os
import asyncio
import pytest
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity.aio import ClientSecretCredential

def _credential():
    credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )
    return credential

@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_send_logs():
    endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
    credential = _credential()

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

    response = await client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
