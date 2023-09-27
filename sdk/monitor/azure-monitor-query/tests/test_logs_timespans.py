# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta
import json

from msrest.serialization import UTC
import pytest

from azure.monitor.query import LogsQueryClient
from azure.monitor.query._helpers import construct_iso8601

from base_testcase import AzureMonitorQueryLogsTestCase


class TestLogsTimespans(AzureMonitorQueryLogsTestCase):

    def test_query_no_duration(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests |
        where TimeGenerated > ago(12h) |
        summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

        def callback(request):
            dic = json.loads(request.http_request.body)
            assert dic.get('timespan') is None
        # returns LogsQueryResult
        client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

    def test_query_start_and_end_time(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = "AppRequests | take 5"

        end_time = datetime(2022, 11, 8)
        start_time = end_time - timedelta(days=3)

        def callback(request):
            dic = json.loads(request.http_request.body)
            assert dic.get('timespan') is not None

        client.query_workspace(monitor_info['workspace_id'], query, timespan=(start_time, end_time), raw_request_hook=callback)

    def test_query_duration_and_start_time(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = "AppRequests | take 5"

        end_time = datetime(2022, 11, 8)
        start_time = end_time - timedelta(days=3)
        duration = timedelta(days=3)

        def callback(request):
            dic = json.loads(request.http_request.body)
            assert '/PT259200.0S' in dic.get('timespan')

        client.query_workspace(monitor_info['workspace_id'], query, timespan=(start_time,duration), raw_request_hook=callback)

    def test_query_duration_only(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = "AppRequests | take 5"

        duration = timedelta(days=3)

        def callback(request):
            dic = json.loads(request.http_request.body)
            assert 'PT259200.0S' in dic.get('timespan')

        client.query_workspace(monitor_info['workspace_id'], query, timespan=duration, raw_request_hook=callback)

    def test_duration_to_iso8601(self):
        d1 = timedelta(days=1)
        d2 = timedelta(weeks=1)
        d3 = timedelta(weeks=3, days=4)
        d4 = timedelta(seconds=10)
        d5 = timedelta(microseconds=1000)
        d6 = timedelta(milliseconds=100000)
        d7 = timedelta(hours=24, days=1)

        assert construct_iso8601(timespan=d1) == 'PT86400.0S'
        assert construct_iso8601(timespan=d2) == 'PT604800.0S'
        assert construct_iso8601(timespan=d3) == 'PT2160000.0S'
        assert construct_iso8601(timespan=d4) == 'PT10.0S'
        assert construct_iso8601(timespan=d5) == 'PT0.001S'
        assert construct_iso8601(timespan=d5) == 'PT0.001S'
        assert construct_iso8601(timespan=d7) == 'PT172800.0S'

        with pytest.raises(ValueError, match="timespan must be a timedelta or a tuple."):
            construct_iso8601(timespan=(datetime.now(UTC())))
