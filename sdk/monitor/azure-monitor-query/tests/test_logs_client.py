# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta

import pytest

from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsBatchQuery, LogsQueryError, LogsTable, LogsQueryResult, LogsTableRow, LogsQueryPartialResult
from azure.monitor.query._helpers import native_col_type

from base_testcase import AzureMonitorQueryLogsTestCase


class TestLogsClient(AzureMonitorQueryLogsTestCase):

    def test_logs_single_query(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests |
        where TimeGenerated > ago(12h) |
        summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

        # returns LogsQueryResult
        response = client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

        assert response is not None
        assert response.tables is not None

    def test_logs_single_query_raises_no_timespan(self, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests |
        where TimeGenerated > ago(12h) |
        summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

        # returns LogsQueryResult
        with pytest.raises(TypeError):
            client.query_workspace(monitor_info['workspace_id'], query)

    def test_logs_single_query_with_non_200(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppInsights |
        where TimeGenerated > ago(12h)"""

        with pytest.raises(HttpResponseError) as e:
            client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

        assert "SemanticError" in e.value.message

    def test_logs_single_query_with_partial_success(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """let Weight = 92233720368547758;
        range x from 1 to 3 step 1
        | summarize percentilesw(x, Weight * 100, 50)"""
        response = client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

        assert response.partial_error is not None
        assert response.partial_data is not None
        assert response.__class__ == LogsQueryPartialResult

    def test_logs_server_timeout(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))

        with pytest.raises(HttpResponseError) as e:
            response = client.query_workspace(
                monitor_info['workspace_id'],
                "range x from 1 to 1000000000000000 step 1 | count",
                timespan=None,
                server_timeout=1,
            )
        assert 'Gateway timeout' in e.value.message

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    def test_logs_query_batch_default(self, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))

        requests = [
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query="AzureActivity | summarize count()",
                timespan=timedelta(hours=1)
            ),
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query= """AppRequests | take 10  |
                    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
                timespan=timedelta(hours=1),
            ),
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query= "Wrong query | take 2",
                timespan=None
            ),
        ]
        response = client.query_batch(requests)

        assert len(response) == 3

        r0 = response[0]
        assert r0.tables[0].columns == ['count_']
        r1 = response[1]
        assert r1.tables[0].columns[0] == 'TimeGenerated'
        assert r1.tables[0].columns[1] == '_ResourceId'
        assert r1.tables[0].columns[2] == 'avgRequestDuration'
        r2 = response[2]
        assert r2.__class__ == LogsQueryError

    def test_logs_single_query_with_statistics(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests | take 10"""

        # returns LogsQueryResult
        response = client.query_workspace(monitor_info['workspace_id'], query, timespan=None, include_statistics=True)

        assert response.statistics is not None

    def test_logs_single_query_with_visualization(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests | take 10"""

        # returns LogsQueryResult
        response = client.query_workspace(
            monitor_info['workspace_id'], query, timespan=None, include_visualization=True)

        assert response.visualization is not None

    def test_logs_single_query_with_visualization_and_stats(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = """AppRequests | take 10"""

        # returns LogsQueryResult
        response = client.query_workspace(
            monitor_info['workspace_id'], query, timespan=None, include_visualization=True, include_statistics=True)

        assert response.visualization is not None
        assert response.statistics is not None

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    def test_logs_query_batch_with_statistics_in_some(self, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))

        requests = [
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query="AzureActivity | summarize count()",
                timespan=timedelta(hours=1),
            ),
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query= """AppRequests|
                    summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
                timespan=timedelta(hours=1),
                include_statistics=True
            ),
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query= "AppRequests",
                timespan=None,
                include_statistics=True
            ),
        ]
        response = client.query_batch(requests)

        assert len(response) == 3
        assert response[0].statistics is None
        assert response[2].statistics is not None

    def test_logs_single_query_additional_workspaces(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = (
            f"{monitor_info['table_name']} | where TimeGenerated > ago(100d)"
            "| project TenantId | summarize count() by TenantId"
        )
        # returns LogsQueryResult
        response = client.query_workspace(
            monitor_info['workspace_id'],
            query,
            timespan=None,
            additional_workspaces=[monitor_info['secondary_workspace_id']],
            )

        assert response is not None
        assert len(response.tables[0].rows) == 2

    @pytest.mark.skip("Flaky deserialization issues with msrest. Re-enable after removing msrest dependency.")
    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    def test_logs_query_batch_additional_workspaces(self, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = (
            f"{monitor_info['table_name']} | where TimeGenerated > ago(100d)"
            "| project TenantId | summarize count() by TenantId"
        )
        requests = [
            LogsBatchQuery(
                monitor_info['workspace_id'],
                query,
                timespan=None,
                additional_workspaces=[monitor_info['secondary_workspace_id']]
            ),
            LogsBatchQuery(
                monitor_info['workspace_id'],
                query,
                timespan=None,
                additional_workspaces=[monitor_info['secondary_workspace_id']]
            ),
            LogsBatchQuery(
                    monitor_info['workspace_id'],
                    query,
                    timespan=None,
                    additional_workspaces=[monitor_info['secondary_workspace_id']]
            ),
        ]
        response = client.query_batch(requests)
        for resp in response:
            assert len(resp.tables[0].rows) == 2

    def test_logs_query_result_iterate_over_tables(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))

        query = "AppRequests | take 10; AppRequests | take 5"

        response = client.query_workspace(
            monitor_info['workspace_id'],
            query,
            timespan=None,
            include_statistics=True,
            include_visualization=True
        )

        ## should iterate over tables
        for item in response:
            assert item.__class__ == LogsTable

        assert response.statistics is not None
        assert response.visualization is not None
        assert len(response.tables) == 2
        assert response.__class__ == LogsQueryResult

    def test_logs_query_result_row_type(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))

        query = "AppRequests | take 5"

        response = client.query_workspace(
            monitor_info['workspace_id'],
            query,
            timespan=None,
        )

        ## should iterate over tables
        for table in response:
            assert table.__class__ == LogsTable

            for row in table.rows:
                assert row.__class__ == LogsTableRow

    def test_native_col_type(self):
        val = native_col_type('datetime', None)
        assert val is None

        val = native_col_type('datetime', '2020-10-10')
        assert val is not None

    def test_logs_resource_query(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = "requests | summarize count()"

        response = client.query_resource(monitor_info['metrics_resource_id'], query, timespan=None)

        assert response is not None
        assert response.tables is not None
        assert len(response.tables[0].rows) == 1

    def test_logs_resource_query_additional_options(self, recorded_test, monitor_info):
        client = self.get_client(LogsQueryClient, self.get_credential(LogsQueryClient))
        query = "requests | summarize count()"

        response = client.query_resource(
            monitor_info['metrics_resource_id'],
            query,
            timespan=None,
            include_statistics=True,
            include_visualization=True
        )

        assert response.visualization is not None
        assert response.statistics is not None

    def test_client_different_endpoint(self):
        credential = self.get_credential(LogsQueryClient)
        endpoint = "https://api.loganalytics.azure.cn/v1"
        client = LogsQueryClient(credential, endpoint=endpoint)

        assert client._endpoint == endpoint
        assert "https://api.loganalytics.azure.cn/.default" in client._client._config.authentication_policy._scopes
