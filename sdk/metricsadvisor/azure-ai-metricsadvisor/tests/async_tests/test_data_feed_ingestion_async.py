# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
import functools
from datetime import timezone
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase
from azure.ai.metricsadvisor.aio import MetricsAdvisorAdministrationClient

from base_testcase_async import MetricsAdvisorClientPreparer, TestMetricsAdvisorClientBase, CREDENTIALS, ids, API_KEY
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClientAsync(TestMetricsAdvisorClientBase):

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY,
                             ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_get_data_feed_ingestion_progress(self, client):
        async with client:
            ingestion = await client.get_data_feed_ingestion_progress(
                data_feed_id=self.data_feed_id
            )
            assert ingestion.latest_success_timestamp is not None
            assert ingestion.latest_active_timestamp is not None

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY,
                             ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_data_feed_ingestion_status(self, client):
        async with client:
            ingestions = client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2021, 8, 9, tzinfo=timezone.utc),
                end_time=datetime.datetime(2021, 9, 16, tzinfo=timezone.utc),
            )
            ingestions_list = []
            async for status in ingestions:
                ingestions_list.append(status)
            assert len(list(ingestions_list)) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY,
                             ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_data_feed_ingest_status_skip(self, client):
        async with client:
            ingestions = client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2021, 8, 9, tzinfo=timezone.utc),
                end_time=datetime.datetime(2021, 9, 16, tzinfo=timezone.utc),
            )

            ingestions_with_skips = client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2021, 8, 9, tzinfo=timezone.utc),
                end_time=datetime.datetime(2021, 9, 16, tzinfo=timezone.utc),
                skip=5
            )
            ingestions_list = []
            async for status in ingestions:
                ingestions_list.append(status)

            ingestions_with_skips_list = []
            async for status in ingestions_with_skips:
                ingestions_with_skips_list.append(status)

            assert len(ingestions_list) == len(ingestions_with_skips_list) + 5

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY,
                             ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_refresh_data_feed_ingestion(self, client):
        async with client:
            await client.refresh_data_feed_ingestion(
                self.data_feed_id,
                start_time=datetime.datetime(2022, 2, 28, tzinfo=timezone.utc),
                end_time=datetime.datetime(2022, 3, 1, tzinfo=timezone.utc),
            )
