# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
from dateutil.tz import tzutc
import pytest
from devtools_testutils import AzureTestCase

from base_testcase_aad_async import TestMetricsAdvisorAdministrationClientBaseAsync


class TestMetricsAdvisorAdministrationClientAsync(TestMetricsAdvisorAdministrationClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_get_data_feed_ingestion_progress(self):
        async with self.admin_client:
            ingestion = await self.admin_client.get_data_feed_ingestion_progress(
                data_feed_id=self.data_feed_id
            )
            self.assertIsNotNone(ingestion.latest_success_timestamp)
            self.assertIsNotNone(ingestion.latest_active_timestamp)

    @AzureTestCase.await_prepared_test
    async def test_list_data_feed_ingestion_status(self):
        async with self.admin_client:
            ingestions = self.admin_client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2020, 8, 9, tzinfo=tzutc()),
                end_time=datetime.datetime(2020, 9, 16, tzinfo=tzutc()),
            )
            ingestions_list = []
            async for status in ingestions:
                ingestions_list.append(status)
            assert len(list(ingestions_list)) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_data_feed_ingestion_status_with_skip(self):
        async with self.admin_client:
            ingestions = self.admin_client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2020, 8, 9, tzinfo=tzutc()),
                end_time=datetime.datetime(2020, 9, 16, tzinfo=tzutc()),
            )

            ingestions_with_skips = self.admin_client.list_data_feed_ingestion_status(
                data_feed_id=self.data_feed_id,
                start_time=datetime.datetime(2020, 8, 9, tzinfo=tzutc()),
                end_time=datetime.datetime(2020, 9, 16, tzinfo=tzutc()),
                skip=5
            )
            ingestions_list = []
            async for status in ingestions:
                ingestions_list.append(status)

            ingestions_with_skips_list = []
            async for status in ingestions_with_skips:
                ingestions_with_skips_list.append(status)

            assert len(ingestions_list) == len(ingestions_with_skips_list) + 5

    @AzureTestCase.await_prepared_test
    async def test_refresh_data_feed_ingestion(self):
        async with self.admin_client:
            await self.admin_client.refresh_data_feed_ingestion(
                self.data_feed_id,
                start_time=datetime.datetime(2020, 10, 1, tzinfo=tzutc()),
                end_time=datetime.datetime(2020, 10, 2, tzinfo=tzutc()),
            )
