# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.data.tables import TableServiceClient
from _shared.testcase import TableTestCase
from preparers import tables_decorator

# --Test Class -----------------------------------------------------------------
class TestTableServiceStats(AzureRecordedTestCase, TableTestCase):
    # --Test cases per service ---------------------------------------
    @tables_decorator
    @recorded_by_proxy
    def test_table_service_stats_f(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

        # Act
        stats = tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        # Assert
        self._assert_stats_default(stats)

    @tables_decorator
    @recorded_by_proxy
    def test_table_service_stats_when_unavailable(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

        # Act
        stats = tsc.get_service_stats(
            raw_response_hook=self.override_response_body_with_unavailable_status)

        # Assert
        self._assert_stats_unavailable(stats)
