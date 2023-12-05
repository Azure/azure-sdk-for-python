# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core.exceptions import HttpResponseError

from azure.data.tables import (
    TableAnalyticsLogging,
    TableServiceClient,
    TableMetrics,
    TableRetentionPolicy,
    TableCorsRule,
)

from _shared.testcase import TableTestCase
from preparers import cosmos_decorator

# ------------------------------------------------------------------------------


class TestTableServicePropertiesCosmos(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_too_many_cors_rules(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        cors = []
        for i in range(0, 6):
            cors.append(TableCorsRule(["www.xyz.com"], ["GET"]))

        with pytest.raises(HttpResponseError):
            tsc.set_service_properties(cors=cors)

    @cosmos_decorator
    @recorded_by_proxy
    def test_retention_too_long(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        minute_metrics = TableMetrics(
            enabled=True, include_apis=True, retention_policy=TableRetentionPolicy(enabled=True, days=366)
        )

        with pytest.raises(HttpResponseError):
            tsc.set_service_properties(minute_metrics=minute_metrics)

    @cosmos_decorator
    @recorded_by_proxy
    def test_client_with_url_ends_with_table_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "table")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        tsc = TableServiceClient(invalid_url, credential=tables_primary_cosmos_account_key)

        with pytest.raises(HttpResponseError) as exc:
            tsc.create_table(table_name)
        assert ("Server failed to authenticate the request") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        with pytest.raises(HttpResponseError) as exc:
            tsc.create_table_if_not_exists(table_name)
        assert ("Server failed to authenticate the request") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        with pytest.raises(HttpResponseError) as exc:
            tsc.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
        assert ("Server failed to authenticate the request") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        with pytest.raises(HttpResponseError) as exc:
            tsc.get_service_properties()
        assert ("Server failed to authenticate the request") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        with pytest.raises(HttpResponseError) as exc:
            tsc.delete_table(table_name)
        assert ("Server failed to authenticate the request") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)


class TestTableUnitTest(TableTestCase):
    def test_retention_no_days(self):
        # Assert
        pytest.raises(ValueError, TableRetentionPolicy, enabled=True)
