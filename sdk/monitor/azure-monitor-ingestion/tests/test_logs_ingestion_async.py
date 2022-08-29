import asyncio
import pytest
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity.aio import ClientSecretCredential

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from preparer import IngestionPreparer


class TestLogsIngestionClientAsync(AzureRecordedTestCase):
    @IngestionPreparer()
    @recorded_by_proxy_async
    async def test_send_logs_async(self, variables, azure_monitor_dce, azure_monitor_dcr_id, monitor_client_id, monitor_client_secret, monitor_tenant_id):
        credential = ClientSecretCredential(
        client_id = monitor_client_id,
        client_secret = monitor_client_secret,
        tenant_id = monitor_tenant_id
    )

        client = LogsIngestionClient(endpoint=azure_monitor_dce, credential=credential)
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

        response = await client.upload(rule_id=azure_monitor_dcr_id, stream_name="Custom-MyTableRawData", logs=body)
