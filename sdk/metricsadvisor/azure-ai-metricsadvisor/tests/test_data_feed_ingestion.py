# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
import functools
from datetime import timezone
import pytest
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids, API_KEY
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_get_data_feed_ingestion_progress(self, client):

        ingestion = client.get_data_feed_ingestion_progress(
            data_feed_id=self.data_feed_id
        )
        assert ingestion.latest_success_timestamp is not None
        assert ingestion.latest_active_timestamp is not None

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_data_feed_ingestion_status(self, client):

        ingestions = client.list_data_feed_ingestion_status(
            data_feed_id=self.data_feed_id,
            start_time=datetime.datetime(2021, 8, 9, tzinfo=timezone.utc),
            end_time=datetime.datetime(2021, 9, 16, tzinfo=timezone.utc),
        )
        assert len(list(ingestions)) > 0

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_data_feed_ingest_status_skip(self, client):

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
        ingestions_list = list(ingestions)
        ingestions_with_skips_list = list(ingestions_with_skips)
        assert len(ingestions_list) == len(ingestions_with_skips_list) + 5

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # API key only. Error: (ERROR_PRIVILEGE_FAILED) You have no permission to do it.
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_refresh_data_feed_ingestion(self, client):
        client.refresh_data_feed_ingestion(
            self.data_feed_id,
            start_time=datetime.datetime(2022, 2, 28, tzinfo=timezone.utc),
            end_time=datetime.datetime(2022, 3, 1, tzinfo=timezone.utc),
        )

