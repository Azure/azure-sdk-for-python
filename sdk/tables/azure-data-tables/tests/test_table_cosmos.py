# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core.exceptions import ResourceExistsError, HttpResponseError
from azure.data.tables import TableServiceClient, TableClient

from _shared.testcase import TableTestCase
from preparers import cosmos_decorator


class TestTableCosmos(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_create_table(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )

        table_name = self._get_table_reference()

        # Act
        table = ts.get_table_client(table_name)
        created = table.create_table()

        # Assert
        assert created.name == table_name
        ts.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_create_table_fail_on_exist(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table_name = self._get_table_reference()

        # Act
        created = ts.create_table(table_name)
        with pytest.raises(ResourceExistsError):
            ts.create_table(table_name)

        # Assert
        assert created
        ts.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_query_tables_per_page(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )

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

    @cosmos_decorator
    @recorded_by_proxy
    def test_query_tables(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table = self._create_table(ts)

        # Act
        tables = list(ts.list_tables())

        # Assert
        assert tables is not None
        assert len(tables) >= 1
        assert tables[0] is not None
        ts.delete_table(table.table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_query_tables_with_filter(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table = self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = list(ts.query_tables(name_filter))

        # Assert
        assert tables is not None
        assert len(tables) == 1
        ts.delete_table(table.table_name)

        self._delete_all_tables(ts)

    @cosmos_decorator
    @recorded_by_proxy
    def test_query_tables_with_num_results(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        prefix = "listtable"
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
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
        assert len(small_page) == 3
        assert len(big_page) >= 4

        self._delete_all_tables(ts)

    @cosmos_decorator
    @recorded_by_proxy
    def test_query_tables_with_marker(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        prefix = "listtable"
        table_names = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_names)

        # table_names.sort()

        # Act
        generator1 = ts.list_tables(results_per_page=2).by_page()
        next(generator1)
        generator2 = ts.list_tables(results_per_page=2).by_page(continuation_token=generator1.continuation_token)
        next(generator2)

        tables1 = generator1._current_page
        tables2 = generator2._current_page

        # Assert
        assert len(tables1) == 2
        assert len(tables2) == 2
        assert tables1 != tables2

        self._delete_all_tables(ts)

    @cosmos_decorator
    @recorded_by_proxy
    def test_delete_table_with_existing_table(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table = self._create_table(ts)

        # Act
        deleted = ts.delete_table(table_name=table.table_name)

        # Assert
        existing = list(ts.query_tables("TableName eq '{}'".format(table.table_name)))
        assert len(existing) == 0

    @cosmos_decorator
    @recorded_by_proxy
    def test_delete_table_with_non_existing_table_fail_not_exist(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table_name = self._get_table_reference()
        ts.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_create_table_underscore_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table_name = "my_table"

        client = ts.create_table(table_name)
        assert client.table_name == table_name

        ts.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_create_table_unicode_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        ts = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key
        )
        table_name = "啊齄丂狛狜"

        client = ts.create_table(table_name)
        assert client.table_name == table_name

        ts.delete_table(table_name)

    @cosmos_decorator
    @recorded_by_proxy
    def test_client_with_url_ends_with_table_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        # test table client has the same table name as in url
        tc = TableClient(invalid_url, table_name, credential=tables_primary_cosmos_account_key)
        with pytest.raises(HttpResponseError) as exc:
            tc.create_table()
        assert ("Request url is invalid") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test table client has a different table name as in url
        table_name2 = self.get_resource_name("mytable2")
        tc2 = TableClient(invalid_url, table_name2, credential=tables_primary_cosmos_account_key)
        with pytest.raises(HttpResponseError) as exc:
            tc2.create_table()
        assert ("Request url is invalid") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)

        valid_tc = TableClient(url, table_name, credential=tables_primary_cosmos_account_key)
        valid_tc.create_table()
        # test creating a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            tc.create_table()
        assert ("Request url is invalid") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        # test deleting a table when it already exists
        with pytest.raises(HttpResponseError) as exc:
            tc.delete_table()
        assert ("Request url is invalid") in str(exc.value)
        assert ("Please check your account URL.") in str(exc.value)
        valid_tc.delete_table()
