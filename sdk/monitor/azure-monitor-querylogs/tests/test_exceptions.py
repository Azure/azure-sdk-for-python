# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta

import pytest

from azure.identity import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.querylogs import (
    LogsQueryClient,
    LogsBatchQuery,
    LogsQueryError,
    LogsQueryPartialResult,
    LogsQueryStatus,
)

from base_testcase import AzureMonitorQueryLogsTestCase


class TestQueryExceptions(AzureMonitorQueryLogsTestCase):

    def test_logs_single_query_fatal_exception(self, recorded_test):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        with pytest.raises(HttpResponseError):
            client.query_workspace("bad_workspace_id", "AppRequests", timespan=None)

    def test_logs_single_query_partial_exception(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)"""
        response = client.query_workspace(monitor_info["workspace_id"], query, timespan=timedelta(days=1))
        assert response.__class__ == LogsQueryPartialResult
        assert response.status == LogsQueryStatus.PARTIAL
        assert response.partial_error is not None
        assert response.partial_data is not None
        assert response.partial_error.details is not None
        assert response.partial_error.code == "PartialError"
        assert response.partial_error.__class__ == LogsQueryError

    def test_logs_resource_query_fatal_exception(self, recorded_test):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        with pytest.raises(HttpResponseError):
            client.query_resource("/bad/resource/id", "AzureActivity", timespan=None)

    def test_logs_resource_query_partial_exception(self, recorded_test, monitor_info):
        # Since this is logs-only package, we'll test workspace query instead
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)"""
        response = client.query_workspace(monitor_info["workspace_id"], query, timespan=timedelta(days=1))
        assert response.__class__ == LogsQueryPartialResult
        assert response.status == LogsQueryStatus.PARTIAL
        assert response.partial_error is not None
        assert response.partial_data is not None
        assert response.partial_error.details is not None
        assert response.partial_error.code == "PartialError"
        assert response.partial_error.__class__ == LogsQueryError

    def test_logs_batch_query_fatal_exception(self, recorded_test, monitor_info):
        credential = ClientSecretCredential(
            client_id="00000000-0000-0000-0000-000000000000",
            client_secret="bad_secret",
            tenant_id="00000000-0000-0000-0000-000000000000",
        )
        client = self.get_client(LogsQueryClient, credential)
        requests = [
            LogsBatchQuery(
                query="AzureActivity | summarize count()",
                timespan=timedelta(hours=1),
                workspace_id=monitor_info["workspace_id"],
            ),
            LogsBatchQuery(
                query="""AppRequestsss | take 10""",
                timespan=(datetime(2021, 6, 2), timedelta(days=1)),
                workspace_id=monitor_info["workspace_id"],
            ),
            LogsBatchQuery(
                query="""let Weight = 92233720368547758;
                range x from 1 to 3 step 1
                | summarize percentilesw(x, Weight * 100, 50)""",
                workspace_id=monitor_info["workspace_id"],
                timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
                include_statistics=True,
            ),
        ]
        with pytest.raises(HttpResponseError):
            responses = client.query_batch(requests)

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    def test_logs_query_batch_partial_exception(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        requests = [
            LogsBatchQuery(
                workspace_id=monitor_info["workspace_id"],
                query="AzureActivity | summarize count()",
                timespan=timedelta(hours=1),
            ),
            LogsBatchQuery(
                workspace_id=monitor_info["workspace_id"],
                query="""let Weight = 92233720368547758;
                range x from 1 to 3 step 1
                | summarize percentilesw(x, Weight * 100, 50)""",
                timespan=timedelta(days=1),
            ),
        ]
        responses = client.query_batch(requests)
        assert responses[1].__class__ == LogsQueryPartialResult

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    def test_logs_query_batch_non_fatal_exception(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        requests = [
            LogsBatchQuery(
                workspace_id=monitor_info["workspace_id"],
                query="AzureActivity | summarize count()",
                timespan=timedelta(hours=1),
            ),
            LogsBatchQuery(workspace_id=monitor_info["workspace_id"], query="not a valid query", timespan=None),
        ]
        responses = client.query_batch(requests)
        assert responses[1].__class__ == LogsQueryError

    def test_logs_query_batch_raises_with_no_timespan(self, monitor_info):
        with pytest.raises(TypeError):
            LogsBatchQuery(
                workspace_id=monitor_info["workspace_id"],
                query="AzureActivity | summarize count()",
            )

    def test_logs_bad_query_fatal_exception(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        with pytest.raises(HttpResponseError):
            client.query_workspace(monitor_info["workspace_id"], "not a table", timespan=None)

    def test_logs_query_result_partial_success_iterator(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)"""
        response = client.query_workspace(monitor_info["workspace_id"], query, timespan=None)
        # LogsQueryPartialResult as an iterator should return tables from `partial_data`
        assert response.__class__ == LogsQueryPartialResult
        for table in response:
            assert table is not None

    def test_logs_invalid_credential(self, recorded_test, monitor_info):
        credential = ClientSecretCredential(client_id="client_id", client_secret="client_secret", tenant_id="tenant-id")
        client = LogsQueryClient(credential)
        with pytest.raises(HttpResponseError) as e:
            client.query_workspace(monitor_info["workspace_id"], "AppRequests", timespan=None)
