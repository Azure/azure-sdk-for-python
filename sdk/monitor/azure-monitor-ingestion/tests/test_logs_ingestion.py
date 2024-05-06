# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import gzip
import json
import os
from unittest import mock
import uuid

import pytest

from azure.core.exceptions import HttpResponseError
from azure.monitor.ingestion import LogsIngestionClient

from base_testcase import LogsIngestionClientTestCase


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


class TestLogsIngestionClient(LogsIngestionClientTestCase):

    def test_send_logs(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])
        with client:
            client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=LOGS_BODY)

    def test_send_logs_large(self, recorded_test, monitor_info, large_data):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])
        with client:
            client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=large_data)

    def test_send_logs_error(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        with pytest.raises(HttpResponseError) as ex:
            client.upload(rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body)

    def test_send_logs_error_custom(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])
        body = [{"foo": "bar"}]

        def on_error(e):
            on_error.called = True
            assert isinstance(e.error, HttpResponseError)
            assert e.failed_logs == body

        on_error.called = False

        client.upload(
            rule_id='bad-rule', stream_name=monitor_info['stream_name'], logs=body, on_error=on_error)
        assert on_error.called

    def test_send_logs_json_file(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])

        temp_file = str(uuid.uuid4()) + '.json'
        with open(temp_file, 'w') as f:
            json.dump(LOGS_BODY, f)

        with client:
            with open(temp_file, 'r') as f:
                client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=f)
        os.remove(temp_file)

    @pytest.mark.live_test_only("Issues recording binary streams with test-proxy")
    def test_send_logs_gzip_file(self, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])

        temp_file = str(uuid.uuid4()) + '.json.gz'
        with gzip.open(temp_file, 'wb') as f:
            f.write(json.dumps(LOGS_BODY).encode('utf-8'))

        with open(temp_file, 'rb') as f:
            client.upload(rule_id=monitor_info['dcr_id'], stream_name=monitor_info['stream_name'], logs=f)
        os.remove(temp_file)

    def test_abort_error_handler(self, monitor_info):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])

        class TestException(Exception):
            pass

        def on_error(e):
            on_error.called = True
            if isinstance(e.error, RuntimeError):
                raise TestException("Abort")
            return

        on_error.called = False

        with client:
            # No exception should be raised
            with mock.patch("azure.monitor.ingestion._operations._patch.GeneratedOps._upload",
                            side_effect=ConnectionError):
                client.upload(
                    rule_id=monitor_info['dcr_id'],
                    stream_name=monitor_info['stream_name'],
                    logs=LOGS_BODY,
                    on_error=on_error)

            assert on_error.called

            on_error.called = False
            # Exception should now be raised since error handler checked for RuntimeError.
            with mock.patch("azure.monitor.ingestion._operations._patch.GeneratedOps._upload",
                            side_effect=RuntimeError):
                with pytest.raises(TestException):
                    client.upload(
                        rule_id=monitor_info['dcr_id'],
                        stream_name=monitor_info['stream_name'],
                        logs=LOGS_BODY,
                        on_error=on_error)

        assert on_error.called

    @pytest.mark.parametrize("logs", ['[{"foo": "bar"}]', "foo", {"foo": "bar"}, None])
    def test_invalid_logs_format(self, monitor_info, logs):
        client = self.get_client(
            LogsIngestionClient, self.get_credential(LogsIngestionClient), endpoint=monitor_info['dce'])

        with pytest.raises(ValueError):
            client.upload(rule_id="rule", stream_name="stream", logs=logs)
