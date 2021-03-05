# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
from dateutil.tz import tzutc
import pytest
from base_testcase_aad import TestMetricsAdvisorAdministrationClientBase


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorAdministrationClientBase):

    def test_get_data_feed_ingestion_progress(self):

        ingestion = self.admin_client.get_data_feed_ingestion_progress(
            data_feed_id=self.data_feed_id
        )
        self.assertIsNotNone(ingestion.latest_success_timestamp)
        self.assertIsNotNone(ingestion.latest_active_timestamp)

    def test_list_data_feed_ingestion_status(self):

        ingestions = self.admin_client.list_data_feed_ingestion_status(
            data_feed_id=self.data_feed_id,
            start_time=datetime.datetime(2020, 8, 9, tzinfo=tzutc()),
            end_time=datetime.datetime(2020, 9, 16, tzinfo=tzutc()),
        )
        assert len(list(ingestions)) > 0

    def test_list_data_feed_ingestion_status_with_skip(self):

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
        ingestions_list = list(ingestions)
        ingestions_with_skips_list = list(ingestions_with_skips)
        assert len(ingestions_list) == len(ingestions_with_skips_list) + 5

    def test_refresh_data_feed_ingestion(self):
        self.admin_client.refresh_data_feed_ingestion(
            self.data_feed_id,
            start_time=datetime.datetime(2020, 10, 1, tzinfo=tzutc()),
            end_time=datetime.datetime(2020, 10, 2, tzinfo=tzutc()),
        )

