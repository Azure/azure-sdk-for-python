import locale
import os
import sys
from datetime import datetime, timedelta

import pytest
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError, HttpResponseError
from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import GlobalStorageAccountPreparer
from azure.data.tables import (
    AccessPolicy,
    TableAnalyticsLogging,
    Metrics,
    TableSasPermissions,
    ResourceTypes,
    RetentionPolicy,
    AccountSasPermissions,
    TableItem
)
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables._generated.models import QueryOptions
from azure.data.tables._table_shared_access_signature import generate_account_sas

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
    @GlobalStorageAccountPreparer()
    async def test_create_properties(self, resource_group, location, storage_account, storage_account_key):
        # # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()
        # Act
        created = await ts.create_table(table_name)

        # Assert
        assert created.table_name == table_name

        properties = await  ts.get_service_properties()
        await ts.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
        # have to wait for return to service
        p = await ts.get_service_properties()
        # have to wait for return to service
        await ts.set_service_properties(minute_metrics= Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5)))

        ps = await ts.get_service_properties()
        await ts.delete_table(table_name)

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

    @GlobalStorageAccountPreparer()
    async def test_create_table_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with self.assertRaises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        name_filter = "TableName eq '{}'".format(table_name)
        existing = ts.query_tables(filter=name_filter)

        # Assert
        self.assertIsInstance(created, TableClient)
        # self.assertEqual(len(existing), 1)
        # TODO: the AsyncItemPaged does not have a length property, and cannot be used as an iterator
        await ts.delete_table(table_name=table_name)

    @GlobalStorageAccountPreparer()
    async def test_create_table_if_exists(self, resource_group, location, storage_account, storage_account_key):
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        t0 = await ts.create_table(table_name)
        t1 = await ts.create_table_if_not_exists(table_name)

        self.assertIsNotNone(t0)
        self.assertIsNotNone(t1)
        self.assertEqual(t0.table_name, t1.table_name)
        await ts.delete_table(table_name)

    @GlobalStorageAccountPreparer()
    async def test_create_table_if_exists_new_table(self, resource_group, location, storage_account, storage_account_key):
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        t = await ts.create_table_if_not_exists(table_name)

        self.assertIsNotNone(t)
        self.assertEqual(t.table_name, table_name)
        await ts.delete_table(table_name)

    @GlobalStorageAccountPreparer()
    async def test_create_table_invalid_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await ts.create_table(table_name=invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    @GlobalStorageAccountPreparer()
    async def test_delete_table_invalid_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await ts.create_table(invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

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
        for table_item in tables:
            self.assertIsInstance(table_item, TableItem)

        self.assertIsNotNone(tables)
        self.assertGreaterEqual(len(tables), 1)
        self.assertIsNotNone(tables[0])
        await ts.delete_table(table.table_name)

    @GlobalStorageAccountPreparer()
    async def test_query_tables_with_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = []
        async for t in ts.query_tables(filter=name_filter):
            tables.append(t)

        # Assert
        self.assertIsNotNone(tables)
        self.assertEqual(len(tables), 1)
        for table_item in tables:
            self.assertIsInstance(table_item, TableItem)
            self.assertIsNotNone(table_item.date)
            self.assertIsNotNone(table_item.table_name)
        await ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    # TODO: TablePropertiesPaged is not an iterator, should inherit from AsyncPageIterator
    @GlobalStorageAccountPreparer()
    async def test_query_tables_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        prefix = 'listtable'
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_list = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_list)

        # Act
        small_page = []
        big_page = []
        for s in next(ts.list_tables(results_per_page=3).by_page()):
            small_page.append(s)
        for t in next(ts.list_tables().by_page()):
            big_page.append(t)

        # Assert
        self.assertEqual(len(small_page), 3)
        self.assertGreaterEqual(len(big_page), 4)

    @GlobalStorageAccountPreparer()
    async def test_list_tables_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        prefix = 'listtable'
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_list = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_list)

        # Act
        big_page = []
        async for t in ts.list_tables():
            big_page.append(t)

        small_page = []
        async for s in ts.list_tables(results_per_page=3).by_page():
            small_page.append(s)

        self.assertEqual(len(small_page), 2)
        self.assertGreaterEqual(len(big_page), 4)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_list_tables_with_marker(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
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
        self.assertEqual(tables1_len, 2)
        self.assertEqual(tables2_len, 2)
        self.assertNotEqual(tables1, tables2)

    @GlobalStorageAccountPreparer()
    async def test_delete_table_with_existing_table(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        await ts.delete_table(table_name=table.table_name)

        existing = ts.query_tables("TableName eq '{}'".format(table.table_name))
        tables = []
        async for e in existing:
            tables.append(e)
        self.assertEqual(tables, [])

    @GlobalStorageAccountPreparer()
    async def test_delete_table_with_non_existing_table_fail_not_exist(self, resource_group, location, storage_account,
                                                                       storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await ts.delete_table(table_name)

    @GlobalStorageAccountPreparer()
    async def test_unicode_create_table_unicode_name(self, resource_group, location, storage_account,
                                                     storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos URLs do notsupport unicode table names")
        ts = TableServiceClient(url, storage_account_key)
        table_name = u'啊齄丂狛狜'

        # Act
        with self.assertRaises(ValueError) as excinfo:
            await ts.create_table(table_name)

            assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)

    @GlobalStorageAccountPreparer()
    async def test_get_table_acl(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            acl = await table.get_table_access_policy()

            # Assert
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            await ts.delete_table(table.table_name)

    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={})

            # Assert
            acl = await table.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_none_signed_identifier(self, resource_group, location, storage_account,
                                                              storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={'empty': None})
            # Assert
            acl = await table.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertIsNotNone(acl['empty'])
            self.assertIsNone(acl['empty'].permission)
            self.assertIsNone(acl['empty'].expiry)
            self.assertIsNone(acl['empty'].start)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_signed_identifiers(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        client = ts.get_table_client(table_name=table.table_name)

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(start=datetime.utcnow() - timedelta(minutes=5),
                                             expiry=datetime.utcnow() + timedelta(hours=1),
                                             permission=TableSasPermissions(read=True))
        try:
            await client.set_table_access_policy(signed_identifiers=identifiers)
            # Assert
            acl = await  client.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertTrue('testid' in acl)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with self.assertRaises(ValueError):
                await table.set_table_access_policy(table_name=table.table_name, signed_identifiers=identifiers)
        finally:
            await ts.delete_table(table.table_name)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        tsc = TableServiceClient(url, storage_account_key)
        table = await self._create_table(tsc)
        try:
            entity = {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'text': 'hello',
            }
            await table.upsert_entity(entity=entity)

            entity['RowKey'] = 'test2'
            await table.upsert_entity(entity=entity)

            token = generate_account_sas(
                storage_account.name,
                storage_account_key,
                resource_types=ResourceTypes(object=True),
                permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            sas_table = service.get_table_client(table.table_name)
            entities = []
            async for e in sas_table.list_entities():
                entities.append(e)

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].text.value, 'hello')
            self.assertEqual(entities[1].text.value, 'hello')
        finally:
            await self._delete_table(table=table, ts=tsc)

    @pytest.mark.skip("msrest fails deserialization: https://github.com/Azure/msrest-for-python/issues/192")
    @GlobalStorageAccountPreparer()
    async def test_locale(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = (self._get_table_reference())
        init_locale = locale.getlocale()
        if os.name == "nt":
            culture = "Spanish_Spain"
        elif os.name == 'posix':
            culture = 'es_ES.UTF-8'
        else:
            culture = 'es_ES.utf8'

        try:
            locale.setlocale(locale.LC_ALL, culture)
            e = None

            # Act
            await table.create_table()
            try:
                resp = ts.list_tables()
            except:
                e = sys.exc_info()[0]

            # Assert
            self.assertIsNone(e)
        finally:
            await ts.delete_table(table.table_name)
            locale.setlocale(locale.LC_ALL, init_locale[0] or 'en_US')
