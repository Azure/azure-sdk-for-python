# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.data.tables import (
    TableServiceClient,
    TableAnalyticsLogging,
    TableMetrics,
    TableRetentionPolicy,
    TableCorsRule
)
from azure.core.exceptions import HttpResponseError

from _shared.testcase import TableTestCase
from preparers import tables_decorator

# ------------------------------------------------------------------------------


class TestTableServiceProperties(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_table_service_properties(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, credential=tables_primary_storage_account_key)
        # Act
        resp = tsc.set_service_properties(
            analytics_logging=TableAnalyticsLogging(),
            hour_metrics=TableMetrics(),
            minute_metrics=TableMetrics(),
            cors=list())

        # Assert
        assert resp is None
        if self.is_live:
            time.sleep(45)
        self._assert_properties_default(tsc.get_service_properties())

    # --Test cases per feature ---------------------------------------
    @tables_decorator
    @recorded_by_proxy
    def test_set_logging(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, credential=tables_primary_storage_account_key)
        logging = TableAnalyticsLogging(read=True, write=True, delete=True, retention_policy=TableRetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(analytics_logging=logging)

        # Assert
        if self.is_live:
            time.sleep(45)
        received_props = tsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @tables_decorator
    @recorded_by_proxy
    def test_set_hour_metrics(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, credential=tables_primary_storage_account_key)
        hour_metrics = TableMetrics(enabled=True, include_apis=True, retention_policy=TableRetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        if self.is_live:
            time.sleep(45)
        received_props = tsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @tables_decorator
    @recorded_by_proxy
    def test_set_minute_metrics(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, credential=tables_primary_storage_account_key)
        minute_metrics = TableMetrics(enabled=True, include_apis=True,
                                 retention_policy=TableRetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        if self.is_live:
            time.sleep(45)
        received_props = tsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @tables_decorator
    @recorded_by_proxy
    def test_set_cors(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(url, credential=tables_primary_storage_account_key)
        cors_rule1 = TableCorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = TableCorsRule(allowed_origins, allowed_methods)
        cors_rule2.max_age_in_seconds = max_age_in_seconds
        cors_rule2.exposed_headers = exposed_headers
        cors_rule2.allowed_headers = allowed_headers

        cors = [cors_rule1, cors_rule2]

        # Act
        tsc.set_service_properties(cors=cors)

        # Assert
        if self.is_live:
            time.sleep(45)
        received_props = tsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    # --Test cases for errors ---------------------------------------
    @tables_decorator
    @recorded_by_proxy
    def test_too_many_cors_rules(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(TableCorsRule(['www.xyz.com'], ['GET']))

        # Assert
        pytest.raises(HttpResponseError,
                          tsc.set_service_properties, cors=cors)

    @tables_decorator
    @recorded_by_proxy
    def test_retention_too_long(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)
        minute_metrics = TableMetrics(enabled=True, include_apis=True,
                                 retention_policy=TableRetentionPolicy(enabled=True, days=366))

        # Assert
        pytest.raises(HttpResponseError,
                          tsc.set_service_properties,
                          minute_metrics=minute_metrics)


class TestTableUnitTest(TableTestCase):
    def test_retention_no_days(self):
        # Assert
        pytest.raises(ValueError, TableRetentionPolicy, enabled=True)
