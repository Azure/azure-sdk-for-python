# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from dateutil.tz import tzutc
import sys
from time import sleep
import uuid

import pytest

from devtools_testutils import AzureTestCase

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    HttpResponseError,
    ClientAuthenticationError
)
from azure.data.tables import (
    EdmType,
    TableEntity,
    EntityProperty,
    UpdateMode,
    BatchTransactionResult,
    BatchErrorException,
    TableServiceClient,
    TableEntity,
    UpdateMode
)

from _shared.testcase import TableTestCase, SLEEP_DELAY
from preparers import CosmosPreparer

#------------------------------------------------------------------------------
TEST_TABLE_PREFIX = 'table'
#------------------------------------------------------------------------------

class StorageTableClientTest(AzureTestCase, TableTestCase):

    def _set_up(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        self.ts = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), tables_primary_cosmos_account_key)
        self.table_name = self.get_resource_name('uttable')
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live:
            try:
                self.ts.create_table(self.table_name)
            except ResourceExistsError:
                pass

        self.test_tables = []

    def _tear_down(self):
        if self.is_live:
            try:
                self.ts.delete_table(self.table_name)
            except:
                pass

            for table_name in self.test_tables:
                try:
                    self.ts.delete_table(table_name)
                except:
                    pass
            sleep(SLEEP_DELAY)

    #--Helpers-----------------------------------------------------------------

    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        self.test_tables.append(table_name)
        return self.ts.get_table_client(table_name)

    def _create_random_entity_dict(self, pk=None, rk=None):
        '''
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        '''
        partition = pk if pk is not None else self.get_resource_name('pk')
        row = rk if rk is not None else self.get_resource_name('rk')
        properties = {
            'PartitionKey': partition,
            'RowKey': row,
            'age': 39,
            'sex': 'male',
            'married': True,
            'deceased': False,
            'optional': None,
            'ratio': 3.1,
            'evenratio': 3.0,
            'large': 933311100,
            'Birthday': datetime(1973, 10, 4, tzinfo=tzutc()),
            'birthday': datetime(1970, 10, 4, tzinfo=tzutc()),
            'binary': b'binary',
            'other': EntityProperty(20, EdmType.INT32),
            'clsid': uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        }
        return TableEntity(**properties)

    def _create_updated_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        '''
        return {
            'PartitionKey': partition,
            'RowKey': row,
            'age': 'abc',
            'sex': 'female',
            'sign': 'aquarius',
            'birthday': datetime(1991, 10, 4, tzinfo=tzutc())
        }

    def _assert_default_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        assert entity['age'] ==  39
        assert entity['sex'] ==  'male'
        assert entity['married'] ==  True
        assert entity['deceased'] ==  False
        assert not "optional" in entity
        assert entity['ratio'] ==  3.1
        assert entity['evenratio'] ==  3.0
        assert entity['large'] ==  933311100
        assert entity['Birthday'] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity['birthday'] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity['binary'].value ==  b'binary'
        assert entity['other'] ==  20
        assert entity['clsid'] ==  uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        assert '_metadata' in entity

    def _assert_updated_entity(self, entity):
        '''
        Asserts that the entity passed in matches the updated entity.
        '''
        assert entity.age ==  'abc'
        assert entity.sex ==  'female'
        assert not hasattr(entity, "married")
        assert not hasattr(entity, "deceased")
        assert entity.sign ==  'aquarius'
        assert not hasattr(entity, "optional")
        assert not hasattr(entity, "ratio")
        assert not hasattr(entity, "evenratio")
        assert not hasattr(entity, "large")
        assert not hasattr(entity, "Birthday")
        assert entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc())
        assert not hasattr(entity, "other")
        assert not hasattr(entity, "clsid")
        assert entity['_metadata']['etag'] is not None

    #--Test cases for batch ---------------------------------------------
    def _assert_valid_batch_transaction(self, transaction, length):
        assert isinstance(transaction,  BatchTransactionResult)
        assert length ==  len(transaction.entities)
        assert length ==  len(transaction.results)
        assert length ==  len(transaction.requests)

    @pytest.mark.skip("pending")
    @CosmosPreparer()
    def test_batch_insert(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_insert'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = self.table.create_batch()
            batch.create_item(entity)
            resp = self.table.commit_batch(batch)

            # Assert
            assert resp is not None
            result, headers = self.table.read_item('001', 'batch_insert', response_hook=lambda e, h: (e, h))
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_update(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = u'001'
            entity.RowKey = u'batch_update'
            entity.test = EntityProperty(True)
            entity.test2 = u'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_entity(entity)

            entity = self.table.get_entity(u'001', u'batch_update')
            assert 3 ==  entity.test3.value
            entity.test2 = u'value1'

            batch = self.table.create_batch()
            batch.update_entity(entity)
            transaction_result = self.table.send_batch(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert transaction_result.get_entity(entity.RowKey) is not None
            result = self.table.get_entity('001', 'batch_update')
            assert 'value1' ==  result.test2.value
            assert entity.PartitionKey ==  u'001'
            assert entity.RowKey ==  u'batch_update'
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_merge(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_merge'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_entity(entity)

            entity = self.table.get_entity('001', 'batch_merge')
            assert 3 ==  entity.test3
            entity = TableEntity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_merge'
            entity.test2 = 'value1'

            batch = self.table.create_batch()
            batch.update_entity(entity, mode='MERGE')
            resp = self.table.send_batch(batch)

            # Assert
            assert resp is not None
            entity, headers = self.table.get_entity('001', 'batch_merge', response_hook=lambda e, h: (e, h))
            assert 'value1' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_update_if_match(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()
            resp = self.table.create_entity(entity=entity)
            etag = resp['etag']

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            batch = self.table.create_batch()
            batch.update_entity(
                sent_entity,
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
                mode=UpdateMode.REPLACE
            )
            transaction_result = self.table.send_batch(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert transaction_result.get_entity(sent_entity['RowKey']) is not None

            entity = self.table.get_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])
            self._assert_updated_entity(entity)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_update_if_doesnt_match(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()
            self.table.create_entity(entity)

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            batch = self.table.create_batch()
            batch.update_entity(
                sent_entity1,
                etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                match_condition=MatchConditions.IfNotModified
            )

            with pytest.raises(HttpResponseError):
                self.table.send_batch(batch)

            # Assert
            received_entity = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_insert_replace(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_insert_replace'
            entity.test = True
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = self.table.create_batch()
            batch.upsert_item(entity)
            resp = self.table.send_batch(batch)

            # Assert
            assert resp is not None
            entity, headers = self.table.get_entity('001', 'batch_insert_replace', response_hook=lambda e, h: (e, h))
            assert entity is not None
            assert 'value' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_insert_merge(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_insert_merge'
            entity.test = True
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = self.table.create_batch()
            batch.upsert_item(entity, mode='MERGE')
            resp = self.table.send_batch(batch)

            # Assert
            assert resp is not None
            entity, headers = self.table.get_entity('001', 'batch_insert_merge', response_hook=lambda e, h: (e, h))
            assert entity is not None
            assert 'value' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_delete(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = u'001'
            entity.RowKey = u'batch_delete'
            entity.test = EntityProperty(True)
            entity.test2 = u'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_entity(entity)

            entity = self.table.get_entity(partition_key=u'001', row_key=u'batch_delete')
            assert 3 ==  entity.test3

            batch = self.table.create_batch()
            batch.delete_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)
            transaction_result = self.table.send_batch(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert transaction_result.get_entity(entity.RowKey) is not None

            with pytest.raises(ResourceNotFoundError):
                entity = self.table.get_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_inserts(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = 'batch_inserts'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)

            batch = self.table.create_batch()
            transaction_count = 0
            for i in range(20):
                entity.RowKey = str(i)
                batch.create_entity(entity)
                transaction_count += 1
            transaction_result = self.table.send_batch(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert transaction_result.get_entity(entity.RowKey) is not None

            entities = list(self.table.query_entities("PartitionKey eq 'batch_inserts'"))

            # Assert
            assert entities is not None
            assert transaction_count ==  len(entities)
            e = self.table.get_entity('batch_inserts', '1')
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_all_operations_together(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = '003'
            entity.RowKey = 'batch_all_operations_together-1'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-2'
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-4'
            self.table.create_entity(entity)

            batch = self.table.create_batch()
            entity.RowKey = 'batch_all_operations_together'
            batch.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-1'
            batch.delete_item(entity.PartitionKey, entity.RowKey)
            entity.RowKey = 'batch_all_operations_together-2'
            entity.test3 = 10
            batch.update_entity(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            entity.test3 = 100
            batch.update_entity(entity, mode='MERGE')
            entity.RowKey = 'batch_all_operations_together-4'
            entity.test3 = 10
            batch.upsert_item(entity)
            entity.RowKey = 'batch_all_operations_together-5'
            batch.upsert_item(entity, mode='MERGE')
            resp = self.table.send_batch(batch)

            # Assert
            assert 6 ==  len(list(resp))
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skip("merge operations fail in cosmos: https://github.com/Azure/azure-sdk-for-python/issues/13844")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_all_operations_together_context_manager(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            entity = TableEntity()
            entity.PartitionKey = '003'
            entity.RowKey = 'batch_all_operations_together-1'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-2'
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            self.table.create_entity(entity)
            entity.RowKey = 'batch_all_operations_together-4'
            self.table.create_entity(entity)

            with self.table.create_batch() as batch:
                entity.RowKey = 'batch_all_operations_together'
                batch.create_entity(entity)
                entity.RowKey = 'batch_all_operations_together-1'
                batch.delete_item(entity.PartitionKey, entity.RowKey)
                entity.RowKey = 'batch_all_operations_together-2'
                entity.test3 = 10
                batch.update_entity(entity)
                entity.RowKey = 'batch_all_operations_together-3'
                entity.test3 = 100
                batch.update_entity(entity, mode='MERGE')
                entity.RowKey = 'batch_all_operations_together-4'
                entity.test3 = 10
                batch.upsert_item(entity)
                entity.RowKey = 'batch_all_operations_together-5'
                batch.upsert_item(entity, mode='MERGE')

            # Assert
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_same_row_operations_fail(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            batch = self.table.create_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.update_entity(entity)
            entity = self._create_random_entity_dict(
                '001', 'batch_negative_1')
            batch.update_entity(entity, mode=UpdateMode.MERGE)
            # Assert
            with pytest.raises(BatchErrorException):
                self.table.send_batch(batch)
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_different_partition_operations_fail(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            batch = self.table.create_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.update_entity(entity)

            entity = self._create_random_entity_dict(
                '002', 'batch_negative_1')

            # Assert
            with pytest.raises(ValueError):
                batch.create_entity(entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("On Cosmos, the limit is not specified.")
    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_batch_too_many_ops(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_entity(entity)

            # Act
            with pytest.raises(BatchErrorException):
                batch = self.table.create_batch()
                for i in range(0, 101):
                    entity = TableEntity()
                    entity.PartitionKey = 'large'
                    entity.RowKey = 'item{0}'.format(i)
                    batch.create_entity(entity)

            # Assert
        finally:
            self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_new_non_existent_table(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            tc = self.ts.get_table_client("doesntexist")

            batch = tc.create_batch()
            batch.create_entity(entity)

            with pytest.raises(ResourceNotFoundError):
                resp = tc.send_batch(batch)
            # Assert
        finally:
            self._tear_down()


    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @CosmosPreparer()
    def test_new_delete_nonexistent_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')

            batch = self.table.create_batch()
            batch.delete_entity(entity['PartitionKey'], entity['RowKey'])

            with pytest.raises(ResourceNotFoundError):
                resp = self.table.send_batch(batch)

        finally:
            self._tear_down()
