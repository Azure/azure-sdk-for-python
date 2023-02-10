# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import gzip
import os
import json
import uuid

import pytest

from azure.core.exceptions import HttpResponseError
from azure.monitor.ingestion.aio import LogsIngestionClient
from devtools_testutils import AzureRecordedTestCase


LOGS_BODY = [
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


class TestLogsIngestionClientAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_send_logs_async(self, recorded_test, monitor_info):
        credential = self.get_credential(LogsIngestionClient, is_async=True)
        client = self.create_client_from_credential(
            LogsIngestionClient, credential, endpoint=monitor_info['dce'])
        async with client:
            await client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=LOGS_BODY)
        credential.close()

    @pytest.mark.asyncio
    async def test_send_logs_error(self, recorded_test, monitor_info):
        credential = self.get_credential(LogsIngestionClient, is_async=True)
        client = self.create_client_from_credential(
            LogsIngestionClient, credential, endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        with pytest.raises(HttpResponseError) as ex:
            async with client:
                await client.upload(rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body)
        credential.close()

    @pytest.mark.asyncio
    async def test_send_logs_error_custom(self, recorded_test, monitor_info):
        credential = self.get_credential(LogsIngestionClient, is_async=True)
        client = self.create_client_from_credential(
            LogsIngestionClient, credential, endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        async def on_error(e):
            on_error.called = True
            assert isinstance(e.error, HttpResponseError)
            assert e.failed_logs == body

        on_error.called = False

        async with client:
            await client.upload(
                rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body, on_error=on_error)
        assert on_error.called
        credential.close()

    @pytest.mark.asyncio
    async def test_send_logs_json_file(self, recorded_test, monitor_info):
        credential = self.get_credential(LogsIngestionClient, is_async=True)
        client = self.create_client_from_credential(
            LogsIngestionClient, credential, endpoint=monitor_info['dce'])

        temp_file = str(uuid.uuid4()) + '.json'
        with open(temp_file, 'w') as f:
            json.dump(LOGS_BODY, f)

        async with client:
            with open(temp_file, 'r') as f:
                await client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=f)
        os.remove(temp_file)
        credential.close()

    @pytest.mark.asyncio
    @pytest.mark.live_test_only("Issues recording binary streams with test-proxy")
    async def test_send_logs_gzip_file(self, monitor_info):
        credential = self.get_credential(LogsIngestionClient, is_async=True)
        client = self.create_client_from_credential(
            LogsIngestionClient, credential, endpoint=monitor_info['dce'])

        temp_file = str(uuid.uuid4()) + '.json.gz'
        with gzip.open(temp_file, 'wb') as f:
            f.write(json.dumps(LOGS_BODY).encode('utf-8'))

        async with client:
            with open(temp_file, 'rb') as f:
                await client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=f)
        os.remove(temp_file)
        credential.close()
