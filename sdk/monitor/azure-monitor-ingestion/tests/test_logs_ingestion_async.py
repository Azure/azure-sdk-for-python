# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError
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

    @pytest.mark.asyncio
    async def test_send_logs_error(self, recorded_test, monitor_info):
        client = self.create_client_from_credential(
            LogsIngestionClient, self.get_credential(LogsIngestionClient, is_async=True), endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        with pytest.raises(HttpResponseError) as ex:
            async with client:
                await client.upload(rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body)

    @pytest.mark.asyncio
    async def test_send_logs_error_custom(self, recorded_test, monitor_info):
        client = self.create_client_from_credential(
            LogsIngestionClient, self.get_credential(LogsIngestionClient, is_async=True), endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        async def on_error(**kwargs):
            on_error.called = True
            assert isinstance(kwargs.get("error"), HttpResponseError)
            assert kwargs.get("logs") == body

        on_error.called = False

        async with client:
            await client.upload(
                rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body, on_error=on_error)
        assert on_error.called
