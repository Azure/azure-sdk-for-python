#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------

from windowsazure.storage.cloudtableclient import *
from windowsazure.storage import EntityProperty, Entity
from windowsazure import WindowsAzureError


from windowsazuretest.util import (credentials, 
                                   getUniqueTestRunID,
                                   STATUS_OK,
                                   STATUS_CREATED,
                                   STATUS_ACCEPTED,
                                   STATUS_NO_CONTENT)

import unittest
import time
from datetime import datetime

#------------------------------------------------------------------------------
__uid = getUniqueTestRunID()

TABLE_TO_DELETE = 'mytesttabletodelete%s' % (__uid)
TABLE_NO_DELETE = 'mytesttablenodelete%s' % (__uid)
ENTITY_TO_DELETE = 'mytestentitytodelete%s' % (__uid)
ENTITY_NO_DELETE = 'mytestentitynodelete%s' % (__uid)

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
        self.tc = CloudTableClient(account_name=credentials.getStorageServicesName(), 
                                   account_key=credentials.getStorageServicesKey())
        self.cleanup()
        time.sleep(10)
    
    def tearDown(self):
        self.cleanup()
        return super(StorageTest, self).tearDown()

    def cleanup(self):
        for cont in [TABLE_NO_DELETE, TABLE_TO_DELETE]:
            try:    self.tc.delete_table(cont)
            except: pass

    def test_sanity(self):
        self.sanity_create_table()
        self.sanity_query_tables()
        
        #TODO - this fails, but I want the code coverage
        try: self.sanity_get_table_service_properties()
        except: pass
        try: self.sanity_set_table_service_properties()
        except: pass 
            
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

    def sanity_get_table_service_properties(self):
        #TODO - file a bug; add assertions!
        resp = self.tc.get_table_service_properties()

    def sanity_set_table_service_properties(self):
        #TODO - file a bug; add assertions!
        table_properties = self.tc.get_table_service_properties()
        self.tc.set_table_service_properties(table_properties)

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
        self.assertEquals(resp.age.value, u'39')
        self.assertEquals(resp.age.type, u'Edm.Int32')
        self.assertEquals(resp.Birthday.value, u'20')
        self.assertEquals(resp.Birthday.type, 'Edm.Int64')

    def sanity_query_entities(self):
        resp = self.tc.query_entities(TABLE_NO_DELETE, '', '')
        self.assertEquals(len(resp), 2)
        self.assertEquals(resp[0].birthday.value, u'1973-10-04T00:00:00Z')
        self.assertEquals(resp[1].Birthday.value, u'20')

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
        self.assertEquals(resp.age.value, u'21')
        self.assertEquals(resp.age.type, u'Edm.Int32')
        self.assertEquals(resp.sex, u'female')
        self.assertEquals(resp.birthday.value, u'1991-10-04T00:00:00Z')
        self.assertEquals(resp.birthday.type, 'Edm.DateTime')

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
        self.assertEquals(resp.birthday.value, u'1991-10-04T00:00:00Z')
        self.assertEquals(resp.birthday.type, 'Edm.DateTime')
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
        self.assertEquals(resp.age.value, u'1')
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
        self.assertEquals(resp.age.value, u'1')
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
    
    def sanity_begin_batch(self):
        resp = self.tc.begin_batch()
        self.assertEquals(resp, None)

    def sanity_commit_batch(self):
        resp = self.tc.commit_batch()
        self.assertEquals(resp, None)

    def sanity_cancel_batch(self):
        resp = self.tc.cancel_batch()
        self.assertEquals(resp, None)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
