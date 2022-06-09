# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import SLEEP_DELAY
from async_preparers import cosmos_decorator_async

TEST_TABLE_PREFIX = 'pytableasync'

# ------------------------------------------------------------------------------

class TestTableCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_create_table(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_name = self._get_table_reference()

        # Act
        table = ts.get_table_client(table_name)
        created = await table.create_table()

        # Assert
        assert created.name == table_name

        await ts.delete_table(table_name=table_name)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_create_table_fail_on_exist(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with pytest.raises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        # Assert
        assert created
        await ts.delete_table(table_name=table_name)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_query_tables_per_page(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)

        table_name = "myasynctable"

        for i in range(5):
            await ts.create_table(table_name + str(i))

        query_filter = "TableName eq 'myasynctable0' or TableName eq 'myasynctable1' or TableName eq 'myasynctable2'"
        table_count = 0
        page_count = 0
        async for table_page in ts.query_tables(query_filter, results_per_page=2).by_page():

            temp_count = 0
            async for table in table_page:
                temp_count += 1
            assert temp_count <= 2
            page_count += 1
            table_count += temp_count

        assert page_count == 2
        assert table_count == 3

        await self._delete_all_tables(tables_cosmos_account_name, tables_primary_cosmos_account_key)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table = await self._create_table(ts)

        # Act
        tables = []
        async for t in ts.list_tables():
            tables.append(t)

        # Assert
        assert tables is not None
        assert len(tables) >=  1
        assert tables[0] is not None

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_query_tables_with_filter(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table = await self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = []
        async for t in ts.query_tables(name_filter):
            tables.append(t)

        # Assert
        assert tables is not None
        assert len(tables) ==  1
        await ts.delete_table(table.table_name)

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables_with_num_results(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        await self._delete_all_tables(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        prefix = 'listtable'
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_list = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_list)

        # Act
        all_tables = 0
        async for t in ts.list_tables():
            all_tables += 1

        small_page = 0
        async for page in ts.list_tables(results_per_page=3).by_page():
            page_size = 0
            async for table in page:
                page_size += 1
            assert page_size <= 3
            small_page += 1

        assert small_page == 2
        assert all_tables == 4

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables_with_marker(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        prefix = 'listtable'
        table_names = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_names)

        # Act
        generator1 = ts.list_tables(results_per_page=2).by_page()
        await generator1.__anext__()

        generator2 = ts.list_tables(results_per_page=2).by_page(
            continuation_token=generator1.continuation_token)
        await generator2.__anext__()

        tables1 = generator1._current_page
        tables2 = generator2._current_page

        tables1_len = 0
        async for _ in tables1:
            tables1_len += 1
        tables2_len = 0
        async for _ in tables2:
            tables2_len += 1

        # Assert
        assert tables1_len ==  2
        assert tables2_len ==  2
        assert tables1 != tables2

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_delete_table_with_existing_table(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table = await self._create_table(ts)

        # Act
        deleted = await ts.delete_table(table_name=table.table_name)

        # Assert
        assert deleted is None

    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_delete_table_with_non_existing_table_fail_not_exist(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_name = self._get_table_reference()
        await ts.delete_table(table_name)
        
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_create_table_underscore_name(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_name = "my_table"

        client = await ts.create_table(table_name)
        assert client.table_name == table_name
        
        await ts.delete_table(table_name)
        
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_create_table_unicode_name(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        # Arrange
        ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        table_name = u'啊齄丂狛狜'

        client = await ts.create_table(table_name)
        assert client.table_name == table_name
        
        await ts.delete_table(table_name)
