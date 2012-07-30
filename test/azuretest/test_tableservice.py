#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

from azure.storage.tableservice import *
from azure.storage import EntityProperty, Entity, StorageServiceProperties
from azure import WindowsAzureError


from azuretest.util import (credentials, 
                            getUniqueTestRunID,
                            STATUS_OK,
                            STATUS_CREATED,
                            STATUS_ACCEPTED,
                            STATUS_NO_CONTENT,
                            getUniqueNameBasedOnCurrentTime,
                            AzureTestCase)

import unittest
import time
from datetime import datetime

#------------------------------------------------------------------------------

MAX_RETRY = 60
#------------------------------------------------------------------------------
class StorageTest(AzureTestCase):

    def setUp(self):
        self.tc = TableService(account_name=credentials.getStorageServicesName(), 
                                   account_key=credentials.getStorageServicesKey())

        __uid = getUniqueTestRunID()
        table_base_name = u'testtable%s' % (__uid)
        self.table_name = getUniqueNameBasedOnCurrentTime(table_base_name)     
        self.additional_table_names = []
    
    def tearDown(self):
        self.cleanup()
        return super(StorageTest, self).tearDown()

    def cleanup(self):
        try:
            self.tc.delete_table(self.table_name)
        except: pass

        for name in self.additional_table_names:
            try:
                self.tc.delete_table(name)
            except: pass

    #--Helpers-----------------------------------------------------------------
    def _create_table(self, table_name):
        '''
        Creates a table with the specified name.
        '''
        self.tc.create_table(table_name, True)

    def _create_table_with_default_entities(self, table_name, entity_count):
        '''
        Creates a table with the specified name and adds entities with the 
        default set of values. PartitionKey is set to 'MyPartition' and RowKey 
        is set to a unique counter value starting at 1 (as a string).
        '''
        entities = []
        self._create_table(table_name)
        for i in range(1, entity_count + 1):
            entities.append(self.tc.insert_entity(table_name, self._create_default_entity_dict('MyPartition', str(i))))
        return entities

    def _create_default_entity_class(self, partition, row):
        '''
        Creates a class-based entity with fixed values, using all
        of the supported data types.
        '''
        # TODO: Edm.Binary and null
        entity = Entity()
        entity.PartitionKey = partition
        entity.RowKey = row
        entity.age = 39
        entity.sex = 'male'
        entity.married = True
        entity.deceased = False
        entity.optional = None
        entity.ratio = 3.1
        entity.large = 9333111000
        entity.Birthday = datetime(1973,10,04)
        entity.birthday = datetime(1970,10,04)
        entity.binary = None
        entity.other = EntityProperty('Edm.Int64', 20)
        entity.clsid = EntityProperty('Edm.Guid', 'c9da6455-213d-42c9-9a79-3e9149a57833')
        return entity

    def _create_default_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        '''
        # TODO: Edm.Binary and null
        return {'PartitionKey':partition, 
                'RowKey':row, 
                'age':39, 
                'sex':'male', 
                'married':True, 
                'deceased':False, 
                'optional':None, 
                'ratio':3.1, 
                'large':9333111000, 
                'Birthday':datetime(1973,10,04),
                'birthday':datetime(1970,10,04),
                'binary':EntityProperty('Edm.Binary', None),
                'other':EntityProperty('Edm.Int64', 20),
                'clsid':EntityProperty('Edm.Guid', 'c9da6455-213d-42c9-9a79-3e9149a57833')}

    def _create_updated_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        '''
        return {'PartitionKey':partition,
                'RowKey':row,
                'age':'abc',
                'sex':'female',
                'sign':'aquarius',
                'birthday':datetime(1991,10,04)}

    def _assert_default_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEquals(entity.age, 39)
        self.assertEquals(entity.sex, 'male')
        self.assertEquals(entity.married, True)
        self.assertEquals(entity.deceased, False)
        self.assertFalse(hasattr(entity, "aquarius"))
        self.assertEquals(entity.ratio, 3.1)
        self.assertEquals(entity.large, 9333111000)
        self.assertEquals(entity.Birthday, datetime(1973,10,04))
        self.assertEquals(entity.birthday, datetime(1970,10,04))
        self.assertEquals(entity.other, 20)
        self.assertIsInstance(entity.clsid, EntityProperty)
        self.assertEquals(entity.clsid.type, 'Edm.Guid')
        self.assertEquals(entity.clsid.value, 'c9da6455-213d-42c9-9a79-3e9149a57833')

    def _assert_updated_entity(self, entity):
        '''
        Asserts that the entity passed in matches the updated entity.
        '''
        self.assertEquals(entity.age, 'abc')
        self.assertEquals(entity.sex, 'female')
        self.assertFalse(hasattr(entity, "married"))
        self.assertFalse(hasattr(entity, "deceased"))
        self.assertEquals(entity.sign, 'aquarius')
        self.assertFalse(hasattr(entity, "optional"))
        self.assertFalse(hasattr(entity, "ratio"))
        self.assertFalse(hasattr(entity, "large"))
        self.assertFalse(hasattr(entity, "Birthday"))
        self.assertEquals(entity.birthday, datetime(1991,10,04))
        self.assertFalse(hasattr(entity, "other"))
        self.assertFalse(hasattr(entity, "clsid"))

    def _assert_merged_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity 
        merged with the updated entity.
        '''
        self.assertEquals(entity.age, 'abc')
        self.assertEquals(entity.sex, 'female')
        self.assertEquals(entity.sign, 'aquarius')
        self.assertEquals(entity.married, True)
        self.assertEquals(entity.deceased, False)
        self.assertEquals(entity.sign, 'aquarius')
        self.assertEquals(entity.ratio, 3.1)
        self.assertEquals(entity.large, 9333111000)
        self.assertEquals(entity.Birthday, datetime(1973,10,04))
        self.assertEquals(entity.birthday, datetime(1991,10,04))
        self.assertEquals(entity.other, 20)
        self.assertIsInstance(entity.clsid, EntityProperty)
        self.assertEquals(entity.clsid.type, 'Edm.Guid')
        self.assertEquals(entity.clsid.value, 'c9da6455-213d-42c9-9a79-3e9149a57833')

    #--Test cases for table service -------------------------------------------
    def test_get_set_table_service_properties(self):
        table_properties = self.tc.get_table_service_properties()
        self.tc.set_table_service_properties(table_properties)
        
        tests = [('logging.delete', True),
                 ('logging.delete', False),
                 ('logging.read', True),
                 ('logging.read', False),
                 ('logging.write', True),
                 ('logging.write', False),
                ]
        for path, value in tests:
            #print path
            cur = table_properties
            for component in path.split('.')[:-1]:
                cur = getattr(cur, component)

            last_attr = path.split('.')[-1]
            setattr(cur, last_attr, value)
            self.tc.set_table_service_properties(table_properties)

            retry_count = 0
            while retry_count < MAX_RETRY:
                table_properties = self.tc.get_table_service_properties()
                cur = table_properties
                for component in path.split('.'):
                    cur = getattr(cur, component)
                if value == cur:
                    break
                time.sleep(1)
                retry_count += 1

            self.assertEquals(value, cur)
            
    def test_table_service_retention_single_set(self):
        table_properties = self.tc.get_table_service_properties()
        table_properties.logging.retention_policy.enabled = False
        table_properties.logging.retention_policy.days = 5

        # TODO: Better error, ValueError?
        self.assertRaises(WindowsAzureError,
                         self.tc.set_table_service_properties,
                         table_properties)

        table_properties = self.tc.get_table_service_properties()
        table_properties.logging.retention_policy.days = None
        table_properties.logging.retention_policy.enabled = True

        # TODO: Better error, ValueError?
        self.assertRaises(WindowsAzureError,
                         self.tc.set_table_service_properties,
                         table_properties)

    def test_table_service_set_both(self):
        table_properties = self.tc.get_table_service_properties()
        table_properties.logging.retention_policy.enabled = True
        table_properties.logging.retention_policy.days = 5
        self.tc.set_table_service_properties(table_properties)
        table_properties = self.tc.get_table_service_properties()
        self.assertEquals(True, table_properties.logging.retention_policy.enabled)

        self.assertEquals(5, table_properties.logging.retention_policy.days)

    #--Test cases for tables --------------------------------------------------
    def test_create_table(self):
        # Arrange

        # Act
        created = self.tc.create_table(self.table_name)

        # Assert
        self.assertTrue(created)

    def test_create_table_fail_on_exist(self):
        # Arrange

        # Act
        created = self.tc.create_table(self.table_name, True)

        # Assert
        self.assertTrue(created)

    def test_create_table_with_already_existing_table(self):
        # Arrange

        # Act
        created1 = self.tc.create_table(self.table_name)
        created2 = self.tc.create_table(self.table_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_table_with_already_existing_table_fail_on_exist(self):
        # Arrange

        # Act
        created = self.tc.create_table(self.table_name)
        with self.assertRaises(WindowsAzureError):
            self.tc.create_table(self.table_name, True)

        # Assert
        self.assertTrue(created)

    def test_query_tables(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        tables = self.tc.query_tables()
        for table in tables:
            pass
        
        # Assert
        tableNames = [x.name for x in tables]
        self.assertGreaterEqual(len(tableNames), 1)
        self.assertGreaterEqual(len(tables), 1)
        self.assertIn(self.table_name, tableNames)

    def test_query_tables_with_table_name(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        tables = self.tc.query_tables(self.table_name)
        for table in tables:
            pass

        # Assert
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].name, self.table_name)

    def test_query_tables_with_table_name_no_tables(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.query_tables(self.table_name)

        # Assert

    def test_query_tables_with_top(self):
        # Arrange
        self.additional_table_names = [self.table_name + suffix for suffix in 'abcd'] 
        for name in self.additional_table_names:
            self.tc.create_table(name)

        # Act
        tables = self.tc.query_tables(None, 3)
        for table in tables:
            pass

        # Assert
        self.assertEqual(len(tables), 3)

    def test_query_tables_with_top_and_next_table_name(self):
        # Arrange
        self.additional_table_names = [self.table_name + suffix for suffix in 'abcd'] 
        for name in self.additional_table_names:
            self.tc.create_table(name)

        # Act
        tables_set1 = self.tc.query_tables(None, 3)
        tables_set2 = self.tc.query_tables(None, 3, tables_set1.x_ms_continuation['NextTableName'])

        # Assert
        self.assertEqual(len(tables_set1), 3)
        self.assertGreaterEqual(len(tables_set2), 1)
        self.assertLessEqual(len(tables_set2), 3)

    def test_delete_table_with_existing_table(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        deleted = self.tc.delete_table(self.table_name)

        # Assert
        self.assertTrue(deleted)
        tables = self.tc.query_tables()
        self.assertNamedItemNotInContainer(tables, self.table_name)

    def test_delete_table_with_existing_table_fail_not_exist(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        deleted = self.tc.delete_table(self.table_name, True)

        # Assert
        self.assertTrue(deleted)
        tables = self.tc.query_tables()
        self.assertNamedItemNotInContainer(tables, self.table_name)

    def test_delete_table_with_non_existing_table(self):
        # Arrange

        # Act
        deleted = self.tc.delete_table(self.table_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_table_with_non_existing_table_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.delete_table(self.table_name, True)

        # Assert

    #--Test cases for entities ------------------------------------------
    def test_insert_entity_dictionary(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        dict = self._create_default_entity_dict('MyPartition', '1')
        resp = self.tc.insert_entity(self.table_name, dict)

        # Assert
        self.assertIsNotNone(resp)

    def test_insert_entity_class_instance(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = self._create_default_entity_class('MyPartition', '1')
        resp = self.tc.insert_entity(self.table_name, entity)

        # Assert
        self.assertIsNotNone(resp)

    def test_insert_entity_conflict(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.insert_entity(self.table_name, self._create_default_entity_dict('MyPartition', '1'))

        # Assert

    def test_get_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.tc.get_entity(self.table_name, 'MyPartition', '1')

        # Assert
        self.assertEquals(resp.PartitionKey, 'MyPartition')
        self.assertEquals(resp.RowKey, '1')
        self._assert_default_entity(resp)

    def test_get_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.get_entity(self.table_name, 'MyPartition', '1')

        # Assert

    def test_get_entity_with_select(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.tc.get_entity(self.table_name, 'MyPartition', '1', 'age,sex')

        # Assert
        self.assertEquals(resp.age, 39)
        self.assertEquals(resp.sex, 'male')
        self.assertFalse(hasattr(resp, "birthday"))
        self.assertFalse(hasattr(resp, "married"))
        self.assertFalse(hasattr(resp, "deceased"))

    def test_query_entities(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)

        # Act
        resp = self.tc.query_entities(self.table_name)

        # Assert
        self.assertEquals(len(resp), 2)
        for entity in resp:
            self.assertEquals(entity.PartitionKey, 'MyPartition')
            self._assert_default_entity(entity)
        self.assertEquals(resp[0].RowKey, '1')
        self.assertEquals(resp[1].RowKey, '2')

    def test_query_entities_with_filter(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)
        self.tc.insert_entity(self.table_name, self._create_default_entity_dict('MyOtherPartition', '3'))

        # Act
        resp = self.tc.query_entities(self.table_name, "PartitionKey eq 'MyPartition'")

        # Assert
        self.assertEquals(len(resp), 2)
        for entity in resp:
            self.assertEquals(entity.PartitionKey, 'MyPartition')
            self._assert_default_entity(entity)

    def test_query_entities_with_select(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)

        # Act
        resp = self.tc.query_entities(self.table_name, None, 'age,sex')

        # Assert
        self.assertEquals(len(resp), 2)
        self.assertEquals(resp[0].age, 39)
        self.assertEquals(resp[0].sex, 'male')
        self.assertFalse(hasattr(resp[0], "birthday"))
        self.assertFalse(hasattr(resp[0], "married"))
        self.assertFalse(hasattr(resp[0], "deceased"))

    def test_query_entities_with_top(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 3)

        # Act
        resp = self.tc.query_entities(self.table_name, None, None, 2)

        # Assert
        self.assertEquals(len(resp), 2)

    def test_query_entities_with_top_and_next(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 5)

        # Act
        resp1 = self.tc.query_entities(self.table_name, None, None, 2)
        resp2 = self.tc.query_entities(self.table_name, None, None, 2, resp1.x_ms_continuation['NextPartitionKey'], resp1.x_ms_continuation['NextRowKey'])
        resp3 = self.tc.query_entities(self.table_name, None, None, 2, resp2.x_ms_continuation['NextPartitionKey'], resp2.x_ms_continuation['NextRowKey'])

        # Assert
        self.assertEquals(len(resp1), 2)
        self.assertEquals(len(resp2), 2)
        self.assertEquals(len(resp3), 1)
        self.assertEquals(resp1[0].RowKey, '1')
        self.assertEquals(resp1[1].RowKey, '2')
        self.assertEquals(resp2[0].RowKey, '3')
        self.assertEquals(resp2[1].RowKey, '4')
        self.assertEquals(resp3[0].RowKey, '5')

    def test_update_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.update_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_update_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.update_entity(self.table_name, 'MyPartition', '1', sent_entity, if_match=entities[0].etag)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_update_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        with self.assertRaises(WindowsAzureError):
            self.tc.update_entity(self.table_name, 'MyPartition', '1', sent_entity, if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    def test_insert_or_merge_entity_with_existing_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.insert_or_merge_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_insert_or_merge_entity_with_non_existing_entity(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.insert_or_merge_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_insert_or_replace_entity_with_existing_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.insert_or_replace_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_insert_or_replace_entity_with_non_existing_entity(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.insert_or_replace_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_merge_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.merge_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_merge_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        with self.assertRaises(WindowsAzureError):
            self.tc.merge_entity(self.table_name, 'MyPartition', '1', sent_entity)

        # Assert

    def test_merge_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        resp = self.tc.merge_entity(self.table_name, 'MyPartition', '1', sent_entity, if_match=entities[0].etag)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.tc.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_merge_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition','1')
        with self.assertRaises(WindowsAzureError):
            self.tc.merge_entity(self.table_name, 'MyPartition', '1', sent_entity, if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    def test_delete_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.tc.delete_entity(self.table_name, 'MyPartition', '1')

        # Assert
        self.assertIsNone(resp)
        with self.assertRaises(WindowsAzureError):
            self.tc.get_entity(self.table_name, 'MyPartition', '1')

    def test_delete_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.delete_entity(self.table_name, 'MyPartition', '1')

        # Assert

    def test_delete_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.tc.delete_entity(self.table_name, 'MyPartition', '1', if_match=entities[0].etag)

        # Assert
        self.assertIsNone(resp)
        with self.assertRaises(WindowsAzureError):
            self.tc.get_entity(self.table_name, 'MyPartition', '1')

    def test_delete_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.delete_entity(self.table_name, 'MyPartition', '1', if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    #--Test cases for batch ---------------------------------------------
    def test_with_filter_single(self):
        called = []

        def my_filter(request, next):
            called.append(True)
            return next(request)

        tc = self.tc.with_filter(my_filter)
        tc.create_table(self.table_name)

        self.assertTrue(called)

        del called[:]        
        
        tc.delete_table(self.table_name)

        self.assertTrue(called)
        del called[:]        

    def test_with_filter_chained(self):
        called = []

        def filter_a(request, next):
            called.append('a')
            return next(request)
        
        def filter_b(request, next):
            called.append('b')
            return next(request)

        tc = self.tc.with_filter(filter_a).with_filter(filter_b)
        tc.create_table(self.table_name)

        self.assertEqual(called, ['b', 'a'])

        tc.delete_table(self.table_name)

    def test_batch_insert(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()

        self.tc.begin_batch()
        self.tc.insert_entity(self.table_name, entity)
        self.tc.commit_batch()

        # Assert 
        result = self.tc.get_entity(self.table_name, '001', 'batch_insert')
        self.assertIsNotNone(result) 

    def test_batch_update(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_update'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.table_name, entity)

        entity = self.tc.get_entity(self.table_name, '001', 'batch_update')
        self.assertEqual(3, entity.test3)
        entity.test2 = 'value1'
        self.tc.begin_batch()
        self.tc.update_entity(self.table_name, '001', 'batch_update', entity)
        self.tc.commit_batch()
        entity = self.tc.get_entity(self.table_name, '001', 'batch_update')

        # Assert
        self.assertEqual('value1', entity.test2)

    def test_batch_merge(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_merge'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.table_name, entity)

        entity = self.tc.get_entity(self.table_name, '001', 'batch_merge')
        self.assertEqual(3, entity.test3)
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_merge'
        entity.test2 = 'value1'
        self.tc.begin_batch()
        self.tc.merge_entity(self.table_name, '001', 'batch_merge', entity)
        self.tc.commit_batch()
        entity = self.tc.get_entity(self.table_name, '001', 'batch_merge')

        # Assert
        self.assertEqual('value1', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_insert_replace(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert_replace'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.begin_batch()
        self.tc.insert_or_replace_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        entity = self.tc.get_entity(self.table_name, '001', 'batch_insert_replace')
        
        # Assert
        self.assertIsNotNone(entity)
        self.assertEqual('value', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_insert_merge(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert_merge'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.begin_batch()
        self.tc.insert_or_merge_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        entity = self.tc.get_entity(self.table_name, '001', 'batch_insert_merge')
        
        # Assert
        self.assertIsNotNone(entity)
        self.assertEqual('value', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_delete(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_delete'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.table_name, entity)

        entity = self.tc.get_entity(self.table_name, '001', 'batch_delete')
        #self.assertEqual(3, entity.test3)
        self.tc.begin_batch()
        self.tc.delete_entity(self.table_name, '001', 'batch_delete')
        self.tc.commit_batch()

    def test_batch_inserts(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = Entity()
        entity.PartitionKey = 'batch_inserts'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')

        self.tc.begin_batch()
        for i in range(100):
            entity.RowKey = str(i)
            self.tc.insert_entity(self.table_name, entity)
        self.tc.commit_batch()
        
        entities = self.tc.query_entities(self.table_name, "PartitionKey eq 'batch_inserts'", '')

        # Assert
        self.assertIsNotNone(entities);
        self.assertEqual(100, len(entities))

    def test_batch_all_operations_together(self):
        # Arrange
        self._create_table(self.table_name)

         # Act
        entity = Entity()
        entity.PartitionKey = '003'
        entity.RowKey = 'batch_all_operations_together-1'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-2'
        self.tc.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        self.tc.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        self.tc.insert_entity(self.table_name, entity)

        self.tc.begin_batch()
        entity.RowKey = 'batch_all_operations_together'
        self.tc.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-1'
        self.tc.delete_entity(self.table_name, entity.PartitionKey, entity.RowKey)
        entity.RowKey = 'batch_all_operations_together-2'
        entity.test3 = 10
        self.tc.update_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        entity.test3 = 100
        self.tc.merge_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        entity.test3 = 10
        self.tc.insert_or_replace_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-5'
        self.tc.insert_or_merge_entity(self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        # Assert
        entities = self.tc.query_entities(self.table_name, "PartitionKey eq '003'", '')
        self.assertEqual(5, len(entities))

    def test_batch_same_row_operations_fail(self):
        # Arrange
        self._create_table(self.table_name)
        entity = self._create_default_entity_dict('001', 'batch_negative_1')
        self.tc.insert_entity(self.table_name, entity)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.begin_batch()

            entity = self._create_updated_entity_dict('001', 'batch_negative_1')
            self.tc.update_entity(self.table_name, entity['PartitionKey'], entity['RowKey'], entity)

            entity = self._create_default_entity_dict('001', 'batch_negative_1')
            self.tc.merge_entity(self.table_name, entity['PartitionKey'], entity['RowKey'], entity)

        self.tc.cancel_batch()

        # Assert

    def test_batch_different_partition_operations_fail(self):
        # Arrange
        self._create_table(self.table_name)
        entity = self._create_default_entity_dict('001', 'batch_negative_1')
        self.tc.insert_entity(self.table_name, entity)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.begin_batch()

            entity = self._create_updated_entity_dict('001', 'batch_negative_1')
            self.tc.update_entity(self.table_name, entity['PartitionKey'], entity['RowKey'], entity)

            entity = self._create_default_entity_dict('002', 'batch_negative_1')
            self.tc.insert_entity(self.table_name, entity) 

        self.tc.cancel_batch()

        # Assert

    def test_batch_different_table_operations_fail(self):
        # Arrange
        other_table_name = self.table_name + 'other'
        self.additional_table_names = [other_table_name]
        self._create_table(self.table_name)
        self._create_table(other_table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.tc.begin_batch()

            entity = self._create_default_entity_dict('001', 'batch_negative_1')
            self.tc.insert_entity(self.table_name, entity) 

            entity = self._create_default_entity_dict('001', 'batch_negative_2')
            self.tc.insert_entity(other_table_name, entity) 

        self.tc.cancel_batch()

        # Assert

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
