# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta

import pytest

from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsBatchQuery, LogsQueryError, LogsTable, LogsQueryResult, LogsTableRow
from azure.monitor.query.aio import LogsQueryClient

from base_testcase import AzureMonitorQueryLogsTestCase


class TestLogsClientAsync(AzureMonitorQueryLogsTestCase):

    @pytest.mark.asyncio
    async def test_logs_auth(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """AppRequests |
            where TimeGenerated > ago(12h) |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

            # returns LogsQueryResult
            response = await client.query_workspace(monitor_info['workspace_id'], query, timespan=None)

            assert response is not None
            assert response.tables is not None

    @pytest.mark.asyncio
    async def test_logs_auth_no_timespan(self, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """AppRequests |
            where TimeGenerated > ago(12h) |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

            # returns LogsQueryResult
            with pytest.raises(TypeError):
                await client.query_workspace(monitor_info['workspace_id'], query)

    @pytest.mark.asyncio
    async def test_logs_server_timeout(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))

        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.query_workspace(
                    monitor_info['workspace_id'],
                    "range x from 1 to 1000000000000000 step 1 | count",
                    timespan=None,
                    server_timeout=1,
                )

        assert 'Gateway timeout' in e.value.message

    @pytest.mark.asyncio
    async def test_logs_query_batch_raises_on_no_timespan(self, monitor_info):
        with pytest.raises(TypeError):
            LogsBatchQuery(
                workspace_id=monitor_info['workspace_id'],
                query="AzureActivity | summarize count()",
            )

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    @pytest.mark.asyncio
    async def test_logs_query_batch_default(self, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            requests = [
                LogsBatchQuery(
                    monitor_info['workspace_id'],
                    query="AzureActivity | summarize count()",
                    timespan=timedelta(hours=1)
                ),
                LogsBatchQuery(
                    monitor_info['workspace_id'],
                    query= """AppRequests | take 10  |
                        summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
                    timespan=timedelta(hours=1),
                ),
                LogsBatchQuery(
                    monitor_info['workspace_id'],
                    query= "Wrong query | take 2",
                    timespan=None
                ),
            ]
            response = await client.query_batch(requests)

            assert len(response) == 3
            r0 = response[0]
            assert r0.tables[0].columns == ['count_']
            r1 = response[1]
            assert r1.tables[0].columns[0] == 'TimeGenerated'
            assert r1.tables[0].columns[1] == '_ResourceId'
            assert r1.tables[0].columns[2] == 'avgRequestDuration'
            r2 = response[2]
            assert r2.__class__ == LogsQueryError

    @pytest.mark.asyncio
    async def test_logs_single_query_additional_workspaces_async(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = (
                f"{monitor_info['table_name']} | where TimeGenerated > ago(100d)"
                "| project TenantId | summarize count() by TenantId"
            )

            # returns LogsQueryResult
            response = await client.query_workspace(
                monitor_info['workspace_id'],
                query,
                timespan=None,
                additional_workspaces=[monitor_info['secondary_workspace_id']],
                )

            assert response
            assert len(response.tables[0].rows) == 2

    @pytest.mark.skip("Flaky deserialization issues with msrest. Re-enable after removing msrest dependency.")
    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    @pytest.mark.asyncio
    async def test_logs_query_batch_additional_workspaces(self, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
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
            response = await client.query_batch(requests)

            assert len(response) == 3
            for resp in response:
                assert len(resp.tables[0].rows) == 2

    @pytest.mark.asyncio
    async def test_logs_single_query_with_visualization(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """AppRequests | take 10"""

            # returns LogsQueryResult
            response = await client.query_workspace(
                monitor_info['workspace_id'], query, timespan=None, include_visualization=True)

            assert response.visualization is not None

    @pytest.mark.asyncio
    async def test_logs_single_query_with_visualization_and_stats(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """AppRequests | take 10"""
            # returns LogsQueryResult
            response = await client.query_workspace(
                monitor_info['workspace_id'], query, timespan=None, include_visualization=True, include_statistics=True)

            assert response.visualization is not None
            assert response.statistics is not None

    @pytest.mark.asyncio
    async def test_logs_query_result_iterate_over_tables(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = "AppRequests | take 10; AppRequests | take 5"
            response = await client.query_workspace(
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

    @pytest.mark.asyncio
    async def test_logs_query_result_row_type(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = "AppRequests | take 5"
            response = await client.query_workspace(
                monitor_info['workspace_id'],
                query,
                timespan=None,
            )

            ## should iterate over tables
            for table in response:
                assert table.__class__ == LogsTable

                for row in table.rows:
                    assert row.__class__ == LogsTableRow

    @pytest.mark.asyncio
    async def test_logs_resource_query(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = "requests | summarize count()"

            response = await client.query_resource(monitor_info['metrics_resource_id'], query, timespan=None)

            assert response is not None
            assert response.tables is not None
            assert len(response.tables[0].rows) == 1

    @pytest.mark.asyncio
    async def test_logs_resource_query_additional_options(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = "requests | summarize count()"

            response = await client.query_resource(
                monitor_info['metrics_resource_id'],
                query,
                timespan=None,
                include_statistics=True,
                include_visualization=True
            )

            assert response.visualization is not None
            assert response.statistics is not None

    @pytest.mark.asyncio
    async def test_client_different_endpoint(self):
        credential = self.get_credential(LogsQueryClient, is_async=True)
        endpoint = "https://api.loganalytics.azure.cn/v1"
        client = LogsQueryClient(credential, endpoint=endpoint)

        assert client._endpoint == endpoint
        assert "https://api.loganalytics.azure.cn/.default" in client._client._config.authentication_policy._scopes
