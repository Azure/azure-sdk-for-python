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
                            getUniqueNameBasedOnCurrentTime)

import unittest
import time
from datetime import datetime

#------------------------------------------------------------------------------
__uid = getUniqueTestRunID()

TABLE_TO_DELETE = 'mytesttabletodelete%s' % (__uid)
TABLE_NO_DELETE = 'mytesttablenodelete%s' % (__uid)
ENTITY_TO_DELETE = 'mytestentitytodelete%s' % (__uid)
ENTITY_NO_DELETE = 'mytestentitynodelete%s' % (__uid)
BATCH_TABLE = 'mytestbatchtable%s' % (__uid)
FILTER_TABLE = 'mytestfiltertable%s' % (__uid)
#------------------------------------------------------------------------------
class StorageTest(unittest.TestCase):
    '''
    TODO:
    - comprehensive, positive test cases for all table client methods
    - comprehensive, negative test cases all table client methods
    - missing coverage for begin_batch
    - missing coverage for cancel_batch
    - missing coverage for commit_batch
    - get_table_service_properties busted
    - set_table_service_properties busted
    '''

    def setUp(self):
        self.tc = TableService(account_name=credentials.getStorageServicesName().encode('ascii', 'ignore'), 
                                   account_key=credentials.getStorageServicesKey().encode('ascii', 'ignore'))

        __uid = getUniqueTestRunID()
        test_table_base_name = u'testtable%s' % (__uid)
        self.test_table = getUniqueNameBasedOnCurrentTime(test_table_base_name)     
        self.tc.create_table(self.test_table)

        #time.sleep(10)
    
    def tearDown(self):
        self.cleanup()
        return super(StorageTest, self).tearDown()

    def cleanup(self):
        for cont in [TABLE_NO_DELETE, TABLE_TO_DELETE]:
            try:    self.tc.delete_table(cont)
            except: pass
        self.tc.delete_table(self.test_table)

    def test_sanity(self):
        self.sanity_create_table()
        time.sleep(10)
        self.sanity_query_tables()
        
        self.sanity_delete_table()
        
        self.sanity_insert_entity()
        self.sanity_get_entity()
        self.sanity_query_entities()
        self.sanity_update_entity()
        self.sanity_insert_or_merge_entity()
        self.sanity_insert_or_replace_entity()
        self.sanity_merge_entity()
        self.sanity_delete_entity()

        self.sanity_begin_batch()
        self.sanity_commit_batch()
        self.sanity_cancel_batch()

    def test_sanity_get_set_table_service_properties(self):
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

            table_properties = self.tc.get_table_service_properties()
            cur = table_properties
            for component in path.split('.'):
                cur = getattr(cur, component)

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


    #--Helpers-----------------------------------------------------------------
    def sanity_create_table(self):
        resp = self.tc.create_table(TABLE_TO_DELETE)
        self.assertTrue(resp)
        #self.assertEqual(resp.cache_control, u'no-cache')

        resp = self.tc.create_table(TABLE_NO_DELETE)
        self.assertTrue(resp)
        #self.assertEqual(resp.cache_control, u'no-cache')

    def sanity_query_tables(self):
        resp = self.tc.query_tables()
        self.assertEqual(type(resp), list)
        tableNames = [x.name for x in resp]
        self.assertGreaterEqual(len(tableNames), 2)
        self.assertIn(TABLE_NO_DELETE, tableNames)
        self.assertIn(TABLE_TO_DELETE, tableNames)

    def sanity_delete_table(self):
        resp = self.tc.delete_table(TABLE_TO_DELETE)
        self.assertTrue(resp)

    def sanity_insert_entity(self):
        resp = self.tc.insert_entity(TABLE_NO_DELETE, {'PartitionKey':'Lastname', 
                                                       'RowKey':'Firstname', 
                                                       'age':39, 
                                                       'sex':'male', 
                                                       'birthday':datetime(1973,10,04)})
        self.assertEquals(resp, None)

        entity = Entity()
        entity.PartitionKey = 'Lastname'
        entity.RowKey = 'Firstname1'
        entity.age = 39
        entity.Birthday = EntityProperty('Edm.Int64', 20)

        resp = self.tc.insert_entity(TABLE_NO_DELETE, entity)
        self.assertEquals(resp, None)

    def sanity_get_entity(self):
        ln = u'Lastname'
        fn1 = u'Firstname1'
        resp = self.tc.get_entity(TABLE_NO_DELETE, 
                                  ln, 
                                  fn1, 
                                  '')                
        self.assertEquals(resp.PartitionKey, ln)
        self.assertEquals(resp.RowKey, fn1)
        self.assertEquals(resp.age, 39)
        self.assertEquals(resp.Birthday, 20)

    def sanity_query_entities(self):
        resp = self.tc.query_entities(TABLE_NO_DELETE, '', '')
        self.assertEquals(len(resp), 2)
        self.assertEquals(resp[0].birthday, datetime(1973, 10, 04))
        self.assertEquals(resp[1].Birthday, 20)

    def sanity_update_entity(self):
        ln = u'Lastname'
        fn = u'Firstname'
        resp = self.tc.update_entity(TABLE_NO_DELETE, 
                                     ln, 
                                     fn, 
                                     {'PartitionKey':'Lastname', 
                                      'RowKey':'Firstname', 
                                      'age':21, 
                                      'sex':'female', 
                                      'birthday':datetime(1991,10,04)})
        self.assertEquals(resp, None)
        
        resp = self.tc.get_entity(TABLE_NO_DELETE, 
                                  ln, 
                                  fn, 
                                  '')
        self.assertEquals(resp.PartitionKey, ln)
        self.assertEquals(resp.RowKey, fn)
        self.assertEquals(resp.age, 21)
        self.assertEquals(resp.sex, u'female')
        self.assertEquals(resp.birthday, datetime(1991, 10, 04))
        
    def sanity_insert_or_merge_entity(self):
        ln = u'Lastname'
        fn = u'Firstname'
        resp = self.tc.insert_or_merge_entity(TABLE_NO_DELETE, 
                                              ln, 
                                              fn, 
                                              {'PartitionKey':'Lastname', 
                                               'RowKey':'Firstname', 
                                               'age': u'abc', #changed type 
                                               'sex':'male', #changed value
                                               'birthday':datetime(1991,10,04),
                                               'sign' : 'aquarius' #new
                                              })
        self.assertEquals(resp, None)
        
        resp = self.tc.get_entity(TABLE_NO_DELETE, 
                                  ln, 
                                  fn, 
                                  '')
        self.assertEquals(resp.PartitionKey, ln)
        self.assertEquals(resp.RowKey, fn)
        self.assertEquals(resp.age, u'abc')
        self.assertEquals(resp.sex, u'male')
        self.assertEquals(resp.birthday, datetime(1991, 10, 4))
        self.assertEquals(resp.sign, u'aquarius')

    def sanity_insert_or_replace_entity(self):
        ln = u'Lastname'
        fn = u'Firstname'
        resp = self.tc.insert_or_replace_entity(TABLE_NO_DELETE, 
                                                ln, 
                                                fn, 
                                                {'PartitionKey':'Lastname', 
                                                 'RowKey':'Firstname', 
                                                 'age':1, 
                                                 'sex':'male'})
        self.assertEquals(resp, None)

        resp = self.tc.get_entity(TABLE_NO_DELETE, 
                                  ln, 
                                  fn, 
                                  '')
        self.assertEquals(resp.PartitionKey, ln)
        self.assertEquals(resp.RowKey, fn)
        self.assertEquals(resp.age, 1)
        self.assertEquals(resp.sex, u'male')
        self.assertFalse(hasattr(resp, "birthday"))
        self.assertFalse(hasattr(resp, "sign"))

    def sanity_merge_entity(self):
        ln = u'Lastname'
        fn = u'Firstname'
        resp = self.tc.merge_entity(TABLE_NO_DELETE, 
                                    ln, 
                                    fn, 
                                    {'PartitionKey':'Lastname', 
                                     'RowKey':'Firstname', 
                                     'sex':'female', 
                                     'fact': 'nice person'})
        self.assertEquals(resp, None)

        resp = self.tc.get_entity(TABLE_NO_DELETE, 
                                  ln, 
                                  fn, 
                                  '')
        self.assertEquals(resp.PartitionKey, ln)
        self.assertEquals(resp.RowKey, fn)
        self.assertEquals(resp.age, 1)
        self.assertEquals(resp.sex, u'female')
        self.assertEquals(resp.fact, u'nice person')
        self.assertFalse(hasattr(resp, "birthday"))

    def sanity_delete_entity(self):
        ln = u'Lastname'
        fn = u'Firstname'
        resp = self.tc.delete_entity(TABLE_NO_DELETE, 
                                     ln, 
                                     fn)
        self.assertEquals(resp, None)

        self.assertRaises(WindowsAzureError,
                          lambda: self.tc.get_entity(TABLE_NO_DELETE, ln, fn, ''))
    
    def test_batch_partition_key(self):
        tn = BATCH_TABLE + 'pk'
        self.tc.create_table(tn)
        try:
            self.tc.begin_batch()
            self.tc.insert_entity(TABLE_NO_DELETE, {'PartitionKey':'Lastname', 
                                                       'RowKey':'Firstname', 
                                                       'age':39, 
                                                       'sex':'male', 
                                                       'birthday':datetime(1973,10,04)})

            self.tc.insert_entity(TABLE_NO_DELETE, {'PartitionKey':'Lastname', 
                                                       'RowKey':'Firstname2', 
                                                       'age':39, 
                                                       'sex':'male', 
                                                       'birthday':datetime(1973,10,04)})

            self.tc.commit_batch()
        finally:
            self.tc.delete_table(tn)

    def test_sanity_batch(self):
        return
        self.tc.create_table(BATCH_TABLE)

        #resp = self.tc.begin_batch()
        #self.assertEquals(resp, None)

        resp = self.tc.insert_entity(BATCH_TABLE, {'PartitionKey':'Lastname', 
                                                       'RowKey':'Firstname', 
                                                       'age':39, 
                                                       'sex':'male', 
                                                       'birthday':datetime(1973,10,04)})

        #resp = self.tc.insert_entity(BATCH_TABLE, {'PartitionKey':'Lastname', 
        #                                               'RowKey':'Firstname2', 
        #                                               'age':35, 
        #                                               'sex':'female', 
        #                                               'birthday':datetime(1977,12,5)})
        #
        resp = self.tc.query_entities(BATCH_TABLE, '', '')
        self.assertEquals(len(resp), 0)

        #self.tc.commit_batch()
        return
        resp = self.tc.query_entities(BATCH_TABLE, '', '')
        self.assertEquals(len(resp), 2)

        self.tc.delete_table(BATCH_TABLE)
        
    def sanity_begin_batch(self):
        resp = self.tc.begin_batch()
        self.assertEquals(resp, None)

    def sanity_commit_batch(self):
        resp = self.tc.commit_batch()
        self.assertEquals(resp, None)

    def sanity_cancel_batch(self):
        resp = self.tc.cancel_batch()
        self.assertEquals(resp, None)

    def test_query_tables_top(self):
        table_id = getUniqueTestRunID()
        for i in xrange(20):
            self.tc.create_table(table_id + str(i))

        res = self.tc.query_tables(top = 5)
        self.assertEqual(len(res), 5)

    def test_with_filter(self):
        # Single filter
        called = []
        def my_filter(request, next):
            called.append(True)
            return next(request)

        tc = self.tc.with_filter(my_filter)
        tc.create_table(FILTER_TABLE)

        self.assertTrue(called)

        del called[:]        
        
        tc.delete_table(FILTER_TABLE)

        self.assertTrue(called)
        del called[:]        

        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)
        
        def filter_b(request, next):
            called.append('b')
            return next(request)

        tc = self.tc.with_filter(filter_a).with_filter(filter_b)
        tc.create_table(FILTER_TABLE + '0')

        self.assertEqual(called, ['b', 'a'])

        tc.delete_table(FILTER_TABLE + '0')

    def test_batch_insert(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()

        self.tc.begin_batch()
        self.tc.insert_entity(self.test_table, entity)
        self.tc.commit_batch()

        #Assert 
        result = self.tc.get_entity(self.test_table, '001', 'batch_insert')
        self.assertIsNotNone(result) 

    def test_batch_update(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_update'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.test_table, entity)

        entity = self.tc.get_entity(self.test_table, '001', 'batch_update')
        self.assertEqual(3, entity.test3)
        entity.test2 = 'value1'
        self.tc.begin_batch()
        self.tc.update_entity(self.test_table, '001', 'batch_update', entity)
        self.tc.commit_batch()
        entity = self.tc.get_entity(self.test_table, '001', 'batch_update')

        #Assert
        self.assertEqual('value1', entity.test2)

    def test_batch_merge(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_merge'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.test_table, entity)

        entity = self.tc.get_entity(self.test_table, '001', 'batch_merge')
        self.assertEqual(3, entity.test3)
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_merge'
        entity.test2 = 'value1'
        self.tc.begin_batch()
        self.tc.merge_entity(self.test_table, '001', 'batch_merge', entity)
        self.tc.commit_batch()
        entity = self.tc.get_entity(self.test_table, '001', 'batch_merge')

        #Assert
        self.assertEqual('value1', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_insert_replace(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert_replace'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.begin_batch()
        self.tc.insert_or_replace_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        entity = self.tc.get_entity(self.test_table, '001', 'batch_insert_replace')
        
        #Assert
        self.assertIsNotNone(entity)
        self.assertEqual('value', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_insert_merge(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_insert_merge'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.begin_batch()
        self.tc.insert_or_merge_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        entity = self.tc.get_entity(self.test_table, '001', 'batch_insert_merge')
        
        #Assert
        self.assertIsNotNone(entity)
        self.assertEqual('value', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_delete(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_delete'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.test_table, entity)

        entity = self.tc.get_entity(self.test_table, '001', 'batch_delete')
        #self.assertEqual(3, entity.test3)
        self.tc.begin_batch()
        self.tc.delete_entity(self.test_table, '001', 'batch_delete')
        self.tc.commit_batch()

    def test_batch_inserts(self):
        #Act
        entity = Entity()
        entity.PartitionKey = 'batch_inserts'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')

        self.tc.begin_batch()
        for i in range(100):
            entity.RowKey = str(i)
            self.tc.insert_entity(self.test_table, entity)
        self.tc.commit_batch()
        
        entities = self.tc.query_entities(self.test_table, "PartitionKey eq 'batch_inserts'", '')

        #Assert
        self.assertIsNotNone(entities);
        self.assertEqual(100, len(entities))

    def test_batch_all_operations_together(self):
         #Act
        entity = Entity()
        entity.PartitionKey = '003'
        entity.RowKey = 'batch_all_operations_together-1'
        entity.test = EntityProperty('Edm.Boolean', 'true')
        entity.test2 = 'value'
        entity.test3 = 3
        entity.test4 = EntityProperty('Edm.Int64', '1234567890')
        entity.test5 = datetime.utcnow()
        self.tc.insert_entity(self.test_table, entity)
        entity.RowKey = 'batch_all_operations_together-2'
        self.tc.insert_entity(self.test_table, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        self.tc.insert_entity(self.test_table, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        self.tc.insert_entity(self.test_table, entity)

        self.tc.begin_batch()
        entity.RowKey = 'batch_all_operations_together'
        self.tc.insert_entity(self.test_table, entity)
        entity.RowKey = 'batch_all_operations_together-1'
        self.tc.delete_entity(self.test_table, entity.PartitionKey, entity.RowKey)
        entity.RowKey = 'batch_all_operations_together-2'
        entity.test3 = 10
        self.tc.update_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        entity.test3 = 100
        self.tc.merge_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        entity.test3 = 10
        self.tc.insert_or_replace_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-5'
        self.tc.insert_or_merge_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
        self.tc.commit_batch()

        #Assert
        entities = self.tc.query_entities(self.test_table, "PartitionKey eq '003'", '')
        self.assertEqual(5, len(entities))

    def test_batch_negative(self):
        #Act
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_negative_1'
        entity.test = 1

        self.tc.insert_entity(self.test_table, entity)
        entity.test = 2
        entity.RowKey = 'batch_negative_2'
        self.tc.insert_entity(self.test_table, entity)
        entity.test = 3
        entity.RowKey = 'batch_negative_3'
        self.tc.insert_entity(self.test_table, entity)
        entity.test = -2
        self.tc.update_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)

        try:        
            self.tc.begin_batch()
            entity.RowKey = 'batch_negative_1'
            self.tc.update_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
            self.tc.merge_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
            self.fail('Should raise WindowsAzueError exception')
            self.tc.commit_batch()            
        except:
            self.tc.cancel_batch()
            pass
        

        try:        
            self.tc.begin_batch()
            entity.PartitionKey = '001'
            entity.RowKey = 'batch_negative_1'
            self.tc.update_entity(self.test_table, entity.PartitionKey, entity.RowKey, entity)
            entity.PartitionKey = '002'
            entity.RowKey = 'batch_negative_1'
            self.tc.insert_entity(self.test_table, entity) 
            self.fail('Should raise WindowsAzueError exception')
            self.tc.commit_batch()
        except:
            self.tc.cancel_batch()
            pass
        

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
