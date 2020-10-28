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

from _shared.testcase import TableTestCase, LogCaptured, RERUNS_DELAY
from _shared.cosmos_testcase import CachedCosmosAccountPreparer

from devtools_testutils import CachedResourceGroupPreparer

#------------------------------------------------------------------------------
TEST_TABLE_PREFIX = 'table'
#------------------------------------------------------------------------------

class StorageTableClientTest(TableTestCase):

    def _set_up(self, cosmos_account, cosmos_account_key):
        self.ts = TableServiceClient(self.account_url(cosmos_account, "table"), cosmos_account_key)
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
        assert entity['age'] ==  39
        assert entity['sex'] ==  'male'
        assert entity['married'] ==  True
        assert entity['deceased'] ==  False
        assert not "optional" in entity
        assert not "aquarius" in entity
        assert entity['ratio'] ==  3.1
        assert entity['evenratio'] ==  3.0
        assert entity['large'] ==  933311100
        assert entity['Birthday'], datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity['birthday'], datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity['binary'] ==  b'binary'
        assert isinstance(entity['other'],  EntityProperty)
        assert entity['other'].type ==  EdmType.INT32
        assert entity['other'].value ==  20
        assert entity['clsid'] ==  uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        assert 'metadata' in entity.odata
        assert entity.timestamp is not None
        assert isinstance(entity.timestamp,  datetime)
        if headers:
            assert "etag" in headers
            assert headers['etag'] is not None

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
        assert entity.odata['etag'] is not None
        assert entity.timestamp is not None
        assert isinstance(entity.timestamp,  datetime)

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
        entity.test8 = EntityProperty(10, EdmType.INT64)

        # Assert
        assert entity.test.type ==  EdmType.BOOLEAN
        assert entity.test2.type ==  EdmType.BINARY
        assert entity.test3.type ==  EdmType.GUID
        assert entity.test4.type ==  EdmType.DATETIME
        assert entity.test5.type ==  EdmType.STRING
        assert entity.test6.type ==  EdmType.DOUBLE
        assert entity.test7.type ==  EdmType.INT32
        assert entity.test8.type ==  EdmType.INT64


    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_insert(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_update(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 3 ==  entity.test3
            entity.test2 = 'value1'

            batch = self.table.create_batch()
            batch.update_item(entity)
            resp = self.table.commit_batch(batch)

            # Assert
            assert resp is not None
            result, headers = self.table.read_item('001', 'batch_update', response_hook=lambda e, h: (e, h))
            assert 'value1' ==  result.test2
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_merge(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 3 ==  entity.test3
            entity = Entity()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_merge'
            entity.test2 = 'value1'

            batch = self.table.create_batch()
            batch.update_item(entity, mode='MERGE')
            resp = self.table.commit_batch(batch)

            # Assert
            assert resp is not None
            entity, headers = self.table.read_item('001', 'batch_merge', response_hook=lambda e, h: (e, h))
            assert 'value1' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_update_if_match(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()
            etag = self.table.create_item(entity, response_hook=lambda e, h: h['etag'])

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            batch = self.table.create_batch()
            batch.update_item(sent_entity, etag=etag, match_condition=MatchConditions.IfNotModified)
            resp = self.table.commit_batch(batch)

            # Assert
            assert resp is not None
            entity, headers = self.table.read_item(entity['PartitionKey'], entity['RowKey'], response_hook=lambda e, h: (e, h))
            self._assert_updated_entity(entity)
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_update_if_doesnt_match(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
                pass
                #assert error.code ==  'UpdateConditionNotSatisfied'
                #assert 'The update condition specified in the request was not satisfied.' in str(error)
            else:
                self.fail('AzureBatchOperationError was expected')

            # Assert
            received_entity = self.table.read_item(entity['PartitionKey'], entity['RowKey'])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_insert_replace(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert resp is not None
            entity, headers = self.table.read_item('001', 'batch_insert_replace', response_hook=lambda e, h: (e, h))
            assert entity is not None
            assert 'value' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_insert_merge(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert resp is not None
            entity, headers = self.table.read_item('001', 'batch_insert_merge', response_hook=lambda e, h: (e, h))
            assert entity is not None
            assert 'value' ==  entity.test2
            assert 1234567890 ==  entity.test4
            assert list(resp)[0].headers['Etag'] ==  headers['etag']
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_delete(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 3 ==  entity.test3

            batch = self.table.create_batch()
            batch.delete_item('001', 'batch_delete')
            resp = self.table.commit_batch(batch)

            # Assert
            assert resp is not None
            assert list(resp)[0].status_code ==  204
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_inserts(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert entities is not None
            assert 100 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_all_operations_together(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 6 ==  len(list(resp))
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_all_operations_together_context_manager(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_reuse(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            assert 6 ==  len(list(resp))
            entities = list(self.table.query_items("PartitionKey eq '003'"))
            assert 5 ==  len(entities)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_same_row_operations_fail(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            with pytest.raises(ValueError):
                batch.update_item(entity, mode='MERGE')
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_different_partition_operations_fail(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
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
            with pytest.raises(ValueError):
                batch.create_item(entity)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedCosmosAccountPreparer(name_prefix="tablestest")
    def test_batch_too_many_ops(self, resource_group, location, cosmos_account, cosmos_account_key):
        # Arrange
        self._set_up(cosmos_account, cosmos_account_key)
        try:
            entity = self._create_random_entity_dict('001', 'batch_negative_1')
            self.table.create_item(entity)

            # Act
            with pytest.raises(ValueError):
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
