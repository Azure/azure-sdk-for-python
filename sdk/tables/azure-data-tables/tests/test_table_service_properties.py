# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import time
import pytest
from azure.data.tables._models import TableAnalyticsLogging, Metrics, RetentionPolicy, CorsRule

from msrest.exceptions import ValidationError  # TODO This should be an azure-core error.
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from azure.core.exceptions import HttpResponseError

from azure.data.tables import TableServiceClient

from _shared.testcase import GlobalStorageAccountPreparer, TableTestCase

# ------------------------------------------------------------------------------


class TableServicePropertiesTest(TableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_properties_default(self, prop):
        self.assertIsNotNone(prop)

        self._assert_logging_equal(prop['analytics_logging'], TableAnalyticsLogging())
        self._assert_metrics_equal(prop['hour_metrics'], Metrics())
        self._assert_metrics_equal(prop['minute_metrics'], Metrics())
        self._assert_cors_equal(prop['cors'], list())

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            self.assertEqual(log1, log2)
            return

        self.assertEqual(log1.version, log2.version)
        self.assertEqual(log1.read, log2.read)
        self.assertEqual(log1.write, log2.write)
        self.assertEqual(log1.delete, log2.delete)
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            self.assertEqual(policy1, policy2)
            return

        self.assertEqual(policy1.enabled, policy2.enabled)
        self.assertEqual(policy1.days, policy2.days)

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            self.assertEqual(prop1, prop2)
            return

        self.assertEqual(prop1.enabled, prop2.enabled)
        self.assertEqual(prop1.index_document, prop2.index_document)
        self.assertEqual(prop1.error_document404_path, prop2.error_document404_path)

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            self.assertNotEqual(policy1, policy2)
            return

        self.assertFalse(policy1.enabled == policy2.enabled
                         and policy1.days == policy2.days)

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            self.assertEqual(metrics1, metrics2)
            return

        self.assertEqual(metrics1.version, metrics2.version)
        self.assertEqual(metrics1.enabled, metrics2.enabled)
        self.assertEqual(metrics1.include_apis, metrics2.include_apis)
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            self.assertEqual(cors1, cors2)
            return

        self.assertEqual(len(cors1), len(cors2))

        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            self.assertEqual(len(rule1.allowed_origins), len(rule2.allowed_origins))
            self.assertEqual(len(rule1.allowed_methods), len(rule2.allowed_methods))
            self.assertEqual(rule1.max_age_in_seconds, rule2.max_age_in_seconds)
            self.assertEqual(len(rule1.exposed_headers), len(rule2.exposed_headers))
            self.assertEqual(len(rule1.allowed_headers), len(rule2.allowed_headers))

    def _assert_retention_equal(self, ret1, ret2):
        self.assertEqual(ret1.enabled, ret2.enabled)
        self.assertEqual(ret1.days, ret2.days)

    # --Test cases per service ---------------------------------------
    @GlobalStorageAccountPreparer()
    def test_table_service_properties(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support service properties")
        tsc = TableServiceClient(url, storage_account_key)
        # Act
        resp = tsc.set_service_properties(
            analytics_logging=TableAnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list())

        # Assert
        self.assertIsNone(resp)
        if self.is_live:
            time.sleep(30)
        self._assert_properties_default(tsc.get_service_properties())


    # --Test cases per feature ---------------------------------------
    @GlobalStorageAccountPreparer()
    def test_set_logging(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support service properties")
        tsc = TableServiceClient(url, storage_account_key)
        logging = TableAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(analytics_logging=logging)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = tsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @GlobalStorageAccountPreparer()
    def test_set_hour_metrics(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support service properties")
        tsc = TableServiceClient(url, storage_account_key)
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = tsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @GlobalStorageAccountPreparer()
    def test_set_minute_metrics(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support service properties")
        tsc = TableServiceClient(url, storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        tsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = tsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @GlobalStorageAccountPreparer()
    def test_set_cors(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support service properties")
        tsc = TableServiceClient(url, storage_account_key)
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
        tsc.set_service_properties(cors=cors)

        # Assert
        if self.is_live:
            time.sleep(30)
        received_props = tsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    # --Test cases for errors ---------------------------------------
    @GlobalStorageAccountPreparer()
    def test_retention_no_days(self, resource_group, location, storage_account, storage_account_key):
        # Assert
        self.assertRaises(ValueError,
                          RetentionPolicy,
                          True, None)

    @GlobalStorageAccountPreparer()
    def test_too_many_cors_rules(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        # Assert
        self.assertRaises(HttpResponseError,
                          tsc.set_service_properties, None, None, None, cors)

    @GlobalStorageAccountPreparer()
    def test_retention_too_long(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=366))

        # Assert
        self.assertRaises(HttpResponseError,
                          tsc.set_service_properties,
                          None, None, minute_metrics)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
