# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.data.tables import (
    ResourceTypes,
    AccountSasPermissions,
    TableRetentionPolicy,
    UpdateMode,
    TableAccessPolicy,
    TableAnalyticsLogging,
    TableMetrics,
    TableServiceClient,
    TableItem,
    generate_account_sas,
    ResourceTypes
)
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import ResourceExistsError

from _shared.testcase import TableTestCase, TEST_TABLE_PREFIX
from preparers import tables_decorator, tables_decorator

# ------------------------------------------------------------------------------

class TestTable(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_create_properties(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()
        # Act
        created = ts.create_table(table_name)

        # Assert
        assert created.table_name == table_name

        properties = ts.get_service_properties()
        ts.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
        # have to wait for return to service
        p = ts.get_service_properties()
        # have to wait for return to service
        ts.set_service_properties(
            minute_metrics=TableMetrics(
                enabled=True,
                include_apis=True,
                retention_policy=TableRetentionPolicy(enabled=True, days=5)
            )
        )

        ps = ts.get_service_properties()
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_create_table(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table_name = self._get_table_reference()

        # Act
        table = ts.get_table_client(table_name)
        created = table.create_table()

        # Assert
        assert created.name == table_name
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_create_table_fail_on_exist(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()

        # Act
        created = ts.create_table(table_name)
        with pytest.raises(ResourceExistsError):
            ts.create_table(table_name)

        name_filter = "TableName eq '{}'".format(table_name)
        existing = list(ts.query_tables(name_filter))

        # Assert
        assert created is not None
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_query_tables_per_page(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table_name = "mytable"

        for i in range(5):
            ts.create_table(table_name + str(i))

        query_filter = "TableName eq 'mytable0' or TableName eq 'mytable1' or TableName eq 'mytable2'"
        table_count = 0
        page_count = 0
        for table_page in ts.query_tables(query_filter, results_per_page=2).by_page():

            temp_count = 0
            for table in table_page:
                temp_count += 1
            assert temp_count <= 2
            page_count += 1
            table_count += temp_count

        assert page_count == 2
        assert table_count == 3

        self._delete_all_tables(ts)

    @tables_decorator
    @recorded_by_proxy
    def test_create_table_if_exists(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()

        t0 = ts.create_table(table_name)
        t1 = ts.create_table_if_not_exists(table_name)

        assert t0 is not None
        assert t1 is not None
        assert t0.table_name == t1.table_name
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_create_table_if_exists_new_table(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()

        t = ts.create_table_if_not_exists(table_name)

        assert t is not None
        assert t.table_name ==  table_name
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_query_tables(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        t = self._create_table(ts)

        # Act
        tables = list(ts.list_tables())

        # Assert
        for table_item in tables:
            assert isinstance(table_item,  TableItem)

        assert tables is not None
        assert len(tables) >=  1
        assert tables[0] is not None

        self._delete_all_tables(ts)

    @tables_decorator
    @recorded_by_proxy
    def test_query_tables_with_filter(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        t = self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(t.table_name)
        tables = list(ts.query_tables(name_filter))

        for table_item in tables:
            assert isinstance(table_item,  TableItem)

        # Assert
        assert tables is not None
        assert len(tables) ==  1
        ts.delete_table(t.table_name)

        self._delete_all_tables(ts)

    @tables_decorator
    @recorded_by_proxy
    def test_query_tables_with_num_results(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        prefix = 'listtable'
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_list = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_list)

        # Act
        small_page = []
        big_page = []
        for s in next(ts.list_tables(results_per_page=3).by_page()):
            small_page.append(s)
            assert s.name.startswith(prefix)
        for t in next(ts.list_tables().by_page()):
            big_page.append(t)
            assert t.name.startswith(prefix)

        # Assert
        assert len(small_page) ==  3
        assert len(big_page) >=  4

        self._delete_all_tables(ts)

    @tables_decorator
    @recorded_by_proxy
    def test_query_tables_with_marker(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        prefix = 'listtable'
        table_names = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_names)

        # Act
        generator1 = ts.list_tables(results_per_page=2).by_page()
        next(generator1)
        generator2 = ts.list_tables(results_per_page=2).by_page(
            continuation_token=generator1.continuation_token)
        next(generator2)

        tables1 = generator1._current_page
        tables2 = generator2._current_page

        # Assert
        assert len(tables1) ==  2
        assert len(tables2) ==  2
        assert tables1 != tables2

        self._delete_all_tables(ts)

    @tables_decorator
    @recorded_by_proxy
    def test_delete_table_with_existing_table(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table = self._create_table(ts)

        # Act
        deleted = ts.delete_table(table_name=table.table_name)
        existing = list(ts.query_tables("TableName eq '{}'".format(table.table_name)))

        # Assert
        assert deleted is None
        assert len(existing) ==  0

    @tables_decorator
    @recorded_by_proxy
    def test_delete_table_with_non_existing_table_fail_not_exist(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table_name = self._get_table_reference()
        ts.delete_table(table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_get_table_acl(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        url = self.account_url(tables_storage_account_name, "table")
        account_url = self.account_url(tables_storage_account_name, "table")
        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)
        table = self._create_table(ts)
        try:
            # Act
            acl = table.get_table_access_policy()

            # Assert
            assert acl is not None
            assert len(acl) ==  0
        finally:
            ts.delete_table(table.table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_set_table_acl_with_empty_signed_identifiers(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = self._create_table(ts)
        try:
            # Act
            table.set_table_access_policy(signed_identifiers={})

            # Assert
            acl = table.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  0
        finally:
            ts.delete_table(table.table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_set_table_acl_with_empty_signed_identifier(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = self._create_table(ts)
        try:
            dt = datetime(2021, 6, 8, 2, 10, 9)
            signed_identifiers={
                'null': None,
                'empty': TableAccessPolicy(start=None, expiry=None, permission=None),
                'partial': TableAccessPolicy(permission='r'),
                'full': TableAccessPolicy(start=dt, expiry=dt, permission='r')
                }
            table.set_table_access_policy(signed_identifiers)
            acl = table.get_table_access_policy()
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

            table.set_table_access_policy(signed_identifiers)
            acl = table.get_table_access_policy()
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
            ts.delete_table(table.table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_set_table_acl_with_signed_identifiers(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = self._create_table(ts)
        client = ts.get_table_client(table_name=table.table_name)

        # Act
        start = datetime(2021, 6, 8, 2, 10, 9) - timedelta(minutes=5)
        expiry = datetime(2021, 6, 8, 2, 10, 9) + timedelta(hours=1)
        identifiers = {'testid': TableAccessPolicy(start=start, expiry=expiry, permission='r')}
        try:
            client.set_table_access_policy(signed_identifiers=identifiers)
            # Assert
            acl = client.get_table_access_policy()
            assert acl is not None
            assert len(acl) ==  1
            assert acl.get('testid')
            self._assert_policy_datetime(start, acl['testid'].start)
            self._assert_policy_datetime(expiry, acl['testid'].expiry)
            assert acl['testid'].permission == 'r'
        finally:
            ts.delete_table(table.table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_set_table_acl_too_many_ids(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        # Arrange
        account_url = self.account_url(tables_storage_account_name, "table")

        ts = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with pytest.raises(ValueError):
                table.set_table_access_policy(signed_identifiers=identifiers)
        finally:
            ts.delete_table(table.table_name)

    @tables_decorator
    @recorded_by_proxy
    def test_account_sas(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=tables_primary_storage_account_key, endpoint=account_url)

        table = self._create_table(tsc)
        try:
            entity = {
                'PartitionKey': u'test',
                'RowKey': u'test1',
                'text': u'hello',
            }
            table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)

            entity['RowKey'] = u'test2'
            table.upsert_entity(mode=UpdateMode.MERGE, entity=entity)

            token = AzureSasCredential(self.generate_sas(
                generate_account_sas,
                tables_primary_storage_account_key,
                resource_types=ResourceTypes(object=True),
                permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            ))

            account_url = self.account_url(tables_storage_account_name, "table")

            service = TableServiceClient(credential=token, endpoint=account_url)

            # Act

            sas_table = service.get_table_client(table.table_name)
            entities = list(sas_table.list_entities())

            # Assert
            assert len(entities) ==  2
            assert entities[0]['text'] == u'hello'
            assert entities[1]['text'] == u'hello'
        finally:
            tsc.delete_table(table.table_name)
    
    @tables_decorator
    @recorded_by_proxy
    def test_unicode_create_table_unicode_name(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)
        invalid_table_name = u'啊齄丂狛狜'

        with pytest.raises(ValueError) as excinfo:
            tsc.create_table(invalid_table_name)
            assert "Storage table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)
    
    @tables_decorator
    @recorded_by_proxy
    def test_create_table_invalid_name(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            tsc.create_table(invalid_table_name)
            assert "Storage table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
                excinfo)
