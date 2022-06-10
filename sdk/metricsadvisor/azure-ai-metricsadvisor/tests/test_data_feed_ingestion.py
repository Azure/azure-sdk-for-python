# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
import functools
from dateutil.tz import tzutc
import pytest
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_get_data_feed_ingestion_progress(self, client, **kwargs):

        ingestion = client.get_data_feed_ingestion_progress(
            data_feed_id=self.data_feed_id
        )
        assert ingestion.latest_success_timestamp is not None
        assert ingestion.latest_active_timestamp is not None

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_data_feed_ingestion_status(self, client, **kwargs):

        ingestions = client.list_data_feed_ingestion_status(
            data_feed_id=self.data_feed_id,
            start_time=datetime.datetime(2021, 8, 9, tzinfo=tzutc()),
            end_time=datetime.datetime(2021, 9, 16, tzinfo=tzutc()),
        )
        assert len(list(ingestions)) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_data_feed_ingest_status_skip(self, client, **kwargs):

        ingestions = client.list_data_feed_ingestion_status(
            data_feed_id=self.data_feed_id,
            start_time=datetime.datetime(2021, 8, 9, tzinfo=tzutc()),
            end_time=datetime.datetime(2021, 9, 16, tzinfo=tzutc()),
        )

        ingestions_with_skips = client.list_data_feed_ingestion_status(
            data_feed_id=self.data_feed_id,
            start_time=datetime.datetime(2021, 8, 9, tzinfo=tzutc()),
            end_time=datetime.datetime(2021, 9, 16, tzinfo=tzutc()),
            skip=5
        )
        ingestions_list = list(ingestions)
        ingestions_with_skips_list = list(ingestions_with_skips)
        assert len(ingestions_list) == len(ingestions_with_skips_list) + 5

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_refresh_data_feed_ingestion(self, client, **kwargs):
        client.refresh_data_feed_ingestion(
            self.data_feed_id,
            start_time=datetime.datetime(2021, 10, 1, tzinfo=tzutc()),
            end_time=datetime.datetime(2021, 10, 2, tzinfo=tzutc()),
        )

