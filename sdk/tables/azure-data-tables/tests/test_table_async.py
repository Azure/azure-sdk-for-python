import locale
import os
import sys
from datetime import datetime, timedelta

import pytest

from devtools_testutils import AzureTestCase

from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.data.tables import (
    AccessPolicy,
    TableSasPermissions,
    ResourceTypes,
    AccountSasPermissions,
    TableItem,
    generate_account_sas
)
from azure.data.tables.aio import TableServiceClient, TableClient

from _shared.asynctestcase import AsyncTableTestCase
from preparers import TablesPreparer

TEST_TABLE_PREFIX = 'pytableasync'


# ------------------------------------------------------------------------------

class TableTestAsync(AzureTestCase, AsyncTableTestCase):
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
            table = ts.get_table_client(table_name)
        return table

    async def _delete_table(self, ts, table):
        if table is None:
            return
        try:
            await ts.delete_table(table.table_name)
        except ResourceNotFoundError:
            pass

    # --Test cases for tables --------------------------------------------------
    @TablesPreparer()
    async def test_create_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)

        # Assert
        assert created.table_name == table_name
        await ts.delete_table(table_name=table_name)

    @TablesPreparer()
    async def test_create_table_fail_on_exist(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with pytest.raises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        name_filter = "TableName eq '{}'".format(table_name)
        existing = ts.query_tables(filter=name_filter)

        # Assert
        assert isinstance(created,  TableClient)
        await ts.delete_table(table_name=table_name)

    @TablesPreparer()
    async def test_query_tables_per_page(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table_name = "myasynctable"

        for i in range(5):
            await ts.create_table(table_name + str(i))

        query_filter = "TableName eq 'myasynctable0' or TableName eq 'myasynctable1' or TableName eq 'myasynctable2'"
        table_count = 0
        page_count = 0
        async for table_page in ts.query_tables(filter=query_filter, results_per_page=2).by_page():

            temp_count = 0
            async for table in table_page:
                temp_count += 1
            assert temp_count <= 2
            page_count += 1
            table_count += temp_count

        assert page_count == 2
        assert table_count == 3

        for i in range(5):
            await ts.delete_table(table_name + str(i))

    @TablesPreparer()
    async def test_list_tables(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = await self._create_table(ts)

        # Act
        tables = []
        async for t in ts.list_tables():
            tables.append(t)

        # Assert
        for table_item in tables:
            assert isinstance(table_item,  TableItem)

        assert tables is not None
        assert len(tables) >=  1
        assert tables[0] is not None
        await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_query_tables_with_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = await self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = []
        async for t in ts.query_tables(filter=name_filter):
            tables.append(t)

        # Assert
        assert tables is not None
        assert len(tables) ==  1
        for table_item in tables:
            assert isinstance(table_item,  TableItem)
            assert table_item.date is not None
            assert table_item.table_name is not None
        await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_list_tables_with_num_results(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        prefix = 'listtable'
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        # Delete any existing tables
        async for table in ts.list_tables():
            await ts.delete_table(table.table_name)

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

        assert len(small_page) ==  2
        assert len(big_page) >=  4

    @TablesPreparer()
    async def test_list_tables_with_marker(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
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
        assert tables1_len == 2
        assert tables2_len == 2
        assert tables1 != tables2

    @TablesPreparer()
    async def test_delete_table_with_existing_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = await self._create_table(ts)

        # Act
        await ts.delete_table(table_name=table.table_name)

        existing = ts.query_tables("TableName eq '{}'".format(table.table_name))
        tables = []
        async for e in existing:
            tables.append(e)
        assert tables ==  []

    @TablesPreparer()
    async def test_delete_table_with_non_existing_table_fail_not_exist(self, tables_storage_account_name,
                                                                       tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table_name = self._get_table_reference()

        # Act
        with pytest.raises(ResourceNotFoundError):
            await ts.delete_table(table_name)

        # Assert

    @TablesPreparer()
    async def test_get_table_acl(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = await self._create_table(ts)
        try:
            # Act
            acl = await table.get_table_access_policy()

            # Assert
            assert acl is not None
            assert len(acl) ==  0
        finally:
            await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_set_table_acl_with_empty_signed_identifiers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={})

            # Assert
            acl = await table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  0
        finally:
            await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_set_table_acl_with_empty_signed_identifier(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, tables_primary_storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={'empty': None})
            # Assert
            acl = await table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  1
            assert acl['empty'] is not None
            assert acl['empty'].permission is None
            assert acl['empty'].expiry is None
            assert acl['empty'].start is None
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_set_table_acl_with_signed_identifiers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, tables_primary_storage_account_key)
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
            assert acl is not None
            assert len(acl) ==  1
            assert 'testid' in acl
        finally:
            await ts.delete_table(table.table_name)

    @TablesPreparer()
    async def test_set_table_acl_too_many_ids(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, tables_primary_storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with pytest.raises(ValueError):
                await table.set_table_access_policy(table_name=table.table_name, signed_identifiers=identifiers)
        finally:
            await ts.delete_table(table.table_name)

    @pytest.mark.live_test_only
    @TablesPreparer()
    async def test_account_sas(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)

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
                tables_storage_account_name,
                tables_primary_storage_account_key,
                resource_types=ResourceTypes(object=True),
                permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            account_url = self.account_url(tables_storage_account_name, "table")

            service = self.create_client_from_credential(TableServiceClient, token, account_url=account_url)

            # Act
            sas_table = service.get_table_client(table.table_name)
            entities = []
            async for e in sas_table.list_entities():
                entities.append(e)

            # Assert
            assert len(entities) ==  2
            assert entities[0].text == u'hello'
            assert entities[1].text == u'hello'
        finally:
            await self._delete_table(table=table, ts=tsc)

    @pytest.mark.skip("Test fails on Linux and in Python2. Throws a locale.Error: unsupported locale setting")
    @TablesPreparer()
    async def test_locale(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = self.create_client_from_credential(TableServiceClient, tables_primary_storage_account_key, account_url=account_url)
        table = (self._get_table_reference())
        init_locale = locale.getlocale()
        if os.name == "nt":
            culture = "Spanish_Spain"
        elif os.name == 'posix':
            culture = 'es_ES.UTF-8'
        else:
            culture = 'es_ES.utf8'

        locale.setlocale(locale.LC_ALL, culture)
        e = None

        # Act
        await ts.create_table(table)

        resp = ts.list_tables()

        e = sys.exc_info()[0]

        # Assert
        assert e is None

        await ts.delete_table(table)
        locale.setlocale(locale.LC_ALL, init_locale[0] or 'en_US')


class TestTablesUnitTest(AsyncTableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA"

    @pytest.mark.asyncio
    async def test_unicode_create_table_unicode_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)

        table_name = u'啊齄丂狛狜'

        # Act
        with pytest.raises(ValueError) as excinfo:
            await tsc.create_table(table_name)

            assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)

    @pytest.mark.asyncio
    async def test_create_table_invalid_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await tsc.create_table(table_name=invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    @pytest.mark.asyncio
    async def test_delete_table_invalid_name(self):
        # Arrange
        account_url = self.account_url(self.tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=self.tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await tsc.create_table(invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)
