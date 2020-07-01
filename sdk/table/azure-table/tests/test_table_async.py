from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import GlobalStorageAccountPreparer
from azure.table._generated.aio import TableServiceClient

TEST_TABLE_PREFIX = 'pytableasync'


# ------------------------------------------------------------------------------

class TableTestAsync(AsyncTableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    async def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = await ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = await ts.get_table_client(table_name)
        return table

    async def _delete_table(self, ts, table):
        if table is None:
            return
        try:
            await ts.delete_table(table.table_name)
        except ResourceNotFoundError:
            pass

    # --Test cases for tables --------------------------------------------------
    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_create_table(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)

        # Assert
        assert created.table_name == table_name

        await ts.delete_table(table_name=table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_create_table_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with self.assertRaises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        # Assert
        self.assertTrue(created)
        await ts.delete_table(table_name=table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_list_tables(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        tables = []
        async for t in ts.list_tables():
            tables.append(t)

        # Assert
        self.assertIsNotNone(tables)
        self.assertGreaterEqual(len(tables), 1)
        self.assertIsNotNone(tables[0])

        await ts.delete_table(table.table_name)
