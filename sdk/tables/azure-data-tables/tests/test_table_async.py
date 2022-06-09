# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta

import pytest

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ResourceExistsError
from azure.data.tables import (
    TableAccessPolicy,
    TableSasPermissions,
    ResourceTypes,
    AccountSasPermissions,
    TableItem,
    generate_account_sas
)
from azure.data.tables.aio import TableServiceClient, TableClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async


class TestTableAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_create_table(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table_name = self._get_table_reference()

        # Act
        table = ts.get_table_client(table_name)
        created = await table.create_table()

        # Assert
        assert created.name == table_name
        await ts.delete_table(table_name=table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_create_table_fail_on_exist(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with pytest.raises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        name_filter = "TableName eq '{}'".format(table_name)
        existing = ts.query_tables(name_filter)

        # Assert
        assert isinstance(created,  TableClient)
        await ts.delete_table(table_name=table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_tables_per_page(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

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

        for i in range(5):
            await ts.delete_table(table_name + str(i))

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_tables_with_filter(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table = await self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = []
        async for t in ts.query_tables(name_filter):
            tables.append(t)

        # Assert
        assert tables is not None
        assert len(tables) ==  1
        for table_item in tables:
            assert isinstance(table_item,  TableItem)
            assert table_item.name is not None
        await ts.delete_table(table.table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables_with_num_results(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        prefix = 'listtable'
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        # Delete any existing tables
        async for table in ts.list_tables():
            await ts.delete_table(table.name)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_list_tables_with_marker(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_table_with_existing_table(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table = await self._create_table(ts)

        # Act
        await ts.delete_table(table_name=table.table_name)

        existing = ts.query_tables("TableName eq '{}'".format(table.table_name))
        tables = []
        async for e in existing:
            tables.append(e)
        assert tables ==  []

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_table_with_non_existing_table_fail_not_exist(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()
        await ts.delete_table(table_name)

        # Assert

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_table_acl(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = await self._create_table(ts)
        try:
            # Act
            acl = await table.get_table_access_policy()

            # Assert
            assert acl is not None
            assert len(acl) ==  0
        finally:
            await ts.delete_table(table.table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_set_table_acl_with_empty_signed_identifiers(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_set_table_acl_with_empty_signed_identifier(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, credential=tables_primary_storage_account_key)
        table = await self._create_table(ts)
        try:
            dt = datetime(2021, 6, 8, 2, 10, 9)
            signed_identifiers={
                'null': None,
                'empty': TableAccessPolicy(start=None, expiry=None, permission=None),
                'partial': TableAccessPolicy(permission='r'),
                'full': TableAccessPolicy(start=dt, expiry=dt, permission='r')
                }
            await table.set_table_access_policy(signed_identifiers)
            acl = await table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  4
            assert acl['null'] is None
            assert acl['empty'] is None
            assert acl['partial'] is not None
            assert acl['partial'].permission == 'r'
            assert acl['partial'].expiry is None
            assert acl['partial'].start is None
            assert acl['full'] is not None
            assert acl['full'].permission == 'r'
            self._assert_policy_datetime(dt, acl['full'].expiry)
            self._assert_policy_datetime(dt, acl['full'].start)

            signed_identifiers.pop('empty')
            signed_identifiers['partial'] = None

            await table.set_table_access_policy(signed_identifiers)
            acl = await table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  3
            assert 'empty' not in acl
            assert acl['null'] is None
            assert acl['partial'] is None
            assert acl['full'] is not None
            assert acl['full'].permission == 'r'
            self._assert_policy_datetime(dt, acl['full'].expiry)
            self._assert_policy_datetime(dt, acl['full'].start)
        finally:
            await ts.delete_table(table.table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_set_table_acl_with_signed_identifiers(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, credential=tables_primary_storage_account_key)
        table = await self._create_table(ts)
        client = ts.get_table_client(table_name=table.table_name)

        # Act
        start = datetime(2021, 6, 8, 2, 10, 9) - timedelta(minutes=5)
        expiry = datetime(2021, 6, 8, 2, 10, 9) + timedelta(hours=1)
        identifiers = {'testid': TableAccessPolicy(start=start, expiry=expiry, permission=TableSasPermissions(read=True))}
        try:
            await client.set_table_access_policy(signed_identifiers=identifiers)

            # Assert
            acl = await  client.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  1
            assert acl.get('testid')
            self._assert_policy_datetime(start, acl['testid'].start)
            self._assert_policy_datetime(expiry, acl['testid'].expiry)
            assert acl['testid'].permission == 'r'
        finally:
            await ts.delete_table(table.table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_set_table_acl_too_many_ids(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(url, credential=tables_primary_storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with pytest.raises(ValueError):
                await table.set_table_access_policy(signed_identifiers=identifiers)
        finally:
            await ts.delete_table(table.table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_account_sas(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

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

            token = self.generate_sas(
                generate_account_sas,
                tables_primary_storage_account_key,
                resource_types=ResourceTypes(object=True),
                permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            token = AzureSasCredential(token)

            account_url = self.account_url(tables_storage_account_name, "table")
            service = TableServiceClient(credential=token, endpoint=account_url)

            # Act
            sas_table = service.get_table_client(table.table_name)
            entities = []
            async for e in sas_table.list_entities():
                entities.append(e)

            # Assert
            assert len(entities) ==  2
            assert entities[0]['text'] == u'hello'
            assert entities[1]['text'] == u'hello'
        finally:
            await tsc.delete_table(table.table_name)
    
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_unicode_create_table_unicode_name(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)
        invalid_table_name = u'啊齄丂狛狜'

        with pytest.raises(ValueError) as excinfo:
            async with tsc:
                await tsc.create_table(invalid_table_name)
            assert "Storage table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)
    
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_create_table_invalid_name(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            async with tsc:
                await tsc.create_table(table_name=invalid_table_name)
            assert "Storage table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)
