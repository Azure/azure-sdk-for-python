# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from uuid import uuid4, UUID
from numpy import int64

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import tables_decorator
from azure.data.tables import TableServiceClient, TableEntityEncoder

from _shared.testcase import TableTestCase


class MyKeysEncoder(TableEntityEncoder):
    def prepare_key(self, key):
        """Custom key preparer to support UUID or int key for delete/get"""
        if isinstance(key, UUID) or isinstance(key, int):
            key = str(key)
        return super().prepare_key(key)


class TestEncoder(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_encode_keys(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        with TableServiceClient(
            self.account_url(tables_storage_account_name, "table"),
            credential=tables_primary_storage_account_key,
            table_name=table_name
        ) as ts:
            table = ts.get_table_client(table_name)
            table.create_table()

            # Act
            entity = {
                "PartitionKey": uuid4(),
                "PartitionKey@odata.type": "Edm.Guid",
                "RowKey": 0,
                "RowKey@odata.type": "Edm.Int32",
            }

            table.create_entity(entity, encoder=MyKeysEncoder())
            table.delete_entity(entity, encoder=MyKeysEncoder())
            table.delete_table()
