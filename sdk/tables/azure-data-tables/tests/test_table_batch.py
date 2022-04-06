# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from datetime import datetime, timedelta
import os
import sys

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, set_custom_default_matcher

from azure.core import MatchConditions
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError
)
from azure.data.tables import (
    EdmType,
    EntityProperty,
    TableTransactionError,
    TableServiceClient,
    TableEntity,
    UpdateMode,
    generate_table_sas,
    TableSasPermissions,
    RequestTooLargeError,
    TransactionOperation,
    TableErrorCode,
    TableClient
)

from _shared.testcase import TableTestCase
from preparers import tables_decorator

#------------------------------------------------------------------------------
TEST_TABLE_PREFIX = 'table'
#------------------------------------------------------------------------------

class TestTableBatch(AzureRecordedTestCase, TableTestCase):
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_single_insert(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('create', entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            e = self.table.get_entity(row_key=entity['RowKey'], partition_key=entity['PartitionKey'])
            assert e['test'] ==  entity['test'].value
            assert e['test2'] ==  entity['test2']
            assert e['test3'] ==  entity['test3']
            assert e['test4'] ==  entity['test4'].value
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_single_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            resp = self.table.create_entity(entity)
            assert resp is not None

            entity['test3'] = 5
            entity['test5'] = datetime.utcnow()

            batch = [('update', entity, {'mode':UpdateMode.MERGE})]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]
            result = self.table.get_entity(row_key=entity['RowKey'], partition_key=entity['PartitionKey'])
            assert result['PartitionKey'] ==  u'001'
            assert result['RowKey'] ==  u'batch_insert'
            assert result['test3'] ==  5
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_update'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            entity['test6'] = (2 ** 40, "Edm.Int64")
            self.table.create_entity(entity)

            entity = self.table.get_entity(u'001', u'batch_update')
            assert 3 ==  entity['test3']
            entity['test2'] = u'value1'

            batch = [('update', entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            result = self.table.get_entity('001', 'batch_update')

            assert 'value1' ==  result['test2']
            assert entity['PartitionKey'] ==  u'001'
            assert entity['RowKey'] ==  u'batch_update'
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_merge(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_merge'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            self.table.create_entity(entity)

            resp_entity = self.table.get_entity(partition_key=u'001', row_key=u'batch_merge')
            assert 3 ==  entity['test3']
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_merge'
            entity['test2'] = u'value1'

            batch = [('update', entity, {'mode': UpdateMode.MERGE})]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            resp_entity = self.table.get_entity(partition_key=u'001', row_key=u'batch_merge')
            assert entity['test2'] ==  resp_entity['test2']
            assert 1234567890 ==  resp_entity['test4']
            assert entity['PartitionKey'] ==  resp_entity['PartitionKey']
            assert entity['RowKey'] ==  resp_entity['RowKey']
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_update_if_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            resp = self.table.create_entity(entity=entity)
            etag = resp['etag']

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            batch = [(
                'update',
                sent_entity,
                {'etag': etag, 'match_condition':MatchConditions.IfNotModified, 'mode':UpdateMode.REPLACE}
            )]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = self.table.get_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
            self._assert_updated_entity(entity)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_update_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            self.table.create_entity(entity)

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            batch = [(
                'update',
                sent_entity1,
                {'etag': u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"', 'match_condition':MatchConditions.IfNotModified}
            )]
            with pytest.raises(TableTransactionError) as error:
                self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            # Assert
            received_entity = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_single_op_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = 'batch_inserts'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)

            batch = []
            transaction_count = 0
            for i in range(10):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))
                transaction_count += 1

            entity = self._create_random_entity_dict()
            self.table.create_entity(entity)

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            batch = [(
                'update',
                sent_entity1,
                {'etag':u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"', 'match_condition': MatchConditions.IfNotModified}
            )]

            with pytest.raises(TableTransactionError) as error:
                self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            # Assert
            received_entity = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_insert_replace(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert_replace'
            entity['test'] = True
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('upsert', entity, {'mode': UpdateMode.REPLACE})]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = self.table.get_entity('001', 'batch_insert_replace')
            assert entity is not None
            assert 'value' ==  entity['test2']
            assert 1234567890 ==  entity['test4']
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_insert_merge(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '001'
            entity['RowKey'] = 'batch_insert_merge'
            entity['test'] = True
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = [('upsert', entity, {'mode': UpdateMode.MERGE})]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' in transaction_result[0]

            entity = self.table.get_entity('001', 'batch_insert_merge')
            assert entity is not None
            assert 'value' ==  entity['test2']
            assert 1234567890 ==  entity['test4']
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_delete(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = u'001'
            entity['RowKey'] = u'batch_delete'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = u'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()
            self.table.create_entity(entity)

            entity = self.table.get_entity(partition_key=u'001', row_key=u'batch_delete')
            assert 3 ==  entity['test3']

            batch = [('delete', entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert 'etag' not in transaction_result[0]

            with pytest.raises(ResourceNotFoundError):
                entity = self.table.get_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_inserts(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = 'batch_inserts'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)

            transaction_count = 0
            batch = []
            for i in range(100):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))
                transaction_count += 1
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert 'etag' in transaction_result[0]

            entities = list(self.table.query_entities("PartitionKey eq 'batch_inserts'"))

            # Assert
            assert entities is not None
            assert transaction_count ==  len(entities)
            e = self.table.get_entity('batch_inserts', '1')
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_all_operations_together(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '003'
            entity['RowKey'] = 'batch_all_operations_together-1'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-2'
            self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-3'
            self.table.create_entity(entity)
            entity['RowKey'] = 'batch_all_operations_together-4'
            self.table.create_entity(entity)
            transaction_count = 0

            batch = []
            entity['RowKey'] = 'batch_all_operations_together'
            batch.append((TransactionOperation.CREATE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-1'
            batch.append((TransactionOperation.DELETE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-2'
            entity['test3'] = 10
            batch.append((TransactionOperation.UPDATE, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-3'
            entity['test3'] = 100
            batch.append((TransactionOperation.UPDATE, entity.copy(), {'mode': UpdateMode.REPLACE}))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-4'
            entity['test3'] = 10
            batch.append((TransactionOperation.UPSERT, entity.copy()))
            transaction_count += 1

            entity['RowKey'] = 'batch_all_operations_together-5'
            batch.append((TransactionOperation.UPSERT, entity.copy(), {'mode': UpdateMode.REPLACE}))
            transaction_count += 1

            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert 'etag' in transaction_result[0]
            assert 'etag' not in transaction_result[1]
            assert 'etag' in transaction_result[2]
            assert 'etag' in transaction_result[3]
            assert 'etag' in transaction_result[4]
            assert 'etag' in transaction_result[5]

            # Assert
            entities = list(self.table.query_entities("PartitionKey eq '003'"))
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_reuse(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference('table2')
            table2 = self.ts.get_table_client(table2_name)
            table2.create_table()

            # Act
            entity = TableEntity()
            entity['PartitionKey'] = '003'
            entity['RowKey'] = 'batch_all_operations_together-1'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)
            entity['test5'] = datetime.utcnow()

            batch = []
            batch.append(('upsert', entity.copy()))
            entity['RowKey'] = 'batch_all_operations_together-2'
            batch.append(('upsert', entity.copy()))
            entity['RowKey'] = 'batch_all_operations_together-3'
            batch.append(('upsert', entity.copy()))
            entity['RowKey'] = 'batch_all_operations_together-4'
            batch.append(('upsert', entity.copy()))

            resp1 = self.table.submit_transaction(batch)
            resp2 = table2.submit_transaction(batch)

            entities = list(self.table.query_entities("PartitionKey eq '003'"))
            assert 4 ==  len(entities)
            table2 = list(table2.query_entities("PartitionKey eq '003'"))
            assert 4 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_same_row_operations_fail(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.append(('update', entity.copy()))

            entity = self._create_random_entity_dict(
                '001', 'batch_negative_1')
            batch.append(('update', entity.copy(), {'mode': UpdateMode.REPLACE}))

            # Assert

            with pytest.raises(TableTransactionError):
                self.table.submit_transaction(batch)

        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_different_partition_operations_fail(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.append(('update', entity.copy()))

            entity = self._create_random_entity_dict(
                '002', 'batch_negative_1')
            batch.append(('update', entity.copy()))

            with pytest.raises(ValueError):
                self.table.submit_transaction(batch)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_too_many_ops(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            with pytest.raises(TableTransactionError):
                batch = []
                for i in range(0, 101):
                    entity = TableEntity()
                    entity['PartitionKey'] = 'large'
                    entity['RowKey'] = 'item{0}'.format(i)
                    batch.append(('create', entity.copy()))
                self.table.submit_transaction(batch)

            # Assert
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_different_partition_keys(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            entity2 = self._create_random_entity_dict('002', 'batch_negative_1')

            batch = [('create', entity), ('create', entity2)]
            with pytest.raises(ValueError):
                self.table.submit_transaction(batch)

            # Assert
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_new_non_existent_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            tc = self.ts.get_table_client("doesntexist")

            batch = [('create', entity)]

            with pytest.raises(TableTransactionError):
                resp = tc.submit_transaction(batch)
            # Assert
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_new_invalid_key(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        invalid_key = tables_primary_storage_account_key.named_key.key[0:-6] + "==" # cut off a bit from the end to invalidate
        tables_primary_storage_account_key = AzureNamedKeyCredential(tables_storage_account_name, invalid_key)
        credential = AzureNamedKeyCredential(name=tables_storage_account_name, key=tables_primary_storage_account_key.named_key.key)
        self.ts = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=credential)
        self.table_name = self.get_resource_name('uttable')
        self.table = self.ts.get_table_client(self.table_name)

        entity = self._create_random_entity_dict('001', 'batch_negative_1')

        batch = [('create', entity)]

        with pytest.raises(ClientAuthenticationError):
            resp = self.table.submit_transaction(batch)

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_new_delete_nonexistent_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            batch = [('delete', entity)]

            with pytest.raises(TableTransactionError):
                resp = self.table.submit_transaction(batch)

        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_delete_batch_with_bad_kwarg(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            received = self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            good_etag = received.metadata["etag"]
            received.metadata["etag"] = u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"'

            batch = [('delete', received, {"match_condition": MatchConditions.IfNotModified})]

            with pytest.raises(TableTransactionError) as error:
                self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            received.metadata["etag"] = good_etag
            batch = [('delete', received, {"match_condition": MatchConditions.IfNotModified})]
            resp = self.table.submit_transaction(batch)

            assert resp is not None
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @pytest.mark.live_test_only
    @tables_decorator
    def test_batch_sas_auth(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:

            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True, read=True, update=True, delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )
            token = AzureSasCredential(token)

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)

            entity = TableEntity()
            entity['PartitionKey'] = 'batch_inserts'
            entity['test'] = EntityProperty(True, EdmType.BOOLEAN)
            entity['test2'] = 'value'
            entity['test3'] = 3
            entity['test4'] = EntityProperty(1234567890, EdmType.INT32)

            batch = []
            transaction_count = 0
            for i in range(10):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))
                transaction_count += 1
            transaction_result = table.submit_transaction(batch)

            assert transaction_result

            total_entities = 0
            for e in table.list_entities():
                total_entities += 1

            assert total_entities == transaction_count
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @pytest.mark.live_test_only  # Request bodies are very large
    @tables_decorator
    def test_batch_request_too_large(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:

            batch = []
            entity = {
                'PartitionKey': 'pk001',
                'Foo': os.urandom(1024*64),
                'Bar': os.urandom(1024*64),
                'Baz': os.urandom(1024*64)
            }
            for i in range(50):
                entity['RowKey'] = str(i)
                batch.append(('create', entity.copy()))

            with pytest.raises(RequestTooLargeError):
                self.table.submit_transaction(batch)

        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_with_mode(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference('table2')
            table2 = self.ts.get_table_client(table2_name)
            table2.create_table()

            # Act
            entity1 = {
                "PartitionKey": "pk001",
                "RowKey": "rk001",
                "Value": 1,
                "day": "Monday",
                "float": 1.001
            }
            entity2 = {
                "PartitionKey": "pk001",
                "RowKey": "rk002",
                "Value": 1,
                "day": "Monday",
                "float": 1.001
            }


            batch = [
                ("upsert", entity1, {"mode": "merge"}),
                ("upsert", entity2, {"mode": "replace"})
            ]

            resp = self.table.submit_transaction(batch)
            assert len(resp) == 2

            with pytest.raises(ValueError):
                batch = [
                    ("upsert", entity1, {"mode": "foo"}),
                    ("upsert", entity2, {"mode": "bar"})
                ]
                self.table.submit_transaction(batch)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator
    @recorded_by_proxy
    def test_batch_with_specialchar_partitionkey(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference('table2')
            table2 = self.ts.get_table_client(table2_name)
            table2.create_table()

            # Act
            entity1 = {
                'PartitionKey': "A'aaa\"_bbbb2",
                'RowKey': '"A\'aaa"_bbbb2',
                'test': '"A\'aaa"_bbbb2'
            }
            self.table.submit_transaction([("create", entity1)])
            get_entity = self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            self.table.submit_transaction([("upsert", entity1, {'mode': 'merge'})])
            get_entity = self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            self.table.submit_transaction([("upsert", entity1, {'mode': 'replace'})])
            get_entity = self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            self.table.submit_transaction([("update", entity1, {'mode': 'merge'})])
            get_entity = self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            self.table.submit_transaction([("update", entity1, {'mode': 'replace'})])
            get_entity = self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            entity_results = list(self.table.list_entities())
            assert entity_results[0] == entity1
            for entity in entity_results:
                get_entity = self.table.get_entity(
                    partition_key=entity['PartitionKey'],
                    row_key=entity['RowKey'])
                assert get_entity == entity1

            self.table.submit_transaction([("delete", entity1)])

        finally:
            self._tear_down()


class RequestCorrect(Exception):
    pass


class CheckBatchURL(HTTPPolicy):
    def __init__(self, account_url, table_name):
        if not account_url.startswith('http'):
            account_url = 'https://' + account_url
        self.url = account_url
        self.table = table_name
        super().__init__()

    def send(self, request):
        assert request.http_request.url == self.url + '/$batch'
        payload = request.http_request.body
        for line in payload.split(b'\r\n\r\n'):
            if line.startswith(b"PATCH") or line.startswith(b"POST"):
                assert line[line.index(b" ") + 1:].decode().startswith(self.url + "/" + self.table)
                raise RequestCorrect()
        raise AssertionError(
            "No matching PATCH/POST requests found in batch:\n{}".format(payload.decode()))


class TestBatchUnitTests(TableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_sas_credential = "fake_sas_credential"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA=="
    credential = AzureSasCredential(tables_sas_credential)
    entity1 = {
        "PartitionKey": "pk001",
        "RowKey": "rk001"
    }
    entity2 = {
        "PartitionKey": "pk001",
        "RowKey": "rk002"
    }
    batch = [
        ("upsert", entity1),
        ("upsert", entity2)
    ]

    def test_batch_url_http(self):
        url = self.account_url(self.tables_storage_account_name, "table").replace('https', 'http')
        table = TableClient(
            url,
            "batchtablename",
            credential=self.credential,
            per_call_policies=[CheckBatchURL(url, "batchtablename")])

        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_https(self):
        table = TableClient(
            self.account_url(self.tables_storage_account_name, "table"),
            "batchtablename",
            credential=self.credential,
            per_call_policies=[CheckBatchURL(self.account_url(self.tables_storage_account_name, "table"), "batchtablename")])

        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_china(self):
        url = self.account_url(self.tables_storage_account_name, "table").replace('core.windows.net', 'core.chinacloudapi.cn')
        table = TableClient(
            url,
            credential=self.credential,
            table_name='foo',
            per_call_policies=[CheckBatchURL(url, "foo")])

        # Assert
        assert table.account_name == self.tables_storage_account_name
        assert table.url.startswith('https://{}.{}.core.chinacloudapi.cn'.format(self.tables_storage_account_name, "table"))
        assert table.scheme == 'https'

        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_connection_string_key(self):
        conn_string = 'AccountName={};AccountKey={};'.format(self.tables_storage_account_name, self.tables_primary_storage_account_key)
        table = TableClient.from_connection_string(
            conn_string,
            table_name='foo',
            per_call_policies=[CheckBatchURL("https://{}.table.core.windows.net".format(self.tables_storage_account_name), "foo")]
        )
        assert table.scheme == 'https'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_connection_string_sas(self):
        token = AzureSasCredential(self.generate_sas_token())
        conn_string = 'AccountName={};SharedAccessSignature={};'.format(self.tables_storage_account_name, token.signature)

        table = TableClient.from_connection_string(
            conn_string,
            table_name='foo',
            per_call_policies=[CheckBatchURL("https://{}.table.core.windows.net".format(self.tables_storage_account_name), "foo")]
        )

        assert table.account_name == self.tables_storage_account_name
        assert table.url.startswith('https://' + self.tables_storage_account_name + '.table.core.windows.net')
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_connection_string_cosmos(self):
        conn_string = 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.cosmos.azure.com:443/;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)
        table = TableClient.from_connection_string(
            conn_string,
            table_name='foo',
            per_call_policies=[CheckBatchURL("https://{}.table.cosmos.azure.com:443".format(self.tables_storage_account_name), "foo")]
        )
        assert table.account_name == self.tables_storage_account_name
        assert table.url.startswith('https://' + self.tables_storage_account_name + '.table.cosmos.azure.com')
        assert table.scheme == 'https'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_connection_string_endpoint_protocol(self):
        # Arrange
        conn_string = 'AccountName={};AccountKey={};DefaultEndpointsProtocol=http;EndpointSuffix=core.chinacloudapi.cn;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://{}.table.core.chinacloudapi.cn".format(self.tables_storage_account_name), "foo")]
        )
        assert table.account_name == self.tables_storage_account_name
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_connection_string_custom_domain(self):
        conn_string = 'AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)

        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[CheckBatchURL("https://www.mydomain.com", "foo")]
        )
        assert table.url.startswith('https://www.mydomain.com')
        assert table.scheme == 'https'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

        conn_string = 'AccountName={};AccountKey={};TableEndpoint=http://www.mydomain.com;'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key)

        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://www.mydomain.com", "foo")]
        )
        assert table.url.startswith('http://www.mydomain.com')
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_custom_account_endpoint_path(self):
        token = AzureSasCredential(self.generate_sas_token())
        custom_account_url = "http://local-machine:11002/custom/account/path/" + token.signature
        conn_string = 'DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};'.format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key, custom_account_url)
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")]
        )
        assert table.account_name == self.tables_storage_account_name
        assert table._primary_hostname == 'local-machine:11002/custom/account/path'
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

        table = TableClient(
            endpoint=custom_account_url,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")]
        )
        assert table.account_name == "custom"
        assert table.table_name == "foo"
        assert table.credential == None
        assert table.url.startswith('http://local-machine:11002/custom/account/path')
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

        table = TableClient.from_table_url(
            "http://local-machine:11002/custom/account/path/foo" + token.signature,
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")]
        )
        assert table.account_name == "custom"
        assert table.table_name == "foo"
        assert table.credential == None
        assert table.url.startswith('http://local-machine:11002/custom/account/path')
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_complete_table_url(self):
        table_url = self.account_url(self.tables_storage_account_name, "table") + "/foo"
        table = TableClient(
            table_url,
            table_name='bar',
            credential=self.credential,
            per_call_policies=[CheckBatchURL("https://{}.table.core.windows.net/foo".format(self.tables_storage_account_name), "bar")]
        )

        assert table.scheme == 'https'
        assert table.table_name == 'bar'
        assert table.account_name == self.tables_storage_account_name
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_with_complete_url(self):
        # Arrange
        table_url = "https://{}.table.core.windows.net:443/foo".format(self.tables_storage_account_name)
        table = TableClient(
            endpoint=table_url,
            table_name='bar',
            credential=self.credential,
            per_call_policies=[CheckBatchURL("https://{}.table.core.windows.net:443/foo".format(self.tables_storage_account_name), "bar")]
        )

        # Assert
        assert table.scheme == 'https'
        assert table.table_name == 'bar'
        assert table.account_name == self.tables_storage_account_name
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

    def test_batch_url_for_cosmos_emulator(self):
        emulator_credential = AzureNamedKeyCredential('localhost', self.tables_primary_storage_account_key)
        emulator_connstr = "DefaultEndpointsProtocol=http;AccountName=localhost;AccountKey={};TableEndpoint=http://localhost:8902/;".format(
            self.tables_primary_storage_account_key
        )

        table = TableClient.from_connection_string(
            emulator_connstr,
            'tablename',
            per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")]
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table._cosmos_endpoint
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

        table = TableClient(
            "http://localhost:8902/",
            "tablename",
            credential=emulator_credential,
            per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")]
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table._cosmos_endpoint
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)

        table = TableClient.from_table_url(
            "http://localhost:8902/Tables('tablename')",
            credential=emulator_credential,
            per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")]
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == 'localhost'
        assert table.table_name == 'tablename'
        assert table._cosmos_endpoint
        assert table.scheme == 'http'
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)
