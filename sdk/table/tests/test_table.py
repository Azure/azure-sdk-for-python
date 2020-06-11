# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import sys
import locale
import os
from azure_table import TableServiceClient, generate_account_sas
from time import time
from wsgiref.handlers import format_date_time
from datetime import (
    datetime,
    timedelta,
)

from azure_table._generated.models import AccessPolicy, QueryOptions
from azure_table._models import TableSasPermissions
from azure_table._shared.models import ResourceTypes, AccountSasPermissions
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    HeadersPolicy,
    ContentDecodePolicy,
)

from _shared.testcase import TableTestCase, GlobalStorageAccountPreparer
from azure_table._shared.authentication import SharedKeyCredentialPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

# from azure.tables import (
#     TableServiceClient,
#     TableClient,
#     TableSasPermissions,
#     AccessPolicy,
#     ResourceTypes,
#     AccountSasPermissions,
#     generate_account_sas,
#     generate_table_sas
# )

# ------------------------------------------------------------------------------

TEST_TABLE_PREFIX = 'pytablesync'


# ------------------------------------------------------------------------------

def _create_pipeline(account, credential, **kwargs):
    # type: (Any, **Any) -> Tuple[Configuration, Pipeline]
    credential_policy = SharedKeyCredentialPolicy(account_name=account.name, account_key=credential)
    transport = RequestsTransport(**kwargs)
    policies = [
        HeadersPolicy(),
        credential_policy,
        ContentDecodePolicy(response_encoding="utf-8")]
    return Pipeline(transport, policies=policies)


class StorageTableTest(TableTestCase):

    # --Helpers-----------------------------------------------------------------
    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = ts.get_table_client(table_name)
        return table

    def _delete_table(self, ts, table):
        if table is None:
            return
        try:
            ts.delete_table(table.table_name)
        except ResourceNotFoundError:
            pass

    # --Test cases for tables --------------------------------------------------
    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_create_table(self, resource_group, location, storage_account, storage_account_key):
        # # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        # response = ts.create_table(table_name)
        # assert response.table_name == table_name

        table_name = self._get_table_reference()
        # table_client = ts.get_table_client(table_name)

        # Act
        created = ts.create_table(table_name)

        # Assert
        assert created.table_name == table_name
        # existing = list(ts.query_tables("TableName eq '{}'".format(table_name)))
        # This is causing problems
        # self.assertEqual(existing, [table_name])
        ts.delete_table(table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_create_table_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()
        # btable_client = ts.get_table_client(table_name)

        # Act
        created = ts.create_table(table_name)
        with self.assertRaises(ResourceExistsError):
            ts.create_table(table_name)

        # Assert
        self.assertTrue(created)
        # existing = list(ts.query_tables(query_options=QueryOptions(filter="TableName eq '{}'".format(table_name))))
        # self.assertEqual(existing[0], [table_name])
        ts.delete_table(table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_list_tables(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = self._create_table(ts)

        # Act
        tables = list(ts.list_tables())

        # Assert
        self.assertIsNotNone(tables)
        self.assertGreaterEqual(len(tables), 1)
        self.assertIsNotNone(tables[0])
        # self.assertNamedItemInContainer(tables, table.table_name)
        ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_list_tables_with_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = list(ts.query_tables(query_options=QueryOptions(filter=name_filter)))
        # Assert
        self.assertIsNotNone(tables)
        self.assertEqual(len(tables), 1)
        # self.assertEqual(tables[0].table_name, [table.table_name])
        # table.delete_table()
        ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_list_tables_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        query = QueryOptions()
        query.top = 3
        prefix = 'listtable'
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_list = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_list)

        # Act
        big_page = list(next(ts.list_tables().by_page()))
        small_page = list(next(ts.list_tables(query_options=query).by_page()))

        # Assert
        self.assertEqual(len(small_page), 3)
        self.assertGreaterEqual(len(big_page), 4)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_list_tables_with_marker(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        prefix = 'listtable'
        table_names = []
        for i in range(0, 4):
            self._create_table(ts, prefix + str(i), table_names)

        # table_names.sort()

        # Act
        generator1 = ts.list_tables(query_options=QueryOptions(top=2)).by_page()
        next(generator1)
        generator2 = ts.list_tables(query_options=QueryOptions(top=2)).by_page(
            continuation_token=generator1.continuation_token)
        next(generator2)

        tables1 = generator1._current_page
        tables2 = generator2._current_page

        # Assert
        self.assertEqual(len(tables1), 2)
        self.assertEqual(len(tables2), 2)
        self.assertNotEqual(tables1, tables2)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_delete_table_with_existing_table(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = self._create_table(ts)

        # Act
        # deleted = table.delete_table()
        deleted = ts.delete_table(table_name=table.table_name)

        # Assert
        self.assertIsNone(deleted)
        # existing = list(ts.query_tables("TableName eq '{}'".format(table.table_name)))
        # self.assertEqual(existing, [])

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_delete_table_with_non_existing_table_fail_not_exist(self, resource_group, location, storage_account,
                                                                 storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            ts.delete_table(table_name)

        # Assert

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_unicode_create_table_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos URLs support unicode table names")
        ts = TableServiceClient(url, storage_account_key)
        table_name = u'啊齄丂狛狜'

        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - table name must be alphanumeric, lowercase
            ts.create_table(table_name)

        # Assert

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_get_table_acl(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = self._create_table(ts)
        try:
            # Act
            acl = ts.get_table_access_policy(table_name=table.table_name)
            # acl = table.get_table_access_policy()

            # Assert
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            # self._delete_table(table)
            ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_set_table_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = self._create_table(ts)
        try:
            # Act
            ts.set_table_access_policy(table_name=table.table_name, signed_identifiers={})

            # Assert
            acl = ts.get_table_access_policy(table_name=table.table_name)
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            # self._delete_table(table)
            ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_set_table_acl_with_empty_signed_identifier(self, resource_group, location, storage_account,
                                                        storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = self._create_table(ts)
        try:
            # Act
            ts.set_table_access_policy(table_name=table.table_name, signed_identifiers={'empty': None})
            # Assert
            acl = ts.get_table_access_policy(table_name=table.table_name)
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertIsNotNone(acl['empty'])
            self.assertIsNone(acl['empty'].permission)
            self.assertIsNone(acl['empty'].expiry)
            self.assertIsNone(acl['empty'].start)
        finally:
            # self._delete_table(table)
            ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_set_table_acl_with_signed_identifiers(self, resource_group, location, storage_account,
                                                   storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = self._create_table(ts)

        # Act
        access_policy = AccessPolicy(permission=TableSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=5))
        identifiers = {'testid': access_policy}
        # identifiers = dict()
        # identifiers['testid'] = AccessPolicy(start=datetime.utcnow() - timedelta(minutes=5),
        #                                      expiry=datetime.utcnow() + timedelta(hours=1),
        #                                      permission=TableSasPermissions(query=True))
        try:
            ts.set_table_access_policy(table_name=table.table_name,signed_identifiers=identifiers)
            # Assert
            acl = ts.get_table_access_policy(table_name=table.table_name)
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertTrue('testid' in acl)
        finally:
            # self._delete_table(table)
            ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_set_table_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with self.assertRaisesRegex(ValueError,
                                        'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'):
                ts.set_table_access_policy(table_name=table.table_name, signed_identifiers=identifiers)
        finally:
            ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        tsc = TableServiceClient(url, storage_account_key)
        table = self._create_table(tsc)
        try:
            entity = {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'text': 'hello',
            }
            tsc.upsert_item(table_name=table.table_name,table_entity_properties=entity)

            entity['RowKey'] = 'test2'
            tsc.upsert_item(table_name=table.table_name,table_entity_properties=entity)

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
            entities = list(sas_table.read_all_items())

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].text, 'hello')
            self.assertEqual(entities[1].text, 'hello')
        finally:
            tsc.delete_table(table.table_name)

    @pytest.mark.skip("msrest fails deserialization: https://github.com/Azure/msrest-for-python/issues/192")
    @GlobalStorageAccountPreparer()
    def test_locale(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = (self._get_table_reference())
        init_locale = locale.getlocale()
        if os.name is "nt":
            culture = "Spanish_Spain"
        elif os.name is 'posix':
            culture = 'es_ES.UTF-8'
        else:
            culture = 'es_ES.utf8'

        try:
            locale.setlocale(locale.LC_ALL, culture)
            e = None

            # Act
            table.create_table()
            try:
                resp = ts.list_tables()
            except:
                e = sys.exc_info()[0]

            # Assert
            self.assertIsNone(e)
        finally:
            ts.delete_table(table.table_name)
            locale.setlocale(locale.LC_ALL, init_locale[0] or 'en_US')
