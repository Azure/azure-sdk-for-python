# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import timedelta, datetime

import pytest

from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsBatchQuery, LogsQueryError,LogsQueryResult, LogsQueryPartialResult
from azure.monitor.query.aio import LogsQueryClient

from base_testcase import AzureMonitorQueryLogsTestCase


class TestQueryExceptionsAsync(AzureMonitorQueryLogsTestCase):

    @pytest.mark.asyncio
    async def test_logs_single_query_fatal_exception(self, recorded_test):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            with pytest.raises(HttpResponseError):
                await client.query_workspace('bad_workspace_id', 'AppRequests', timespan=None)

    @pytest.mark.asyncio
    async def test_logs_single_query_partial_exception_not_allowed(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """let Weight = 92233720368547758;
            range x from 1 to 3 step 1
            | summarize percentilesw(x, Weight * 100, 50)"""
            response = await client.query_workspace(monitor_info['workspace_id'], query, timespan=timedelta(days=1))
            assert response.__class__ == LogsQueryPartialResult
            assert response.partial_error is not None
            assert response.partial_error.code == 'PartialError'
            assert response.partial_error.__class__ == LogsQueryError

    @pytest.mark.asyncio
    async def test_logs_resource_query_fatal_exception(self, recorded_test):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            with pytest.raises(HttpResponseError):
                await client.query_resource('/bad/resource/id', 'AzureActivity', timespan=None)

    @pytest.mark.asyncio
    async def test_logs_resource_query_partial_exception(self, recorded_test, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            query = """let Weight = 92233720368547758;
            range x from 1 to 3 step 1
            | summarize percentilesw(x, Weight * 100, 50)"""
            response = await client.query_resource(monitor_info['metrics_resource_id'], query, timespan=timedelta(days=1))
            assert response.__class__ == LogsQueryPartialResult
            assert response.partial_error is not None
            assert response.partial_error.code == 'PartialError'
            assert response.partial_error.__class__ == LogsQueryError

    @pytest.mark.asyncio
    async def test_logs_batch_query_fatal_exception(self, recorded_test, monitor_info):
        credential  = ClientSecretCredential(
            client_id = monitor_info['client_id'],
            client_secret = 'bad_secret',
            tenant_id = monitor_info['tenant_id']
        )
        client = self.get_client(LogsQueryClient, credential)
        async with client:
            requests = [
                LogsBatchQuery(
                    query="AzureActivity | summarize count()",
                    timespan=timedelta(hours=1),
                    workspace_id=monitor_info['workspace_id']
                ),
                LogsBatchQuery(
                    query= """AppRequestsss | take 10""",
                    timespan=(datetime(2021, 6, 2), timedelta(days=1)),
                    workspace_id=monitor_info['workspace_id']
                ),
                LogsBatchQuery(
                    query= """let Weight = 92233720368547758;
                    range x from 1 to 3 step 1
                    | summarize percentilesw(x, Weight * 100, 50)""",
                    workspace_id=monitor_info['workspace_id'],
                    timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
                    include_statistics=True
                ),
            ]
            with pytest.raises(HttpResponseError):
                await client.query_batch(requests)

    @pytest.mark.live_test_only("Issues recording dynamic 'id' values in requests/responses")
    @pytest.mark.asyncio
    async def test_logs_batch_query_partial_exception_not_allowed(self, monitor_info):
        client = self.get_client(
            LogsQueryClient, self.get_credential(LogsQueryClient, is_async=True))
        async with client:
            requests = [
                LogsBatchQuery(
                    query="AzureActivity | summarize count()",
                    timespan=timedelta(hours=1),
                    workspace_id=monitor_info['workspace_id']
                ),
                LogsBatchQuery(
                    query= """bad query | take 10""",
                    timespan=(datetime(2021, 6, 2), timedelta(days=1)),
                    workspace_id=monitor_info['workspace_id']
                ),
                LogsBatchQuery(
                    query= """let Weight = 92233720368547758;
                    range x from 1 to 3 step 1
                    | summarize percentilesw(x, Weight * 100, 50)""",
                    workspace_id=monitor_info['workspace_id'],
                    timespan=(datetime(2021, 6, 2), datetime(2021, 6, 3)),
                    include_statistics=True
                ),
            ]
            responses = await client.query_batch(requests)
            r1, r2, r3 = responses[0], responses[1], responses[2]
            assert r1.__class__ == LogsQueryResult
            assert r2.__class__ == LogsQueryError
            assert r3.__class__ == LogsQueryPartialResult
