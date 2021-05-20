# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import pytest

from devtools_testutils import AzureRecordedTestCase

from azure.core.exceptions import HttpResponseError

from azure.data.tables import TableAnalyticsLogging, Metrics, RetentionPolicy, CorsRule
from azure.data.tables.aio import TableServiceClient

from _shared.testcase import TableTestCase
from async_preparers import tables_decorator_async

# ------------------------------------------------------------------------------


class TestTableServiceProperties(AzureRecordedTestCase, TableTestCase):
    @tables_decorator_async
    async def test_table_service_properties_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, tables_primary_storage_account_key, logging_enable=True)
        # Act
        resp = await tsc.set_service_properties(
            analytics_logging=TableAnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list())

        # Assert
        assert resp is None
        if self.is_live:
            time.sleep(30)
        self._assert_properties_default(await tsc.get_service_properties())

    # --Test cases per feature ---------------------------------------
    @tables_decorator_async
    async def test_set_logging_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, tables_primary_storage_account_key)
        logging = TableAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(analytics_logging=logging)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = await tsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @tables_decorator_async
    async def test_set_hour_metrics_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, tables_primary_storage_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = await tsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @tables_decorator_async
    async def test_set_minute_metrics_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, tables_primary_storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = await tsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @tables_decorator_async
    async def test_set_cors_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, tables_primary_storage_account_key)
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Act
        await tsc.set_service_properties(cors=cors)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = await tsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    # --Test cases for errors ---------------------------------------
    @tables_decorator_async
    async def test_too_many_cors_rules_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), tables_primary_storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(None, None, None, cors)

    @tables_decorator_async
    async def test_retention_too_long_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), tables_primary_storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=366))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(None, None, minute_metrics)


class TestTableUnit(TableTestCase):

    @pytest.mark.asyncio
    async def test_retention_no_days_async(self):
        # Assert
        pytest.raises(ValueError,
                          RetentionPolicy,
                          True, None)