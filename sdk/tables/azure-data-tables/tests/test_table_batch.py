# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
import pytest

import uuid
from datetime import datetime
from dateutil.tz import tzutc

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError)
from azure.data.tables import EdmType, TableEntity, EntityProperty

from _shared.testcase import GlobalStorageAccountPreparer, TableTestCase, LogCaptured

#------------------------------------------------------------------------------
TEST_TABLE_PREFIX = 'table'
#------------------------------------------------------------------------------

class StorageTableBatchTest(TableTestCase):

    def _set_up(self, storage_account, storage_account_key):
        self.ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
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
        return Entity(**properties)

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

    def _assert_default_entity(self, entity, headers=None):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEqual(entity['age'], 39)
        self.assertEqual(entity['sex'], 'male')
        self.assertEqual(entity['married'], True)
        self.assertEqual(entity['deceased'], False)
        self.assertFalse("optional" in entity)
        self.assertFalse("aquarius" in entity)
        self.assertEqual(entity['ratio'], 3.1)
        self.assertEqual(entity['evenratio'], 3.0)
        self.assertEqual(entity['large'], 933311100)
        self.assertEqual(entity['Birthday'], datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['birthday'], datetime(1970, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['binary'], b'binary')
        self.assertIsInstance(entity['other'], EntityProperty)
        self.assertEqual(entity['other'].type, EdmType.INT32)
        self.assertEqual(entity['other'].value, 20)
        self.assertEqual(entity['clsid'], uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833'))
        self.assertTrue('metadata' in entity.odata)
        self.assertIsNotNone(entity.timestamp)
        self.assertIsInstance(entity.timestamp, datetime)
        if headers:
            self.assertTrue("etag" in headers)
            self.assertIsNotNone(headers['etag'])

    def _assert_updated_entity(self, entity):
        '''
        Asserts that the entity passed in matches the updated entity.
        '''
        self.assertEqual(entity.age, 'abc')
        self.assertEqual(entity.sex, 'female')
        self.assertFalse(hasattr(entity, "married"))
        self.assertFalse(hasattr(entity, "deceased"))
        self.assertEqual(entity.sign, 'aquarius')
        self.assertFalse(hasattr(entity, "optional"))
        self.assertFalse(hasattr(entity, "ratio"))
        self.assertFalse(hasattr(entity, "evenratio"))
        self.assertFalse(hasattr(entity, "large"))
        self.assertFalse(hasattr(entity, "Birthday"))
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertFalse(hasattr(entity, "other"))
        self.assertFalse(hasattr(entity, "clsid"))
        self.assertIsNotNone(entity.odata['etag'])
        self.assertIsNotNone(entity.timestamp)
        self.assertIsInstance(entity.timestamp, datetime)

    #--Test cases for batch ---------------------------------------------
    def test_inferred_types(self):
        # Arrange
        # Act
        entity = TableEntity()
        entity.PartitionKey = '003'
        entity.RowKey = 'batch_all_operations_together-1'
        entity.test = EntityProperty(True)
        entity.test2 = EntityProperty(b'abcdef')
        entity.test3 = EntityProperty(u'c9da6455-213d-42c9-9a79-3e9149a57833')
        entity.test4 = EntityProperty(datetime(1973, 10, 4, tzinfo=tzutc()))
        entity.test5 = EntityProperty(u"stringystring")
        entity.test6 = EntityProperty(3.14159)
        entity.test7 = EntityProperty(100)
        entity.test8 = EntityProperty(2 ** 33, EdmType.INT64)

        # Assert
        self.assertEqual(entity.test.type, EdmType.BOOLEAN)
        self.assertEqual(entity.test2.type, EdmType.BINARY)
        self.assertEqual(entity.test3.type, EdmType.GUID)
        self.assertEqual(entity.test4.type, EdmType.DATETIME)
        self.assertEqual(entity.test5.type, EdmType.STRING)
        self.assertEqual(entity.test6.type, EdmType.DOUBLE)
        self.assertEqual(entity.test7.type, EdmType.INT32)
        self.assertEqual(entity.test8.type, EdmType.INT64)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_insert(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
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
            self.assertIsNotNone(resp)
            result, headers = self.table.read_item('001', 'batch_insert', response_hook=lambda e, h: (e, h))
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_update(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_update'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_item(entity)

            entity = self.table.read_item('001', 'batch_update')
            self.assertEqual(3, entity.test3)
            entity.test2 = 'value1'

            batch = self.table.create_batch()
            batch.update_item(entity)
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            result, headers = self.table.read_item('001', 'batch_update', response_hook=lambda e, h: (e, h))
            self.assertEqual('value1', result.test2)
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_merge(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_merge'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_item(entity)

            entity = self.table.read_item('001', 'batch_merge')
            self.assertEqual(3, entity.test3)
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_merge'
            entity.test2 = 'value1'

            batch = self.table.create_batch()
            batch.update_item(entity, mode='MERGE')
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            entity, headers = self.table.read_item('001', 'batch_merge', response_hook=lambda e, h: (e, h))
            self.assertEqual('value1', entity.test2)
            self.assertEqual(1234567890, entity.test4)
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_update_if_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            etag = self.table.create_item(entity, response_hook=lambda e, h: h['etag'])

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            batch = self.table.create_batch()
            batch.update_item(sent_entity, etag=etag, match_condition=MatchConditions.IfNotModified)
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            entity, headers = self.table.read_item(entity['PartitionKey'], entity['RowKey'], response_hook=lambda e, h: (e, h))
            self._assert_updated_entity(entity)
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_update_if_doesnt_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            self.table.create_item(entity)

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            batch = self.table.create_batch()
            batch.update_item(
                sent_entity1,
                etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                match_condition=MatchConditions.IfNotModified)
            try:
                self.table.commit_batch(batch)
            except PartialBatchErrorException as error:
                pass  # TODO
                #self.assertEqual(error.code, 'UpdateConditionNotSatisfied')
                #self.assertTrue('The update condition specified in the request was not satisfied.' in str(error))
            else:
                self.fail('AzureBatchOperationError was expected')

            # Assert
            received_entity = self.table.read_item(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_insert_replace(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_insert_replace'
            entity.test = True
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = self.table.create_batch()
            batch.upsert_item(entity)
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            entity, headers = self.table.read_item('001', 'batch_insert_replace', response_hook=lambda e, h: (e, h))
            self.assertIsNotNone(entity)
            self.assertEqual('value', entity.test2)
            self.assertEqual(1234567890, entity.test4)
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_insert_merge(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_insert_merge'
            entity.test = True
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = self.table.create_batch()
            batch.upsert_item(entity, mode='MERGE')
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            entity, headers = self.table.read_item('001', 'batch_insert_merge', response_hook=lambda e, h: (e, h))
            self.assertIsNotNone(entity)
            self.assertEqual('value', entity.test2)
            self.assertEqual(1234567890, entity.test4)
            self.assertEqual(list(resp)[0].headers['Etag'], headers['etag'])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_delete(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_delete'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_item(entity)

            entity = self.table.read_item('001', 'batch_delete')
            self.assertEqual(3, entity.test3)

            batch = self.table.create_batch()
            batch.delete_item('001', 'batch_delete')
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertIsNotNone(resp)
            self.assertEqual(list(resp)[0].status_code, 204)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_inserts(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = 'batch_inserts'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)

            batch = self.table.create_batch()
            for i in range(100):
                entity.RowKey = str(i)
                batch.create_item(entity)
            self.table.commit_batch(batch)

            entities = list(self.table.query_items("PartitionKey eq 'batch_inserts'"))

            # Assert
            self.assertIsNotNone(entities)
            self.assertEqual(100, len(entities))
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_all_operations_together(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '003'
            entity.RowKey = 'batch_all_operations_together-1'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-2'
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-4'
            self.table.create_item(entity)

            batch = self.table.create_batch()
            entity.RowKey = 'batch_all_operations_together'
            batch.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-1'
            batch.delete_item(entity.PartitionKey, entity.RowKey)
            entity.RowKey = 'batch_all_operations_together-2'
            entity.test3 = 10
            batch.update_item(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            entity.test3 = 100
            batch.update_item(entity, mode='MERGE')
            entity.RowKey = 'batch_all_operations_together-4'
            entity.test3 = 10
            batch.upsert_item(entity)
            entity.RowKey = 'batch_all_operations_together-5'
            batch.upsert_item(entity, mode='MERGE')
            resp = self.table.commit_batch(batch)

            # Assert
            self.assertEqual(6, len(list(resp)))
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            self.assertEqual(5, len(entities))
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_all_operations_together_context_manager(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            entity = Entity()
            entity.PartitionKey = '003'
            entity.RowKey = 'batch_all_operations_together-1'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-2'
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            self.table.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-4'
            self.table.create_item(entity)

            with self.table.create_batch() as batch:
                entity.RowKey = 'batch_all_operations_together'
                batch.create_item(entity)
                entity.RowKey = 'batch_all_operations_together-1'
                batch.delete_item(entity.PartitionKey, entity.RowKey)
                entity.RowKey = 'batch_all_operations_together-2'
                entity.test3 = 10
                batch.update_item(entity)
                entity.RowKey = 'batch_all_operations_together-3'
                entity.test3 = 100
                batch.update_item(entity, mode='MERGE')
                entity.RowKey = 'batch_all_operations_together-4'
                entity.test3 = 10
                batch.upsert_item(entity)
                entity.RowKey = 'batch_all_operations_together-5'
                batch.upsert_item(entity, mode='MERGE')

            # Assert
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            self.assertEqual(5, len(entities))
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_reuse(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table2 = self._get_table_reference('table2')
            table2.create_table()

            # Act
            entity = Entity()
            entity.PartitionKey = '003'
            entity.RowKey = 'batch_all_operations_together-1'
            entity.test = EntityProperty(True)
            entity.test2 = 'value'
            entity.test3 = 3
            entity.test4 = EntityProperty(1234567890)
            entity.test5 = datetime.utcnow()

            batch = TableBatchClient()
            batch.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-2'
            batch.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            batch.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-4'
            batch.create_item(entity)

            self.table.commit_batch(batch)
            table2.commit_batch(batch)

            batch = TableBatchClient()
            entity.RowKey = 'batch_all_operations_together'
            batch.create_item(entity)
            entity.RowKey = 'batch_all_operations_together-1'
            batch.delete_item(entity.PartitionKey, entity.RowKey)
            entity.RowKey = 'batch_all_operations_together-2'
            entity.test3 = 10
            batch.update_item(entity)
            entity.RowKey = 'batch_all_operations_together-3'
            entity.test3 = 100
            batch.update_item(entity, mode='MERGE')
            entity.RowKey = 'batch_all_operations_together-4'
            entity.test3 = 10
            batch.upsert_item(entity)
            entity.RowKey = 'batch_all_operations_together-5'
            batch.upsert_item(entity, mode='MERGE')

            self.table.commit_batch(batch)
            resp = table2.commit_batch(batch)

            # Assert
            self.assertEqual(6, len(list(resp)))
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            self.assertEqual(5, len(entities))
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_same_row_operations_fail(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_item(entity)

            # Act
            batch = self.table.create_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.update_item(entity)
            entity = self._create_random_entity_dict(
                '001', 'batch_negative_1')

            # Assert
            with self.assertRaises(ValueError):
                batch.update_item(entity, mode='MERGE')
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_different_partition_operations_fail(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_item(entity)

            # Act
            batch = self.table.create_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            batch.update_item(entity)

            entity = self._create_random_entity_dict(
                '002', 'batch_negative_1')

            # Assert
            with self.assertRaises(ValueError):
                batch.create_item(entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    def test_batch_too_many_ops(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_item(entity)

            # Act
            with self.assertRaises(ValueError):
                batch = self.table.create_batch()
                for i in range(0, 101):
                    entity = Entity()
                    entity.PartitionKey = 'large'
                    entity.RowKey = 'item{0}'.format(i)
                    batch.create_item(entity)

            # Assert
        finally:
            self._tear_down()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
