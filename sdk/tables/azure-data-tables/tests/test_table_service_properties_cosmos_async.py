# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from time import sleep

from devtools_testutils import AzureTestCase

from azure.data.tables import TableAnalyticsLogging, Metrics, RetentionPolicy, CorsRule
from azure.data.tables.aio import TableServiceClient
from azure.core.exceptions import HttpResponseError

from _shared.testcase import SLEEP_DELAY
from _shared.asynctestcase import AsyncTableTestCase
from preparers import CosmosPreparer
# ------------------------------------------------------------------------------

class TableServicePropertiesTest(AzureTestCase, AsyncTableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_properties_default(self, prop):
        assert prop is not None

        self._assert_logging_equal(prop['analytics_logging'], TableAnalyticsLogging())
        self._assert_metrics_equal(prop['hour_metrics'], Metrics())
        self._assert_metrics_equal(prop['minute_metrics'], Metrics())
        self._assert_cors_equal(prop['cors'], list())

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            assert log1 ==  log2
            return

        assert log1.version ==  log2.version
        assert log1.read ==  log2.read
        assert log1.write ==  log2.write
        assert log1.delete ==  log2.delete
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 ==  policy2
            return

        assert policy1.enabled ==  policy2.enabled
        assert policy1.days ==  policy2.days

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            assert prop1 ==  prop2
            return

        assert prop1.enabled ==  prop2.enabled
        assert prop1.index_document ==  prop2.index_document
        assert prop1.error_document404_path ==  prop2.error_document404_path

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 != policy2
            return

        assert not (policy1.enabled == policy2.enabled) and (policy1.days == policy2.days)

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            assert metrics1 ==  metrics2
            return

        assert metrics1.version ==  metrics2.version
        assert metrics1.enabled ==  metrics2.enabled
        assert metrics1.include_apis ==  metrics2.include_apis
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            assert cors1 ==  cors2
            return

        assert len(cors1) ==  len(cors2)

        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            assert len(rule1.allowed_origins) ==  len(rule2.allowed_origins)
            assert len(rule1.allowed_methods) ==  len(rule2.allowed_methods)
            assert rule1.max_age_in_seconds ==  rule2.max_age_in_seconds
            assert len(rule1.exposed_headers) ==  len(rule2.exposed_headers)
            assert len(rule1.allowed_headers) ==  len(rule2.allowed_headers)

    def _assert_retention_equal(self, ret1, ret2):
        assert ret1.enabled ==  ret2.enabled
        assert ret1.days ==  ret2.days

    # --Test cases per service ---------------------------------------
    @pytest.mark.skip("Cosmos Tables does not yet support service properties")
    @CosmosPreparer()
    async def test_table_service_properties_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        tsc = TableServiceClient(url, tables_primary_cosmos_account_key, logging_enable=True)
        # Act
        resp = await tsc.set_service_properties(
            analytics_logging=TableAnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list())

        # Assert
        assert resp is None
        self._assert_properties_default(await tsc.get_service_properties())
        if self.is_live:
            sleep(SLEEP_DELAY)

    # --Test cases per feature ---------------------------------------
    @pytest.mark.skip("Cosmos Tables does not yet support service properties")
    @CosmosPreparer()
    async def test_set_logging_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        tsc = TableServiceClient(url, tables_primary_cosmos_account_key)
        logging = TableAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(analytics_logging=logging)

        # Assert
        received_props = await tsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support service properties")
    @CosmosPreparer()
    async def test_set_hour_metrics_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        tsc = TableServiceClient(url, tables_primary_cosmos_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = await tsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support service properties")
    @CosmosPreparer()
    async def test_set_minute_metrics_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        tsc = TableServiceClient(url, tables_primary_cosmos_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        await tsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = await tsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support service properties")
    @CosmosPreparer()
    async def test_set_cors_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        tsc = TableServiceClient(url, tables_primary_cosmos_account_key)
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
        received_props = await tsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)
        if self.is_live:
            sleep(SLEEP_DELAY)

    # --Test cases for errors ---------------------------------------
    @CosmosPreparer()
    async def test_too_many_cors_rules_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(None, None, None, cors)
        if self.is_live:
            sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_retention_too_long_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=366))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(None, None, minute_metrics)
        if self.is_live:
            sleep(SLEEP_DELAY)


class TestTableUnitTest(AsyncTableTestCase):

    @pytest.mark.asyncio
    async def test_retention_no_days_async(self):
        # Assert
        pytest.raises(ValueError, RetentionPolicy, True, None)
