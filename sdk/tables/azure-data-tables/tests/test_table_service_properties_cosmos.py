# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureTestCase

from azure.core.exceptions import HttpResponseError

from azure.data.tables import (
    TableServiceClient,
    Metrics,
    RetentionPolicy,
    CorsRule
)

from _shared.testcase import TableTestCase, SLEEP_DELAY
from preparers import cosmos_decorator
# ------------------------------------------------------------------------------

class TableServicePropertiesTest(AzureTestCase, TableTestCase):
    @cosmos_decorator
    def test_too_many_cors_rules(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(CorsRule(['www.xyz.com'], ['GET']))

        with pytest.raises(HttpResponseError):
            tsc.set_service_properties(None, None, None, cors)

    @cosmos_decorator
    def test_retention_too_long(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=366))

        with pytest.raises(HttpResponseError):
            tsc.set_service_properties(None, None, minute_metrics)


class TestTableUnitTest(TableTestCase):

    def test_retention_no_days(self):
        # Assert
        pytest.raises(ValueError, RetentionPolicy, True, None)
