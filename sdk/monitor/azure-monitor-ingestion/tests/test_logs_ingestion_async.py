# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from azure.monitor.ingestion.aio import LogsIngestionClient
from devtools_testutils import AzureRecordedTestCase


class TestLogsIngestionClientAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_send_logs_async(self, recorded_test, monitor_info):
        client = self.create_client_from_credential(
            LogsIngestionClient, self.get_credential(LogsIngestionClient, is_async=True), endpoint=monitor_info['dce'])
        async with client:
            body = [
                {
                    "Time": "2021-12-08T23:51:14.1104269Z",
                    "Computer": "Computer1",
                    "AdditionalContext": {
                        "testContextKey": 3,
                        "CounterName": "AppMetric1"
                    }
                },
                {
                    "Time": "2021-12-08T23:51:14.1104269Z",
                    "Computer": "Computer2",
                    "AdditionalContext": {
                        "testContextKey": 2,
                        "CounterName": "AppMetric1"
                    }
                }
            ]
            await client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=body)
