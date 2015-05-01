# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
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
import base64
import time
import unittest

from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzoffset
from azure import (
    WindowsAzureError,
    WindowsAzureBatchOperationError,
    WindowsAzureMissingResourceError,
)
from azure.storage import (
    AccessPolicy,
    Entity,
    EntityProperty,
    SignedIdentifier,
    SignedIdentifiers,
    StorageServiceProperties,
    TableService,
    TableSharedAccessPermissions,
)
from azure.storage.sharedaccesssignature import SharedAccessPolicy
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
)

#------------------------------------------------------------------------------

MAX_RETRY = 60
#------------------------------------------------------------------------------


class TableServiceTest(AzureTestCase):

    def setUp(self):
        self.ts = TableService(credentials.getStorageServicesName(),
                               credentials.getStorageServicesKey())
        set_service_options(self.ts)

        self.table_name = getUniqueName('uttable')
        self.additional_table_names = []

    def tearDown(self):
        self.cleanup()
        return super(TableServiceTest, self).tearDown()

    def cleanup(self):
        try:
            self.ts.delete_table(self.table_name)
        except:
            pass

        for name in self.additional_table_names:
            try:
                self.ts.delete_table(name)
            except:
                pass

    #--Helpers-----------------------------------------------------------------
    def _create_table(self, table_name):
        '''
        Creates a table with the specified name.
        '''
        self.ts.create_table(table_name, True)

    def _create_table_with_default_entities(self, table_name, entity_count):
        '''
        Creates a table with the specified name and adds entities with the
        default set of values. PartitionKey is set to 'MyPartition' and RowKey
        is set to a unique counter value starting at 1 (as a string).
        '''
        entities = []
        self._create_table(table_name)
        for i in range(1, entity_count + 1):
            entities.append(self.ts.insert_entity(
                table_name,
                self._create_default_entity_dict('MyPartition', str(i))))
        return entities

    def _create_default_entity_class(self, partition, row):
        '''
        Creates a class-based entity with fixed values, using all
        of the supported data types.
        '''
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
        entity.Birthday = datetime(1973, 10, 4)
        entity.birthday = datetime(1970, 10, 4)
        entity.binary = None
        entity.other = EntityProperty('Edm.Int64', 20)
        entity.clsid = EntityProperty(
            'Edm.Guid', 'c9da6455-213d-42c9-9a79-3e9149a57833')
        return entity

    def _create_default_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        '''
        return {'PartitionKey': partition,
                'RowKey': row,
                'age': 39,
                'sex': 'male',
                'married': True,
                'deceased': False,
                'optional': None,
                'ratio': 3.1,
                'large': 9333111000,
                'Birthday': datetime(1973, 10, 4),
                'birthday': datetime(1970, 10, 4),
                'other': EntityProperty('Edm.Int64', 20),
                'clsid': EntityProperty(
                    'Edm.Guid',
                    'c9da6455-213d-42c9-9a79-3e9149a57833')}

    def _create_updated_entity_dict(self, partition, row):
        '''
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        '''
        return {'PartitionKey': partition,
                'RowKey': row,
                'age': 'abc',
                'sex': 'female',
                'sign': 'aquarius',
                'birthday': datetime(1991, 10, 4)}

    def _assert_default_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEqual(entity.age, 39)
        self.assertEqual(entity.sex, 'male')
        self.assertEqual(entity.married, True)
        self.assertEqual(entity.deceased, False)
        self.assertFalse(hasattr(entity, "aquarius"))
        self.assertEqual(entity.ratio, 3.1)
        self.assertEqual(entity.large, 9333111000)
        self.assertEqual(entity.Birthday, datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity.birthday, datetime(1970, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity.other, 20)
        self.assertIsInstance(entity.clsid, EntityProperty)
        self.assertEqual(entity.clsid.type, 'Edm.Guid')
        self.assertEqual(entity.clsid.value,
                         'c9da6455-213d-42c9-9a79-3e9149a57833')
        self.assertTrue(hasattr(entity, "Timestamp"))

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
        self.assertFalse(hasattr(entity, "large"))
        self.assertFalse(hasattr(entity, "Birthday"))
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertFalse(hasattr(entity, "other"))
        self.assertFalse(hasattr(entity, "clsid"))
        self.assertTrue(hasattr(entity, "Timestamp"))

    def _assert_merged_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity
        merged with the updated entity.
        '''
        self.assertEqual(entity.age, 'abc')
        self.assertEqual(entity.sex, 'female')
        self.assertEqual(entity.sign, 'aquarius')
        self.assertEqual(entity.married, True)
        self.assertEqual(entity.deceased, False)
        self.assertEqual(entity.sign, 'aquarius')
        self.assertEqual(entity.ratio, 3.1)
        self.assertEqual(entity.large, 9333111000)
        self.assertEqual(entity.Birthday, datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity.other, 20)
        self.assertIsInstance(entity.clsid, EntityProperty)
        self.assertEqual(entity.clsid.type, 'Edm.Guid')
        self.assertEqual(entity.clsid.value,
                         'c9da6455-213d-42c9-9a79-3e9149a57833')
        self.assertTrue(hasattr(entity, "Timestamp"))

    def _get_shared_access_policy(self, permission):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.utcnow() - timedelta(minutes=1)
        expiry = start + timedelta(hours=1)
        return SharedAccessPolicy(
            AccessPolicy(
                start.strftime(date_format),
                expiry.strftime(date_format),
                permission
            )
        )

    #--Test cases for table service -------------------------------------------
    def test_get_set_table_service_properties(self):
        table_properties = self.ts.get_table_service_properties()
        self.ts.set_table_service_properties(table_properties)

        tests = [('logging.delete', True),
                 ('logging.delete', False),
                 ('logging.read', True),
                 ('logging.read', False),
                 ('logging.write', True),
                 ('logging.write', False),
                 ]
        for path, value in tests:
            # print path
            cur = table_properties
            for component in path.split('.')[:-1]:
                cur = getattr(cur, component)

            last_attr = path.split('.')[-1]
            setattr(cur, last_attr, value)
            self.ts.set_table_service_properties(table_properties)

            retry_count = 0
            while retry_count < MAX_RETRY:
                table_properties = self.ts.get_table_service_properties()
                cur = table_properties
                for component in path.split('.'):
                    cur = getattr(cur, component)
                if value == cur:
                    break
                time.sleep(1)
                retry_count += 1

            self.assertEqual(value, cur)

    def test_table_service_retention_single_set(self):
        table_properties = self.ts.get_table_service_properties()
        table_properties.logging.retention_policy.enabled = False
        table_properties.logging.retention_policy.days = 5

        # TODO: Better error, ValueError?
        self.assertRaises(WindowsAzureError,
                          self.ts.set_table_service_properties,
                          table_properties)

        table_properties = self.ts.get_table_service_properties()
        table_properties.logging.retention_policy.days = None
        table_properties.logging.retention_policy.enabled = True

        # TODO: Better error, ValueError?
        self.assertRaises(WindowsAzureError,
                          self.ts.set_table_service_properties,
                          table_properties)

    def test_table_service_set_both(self):
        table_properties = self.ts.get_table_service_properties()
        table_properties.logging.retention_policy.enabled = True
        table_properties.logging.retention_policy.days = 5
        self.ts.set_table_service_properties(table_properties)
        table_properties = self.ts.get_table_service_properties()
        self.assertEqual(
            True, table_properties.logging.retention_policy.enabled)

        self.assertEqual(5, table_properties.logging.retention_policy.days)

    #--Test cases for tables --------------------------------------------------
    def test_create_table(self):
        # Arrange

        # Act
        created = self.ts.create_table(self.table_name)

        # Assert
        self.assertTrue(created)

    def test_create_table_fail_on_exist(self):
        # Arrange

        # Act
        created = self.ts.create_table(self.table_name, True)

        # Assert
        self.assertTrue(created)

    def test_create_table_with_already_existing_table(self):
        # Arrange

        # Act
        created1 = self.ts.create_table(self.table_name)
        created2 = self.ts.create_table(self.table_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_table_with_already_existing_table_fail_on_exist(self):
        # Arrange

        # Act
        created = self.ts.create_table(self.table_name)
        with self.assertRaises(WindowsAzureError):
            self.ts.create_table(self.table_name, True)

        # Assert
        self.assertTrue(created)

    def test_query_tables(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        tables = self.ts.query_tables()
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
        tables = self.ts.query_tables(self.table_name)
        for table in tables:
            pass

        # Assert
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].name, self.table_name)

    def test_query_tables_with_table_name_no_tables(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.query_tables(self.table_name)

        # Assert

    def test_query_tables_with_top(self):
        # Arrange
        self.additional_table_names = [
            self.table_name + suffix for suffix in 'abcd']
        for name in self.additional_table_names:
            self.ts.create_table(name)

        # Act
        tables = self.ts.query_tables(None, 3)
        for table in tables:
            pass

        # Assert
        self.assertEqual(len(tables), 3)

    def test_query_tables_with_top_and_next_table_name(self):
        # Arrange
        self.additional_table_names = [
            self.table_name + suffix for suffix in 'abcd']
        for name in self.additional_table_names:
            self.ts.create_table(name)

        # Act
        tables_set1 = self.ts.query_tables(None, 3)
        tables_set2 = self.ts.query_tables(
            None, 3, tables_set1.x_ms_continuation['NextTableName'])

        # Assert
        self.assertEqual(len(tables_set1), 3)
        self.assertGreaterEqual(len(tables_set2), 1)
        self.assertLessEqual(len(tables_set2), 3)

    def test_delete_table_with_existing_table(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        deleted = self.ts.delete_table(self.table_name)

        # Assert
        self.assertTrue(deleted)
        tables = self.ts.query_tables()
        self.assertNamedItemNotInContainer(tables, self.table_name)

    def test_delete_table_with_existing_table_fail_not_exist(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        deleted = self.ts.delete_table(self.table_name, True)

        # Assert
        self.assertTrue(deleted)
        tables = self.ts.query_tables()
        self.assertNamedItemNotInContainer(tables, self.table_name)

    def test_delete_table_with_non_existing_table(self):
        # Arrange

        # Act
        deleted = self.ts.delete_table(self.table_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_table_with_non_existing_table_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.delete_table(self.table_name, True)

        # Assert

    #--Test cases for entities ------------------------------------------
    def test_insert_entity_dictionary(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        dict = self._create_default_entity_dict('MyPartition', '1')
        resp = self.ts.insert_entity(self.table_name, dict)

        # Assert
        self.assertIsNotNone(resp)

    def test_insert_entity_class_instance(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        entity = self._create_default_entity_class('MyPartition', '1')
        resp = self.ts.insert_entity(self.table_name, entity)

        # Assert
        self.assertIsNotNone(resp)

    def test_insert_entity_conflict(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.insert_entity(
                self.table_name,
                self._create_default_entity_dict('MyPartition', '1'))

        # Assert

    def test_get_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.ts.get_entity(self.table_name, 'MyPartition', '1')

        # Assert
        self.assertEqual(resp.PartitionKey, 'MyPartition')
        self.assertEqual(resp.RowKey, '1')
        self._assert_default_entity(resp)

    def test_get_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.get_entity(self.table_name, 'MyPartition', '1')

        # Assert

    def test_get_entity_with_select(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.ts.get_entity(
            self.table_name, 'MyPartition', '1', 'age,sex')

        # Assert
        self.assertEqual(resp.age, 39)
        self.assertEqual(resp.sex, 'male')
        self.assertFalse(hasattr(resp, "birthday"))
        self.assertFalse(hasattr(resp, "married"))
        self.assertFalse(hasattr(resp, "deceased"))

    def test_query_entities(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)

        # Act
        resp = self.ts.query_entities(self.table_name)

        # Assert
        self.assertEqual(len(resp), 2)
        for entity in resp:
            self.assertEqual(entity.PartitionKey, 'MyPartition')
            self._assert_default_entity(entity)
        self.assertEqual(resp[0].RowKey, '1')
        self.assertEqual(resp[1].RowKey, '2')

    def test_query_entities_large(self):
        # Arrange
        self._create_table(self.table_name)
        total_entities_count = 1000
        entities_per_batch = 50

        for j in range(total_entities_count // entities_per_batch):
            self.ts.begin_batch()
            for i in range(entities_per_batch):
                entity = Entity()
                entity.PartitionKey = 'large'
                entity.RowKey = 'batch{0}-item{1}'.format(j, i)
                entity.test = EntityProperty('Edm.Boolean', 'true')
                entity.test2 = 'hello world;' * 100
                entity.test3 = 3
                entity.test4 = EntityProperty('Edm.Int64', '1234567890')
                entity.test5 = datetime.utcnow()
                self.ts.insert_entity(self.table_name, entity)
            self.ts.commit_batch()

        # Act
        start_time = datetime.now()
        resp = self.ts.query_entities(self.table_name)
        elapsed_time = datetime.now() - start_time

        # Assert
        print('query_entities took {0} secs.'.format(elapsed_time.total_seconds()))
        # azure allocates 5 seconds to execute a query
        # if it runs slowly, it will return fewer results and make the test fail
        self.assertEqual(len(resp), total_entities_count)

    def test_query_entities_with_filter(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)
        self.ts.insert_entity(
            self.table_name,
            self._create_default_entity_dict('MyOtherPartition', '3'))

        # Act
        resp = self.ts.query_entities(
            self.table_name, "PartitionKey eq 'MyPartition'")

        # Assert
        self.assertEqual(len(resp), 2)
        for entity in resp:
            self.assertEqual(entity.PartitionKey, 'MyPartition')
            self._assert_default_entity(entity)

    def test_query_entities_with_select(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)

        # Act
        resp = self.ts.query_entities(self.table_name, None, 'age,sex')

        # Assert
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0].age, 39)
        self.assertEqual(resp[0].sex, 'male')
        self.assertFalse(hasattr(resp[0], "birthday"))
        self.assertFalse(hasattr(resp[0], "married"))
        self.assertFalse(hasattr(resp[0], "deceased"))

    def test_query_entities_with_top(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 3)

        # Act
        resp = self.ts.query_entities(self.table_name, None, None, 2)

        # Assert
        self.assertEqual(len(resp), 2)

    def test_query_entities_with_top_and_next(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 5)

        # Act
        resp1 = self.ts.query_entities(self.table_name, None, None, 2)
        resp2 = self.ts.query_entities(
            self.table_name, None, None, 2,
            resp1.x_ms_continuation['NextPartitionKey'],
            resp1.x_ms_continuation['NextRowKey'])
        resp3 = self.ts.query_entities(
            self.table_name, None, None, 2,
            resp2.x_ms_continuation['NextPartitionKey'],
            resp2.x_ms_continuation['NextRowKey'])

        # Assert
        self.assertEqual(len(resp1), 2)
        self.assertEqual(len(resp2), 2)
        self.assertEqual(len(resp3), 1)
        self.assertEqual(resp1[0].RowKey, '1')
        self.assertEqual(resp1[1].RowKey, '2')
        self.assertEqual(resp2[0].RowKey, '3')
        self.assertEqual(resp2[1].RowKey, '4')
        self.assertEqual(resp3[0].RowKey, '5')

    def test_update_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.update_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_update_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.update_entity(
            self.table_name,
            'MyPartition', '1', sent_entity, if_match=entities[0].etag)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_update_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        with self.assertRaises(WindowsAzureError):
            self.ts.update_entity(
                self.table_name, 'MyPartition', '1', sent_entity,
                if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    def test_insert_or_merge_entity_with_existing_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.insert_or_merge_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_insert_or_merge_entity_with_non_existing_entity(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.insert_or_merge_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_insert_or_replace_entity_with_existing_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.insert_or_replace_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_insert_or_replace_entity_with_non_existing_entity(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.insert_or_replace_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_merge_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.merge_entity(
            self.table_name, 'MyPartition', '1', sent_entity)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_merge_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        with self.assertRaises(WindowsAzureError):
            self.ts.merge_entity(
                self.table_name, 'MyPartition', '1', sent_entity)

        # Assert

    def test_merge_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = self.ts.merge_entity(
            self.table_name, 'MyPartition', '1',
            sent_entity, if_match=entities[0].etag)

        # Assert
        self.assertIsNotNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_merged_entity(received_entity)

    def test_merge_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        with self.assertRaises(WindowsAzureError):
            self.ts.merge_entity(
                self.table_name, 'MyPartition', '1', sent_entity,
                if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    def test_delete_entity(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.ts.delete_entity(self.table_name, 'MyPartition', '1')

        # Assert
        self.assertIsNone(resp)
        with self.assertRaises(WindowsAzureError):
            self.ts.get_entity(self.table_name, 'MyPartition', '1')

    def test_delete_entity_not_existing(self):
        # Arrange
        self._create_table(self.table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.delete_entity(self.table_name, 'MyPartition', '1')

        # Assert

    def test_delete_entity_with_if_matches(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.ts.delete_entity(
            self.table_name, 'MyPartition', '1', if_match=entities[0].etag)

        # Assert
        self.assertIsNone(resp)
        with self.assertRaises(WindowsAzureError):
            self.ts.get_entity(self.table_name, 'MyPartition', '1')

    def test_delete_entity_with_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.delete_entity(
                self.table_name, 'MyPartition', '1',
                if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')

        # Assert

    #--Test cases for batch ---------------------------------------------
    def test_with_filter_single(self):
        called = []

        def my_filter(request, next):
            called.append(True)
            return next(request)

        tc = self.ts.with_filter(my_filter)
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

        tc = self.ts.with_filter(filter_a).with_filter(filter_b)
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

        self.ts.begin_batch()
        self.ts.insert_entity(self.table_name, entity)
        self.ts.commit_batch()

        # Assert
        result = self.ts.get_entity(self.table_name, '001', 'batch_insert')
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
        self.ts.insert_entity(self.table_name, entity)

        entity = self.ts.get_entity(self.table_name, '001', 'batch_update')
        self.assertEqual(3, entity.test3)
        entity.test2 = 'value1'
        self.ts.begin_batch()
        self.ts.update_entity(self.table_name, '001', 'batch_update', entity)
        self.ts.commit_batch()
        entity = self.ts.get_entity(self.table_name, '001', 'batch_update')

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
        self.ts.insert_entity(self.table_name, entity)

        entity = self.ts.get_entity(self.table_name, '001', 'batch_merge')
        self.assertEqual(3, entity.test3)
        entity = Entity()
        entity.PartitionKey = '001'
        entity.RowKey = 'batch_merge'
        entity.test2 = 'value1'
        self.ts.begin_batch()
        self.ts.merge_entity(self.table_name, '001', 'batch_merge', entity)
        self.ts.commit_batch()
        entity = self.ts.get_entity(self.table_name, '001', 'batch_merge')

        # Assert
        self.assertEqual('value1', entity.test2)
        self.assertEqual(1234567890, entity.test4)

    def test_batch_update_if_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 1)

        # Act
        sent_entity = self._create_updated_entity_dict('MyPartition', '1')
        self.ts.begin_batch()
        resp = self.ts.update_entity(
            self.table_name,
            'MyPartition', '1', sent_entity, if_match=entities[0].etag)
        self.ts.commit_batch()

        # Assert
        self.assertIsNone(resp)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_batch_update_if_doesnt_match(self):
        # Arrange
        entities = self._create_table_with_default_entities(self.table_name, 2)

        # Act
        sent_entity1 = self._create_updated_entity_dict('MyPartition', '1')
        sent_entity2 = self._create_updated_entity_dict('MyPartition', '2')
        self.ts.begin_batch()
        self.ts.update_entity(
            self.table_name, 'MyPartition', '1', sent_entity1,
            if_match=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"')
        self.ts.update_entity(
            self.table_name, 'MyPartition', '2', sent_entity2)
        try:
            self.ts.commit_batch()
        except WindowsAzureBatchOperationError as error:
            self.assertEqual(error.code, 'UpdateConditionNotSatisfied')
            self.assertTrue(str(error).startswith('0:The update condition specified in the request was not satisfied.'))
        else:
            self.fail('WindowsAzureBatchOperationError was expected')

        # Assert
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '1')
        self._assert_default_entity(received_entity)
        received_entity = self.ts.get_entity(
            self.table_name, 'MyPartition', '2')
        self._assert_default_entity(received_entity)

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
        self.ts.begin_batch()
        self.ts.insert_or_replace_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.ts.commit_batch()

        entity = self.ts.get_entity(
            self.table_name, '001', 'batch_insert_replace')

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
        self.ts.begin_batch()
        self.ts.insert_or_merge_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.ts.commit_batch()

        entity = self.ts.get_entity(
            self.table_name, '001', 'batch_insert_merge')

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
        self.ts.insert_entity(self.table_name, entity)

        entity = self.ts.get_entity(self.table_name, '001', 'batch_delete')
        #self.assertEqual(3, entity.test3)
        self.ts.begin_batch()
        self.ts.delete_entity(self.table_name, '001', 'batch_delete')
        self.ts.commit_batch()

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

        self.ts.begin_batch()
        for i in range(100):
            entity.RowKey = str(i)
            self.ts.insert_entity(self.table_name, entity)
        self.ts.commit_batch()

        entities = self.ts.query_entities(
            self.table_name, "PartitionKey eq 'batch_inserts'", '')

        # Assert
        self.assertIsNotNone(entities)
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
        self.ts.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-2'
        self.ts.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        self.ts.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        self.ts.insert_entity(self.table_name, entity)

        self.ts.begin_batch()
        entity.RowKey = 'batch_all_operations_together'
        self.ts.insert_entity(self.table_name, entity)
        entity.RowKey = 'batch_all_operations_together-1'
        self.ts.delete_entity(
            self.table_name, entity.PartitionKey, entity.RowKey)
        entity.RowKey = 'batch_all_operations_together-2'
        entity.test3 = 10
        self.ts.update_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-3'
        entity.test3 = 100
        self.ts.merge_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-4'
        entity.test3 = 10
        self.ts.insert_or_replace_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        entity.RowKey = 'batch_all_operations_together-5'
        self.ts.insert_or_merge_entity(
            self.table_name, entity.PartitionKey, entity.RowKey, entity)
        self.ts.commit_batch()

        # Assert
        entities = self.ts.query_entities(
            self.table_name, "PartitionKey eq '003'", '')
        self.assertEqual(5, len(entities))

    def test_batch_same_row_operations_fail(self):
        # Arrange
        self._create_table(self.table_name)
        entity = self._create_default_entity_dict('001', 'batch_negative_1')
        self.ts.insert_entity(self.table_name, entity)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.begin_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            self.ts.update_entity(
                self.table_name,
                entity['PartitionKey'],
                entity['RowKey'], entity)

            entity = self._create_default_entity_dict(
                '001', 'batch_negative_1')
            self.ts.merge_entity(
                self.table_name,
                entity['PartitionKey'],
                entity['RowKey'], entity)

        self.ts.cancel_batch()

        # Assert

    def test_batch_different_partition_operations_fail(self):
        # Arrange
        self._create_table(self.table_name)
        entity = self._create_default_entity_dict('001', 'batch_negative_1')
        self.ts.insert_entity(self.table_name, entity)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.begin_batch()

            entity = self._create_updated_entity_dict(
                '001', 'batch_negative_1')
            self.ts.update_entity(
                self.table_name, entity['PartitionKey'], entity['RowKey'],
                entity)

            entity = self._create_default_entity_dict(
                '002', 'batch_negative_1')
            self.ts.insert_entity(self.table_name, entity)

        self.ts.cancel_batch()

        # Assert

    def test_batch_different_table_operations_fail(self):
        # Arrange
        other_table_name = self.table_name + 'other'
        self.additional_table_names = [other_table_name]
        self._create_table(self.table_name)
        self._create_table(other_table_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.begin_batch()

            entity = self._create_default_entity_dict(
                '001', 'batch_negative_1')
            self.ts.insert_entity(self.table_name, entity)

            entity = self._create_default_entity_dict(
                '001', 'batch_negative_2')
            self.ts.insert_entity(other_table_name, entity)

        self.ts.cancel_batch()

    def test_unicode_property_value(self):
        ''' regression test for github issue #57'''
        # Act
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {'PartitionKey': 'test', 'RowKey': 'test1', 'Description': u'ꀕ'})
        self.ts.insert_entity(
            self.table_name,
            {'PartitionKey': 'test', 'RowKey': 'test2', 'Description': 'ꀕ'})
        resp = self.ts.query_entities(
            self.table_name, "PartitionKey eq 'test'")
        # Assert
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0].Description, u'ꀕ')
        self.assertEqual(resp[1].Description, u'ꀕ')

    def test_unicode_property_name(self):
        # Act
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {'PartitionKey': 'test', 'RowKey': 'test1', u'啊齄丂狛狜': u'ꀕ'})
        self.ts.insert_entity(
            self.table_name,
            {'PartitionKey': 'test', 'RowKey': 'test2', u'啊齄丂狛狜': 'hello'})
        resp = self.ts.query_entities(
            self.table_name, "PartitionKey eq 'test'")
        # Assert
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0].__dict__[u'啊齄丂狛狜'], u'ꀕ')
        self.assertEqual(resp[1].__dict__[u'啊齄丂狛狜'], u'hello')

    def test_unicode_create_table_unicode_name(self):
        # Arrange
        self.table_name = self.table_name + u'啊齄丂狛狜'

        # Act
        with self.assertRaises(WindowsAzureError):
            # not supported - table name must be alphanumeric, lowercase
            self.ts.create_table(self.table_name)

        # Assert

    def test_empty_and_spaces_property_value(self):
        # Act
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'EmptyByte': '',
                'EmptyUnicode': u'',
                'SpacesOnlyByte': '   ',
                'SpacesOnlyUnicode': u'   ',
                'SpacesBeforeByte': '   Text',
                'SpacesBeforeUnicode': u'   Text',
                'SpacesAfterByte': 'Text   ',
                'SpacesAfterUnicode': u'Text   ',
                'SpacesBeforeAndAfterByte': '   Text   ',
                'SpacesBeforeAndAfterUnicode': u'   Text   ',
            })
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')
        
        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp.EmptyByte, '')
        self.assertEqual(resp.EmptyUnicode, u'')
        self.assertEqual(resp.SpacesOnlyByte, '   ')
        self.assertEqual(resp.SpacesOnlyUnicode, u'   ')
        self.assertEqual(resp.SpacesBeforeByte, '   Text')
        self.assertEqual(resp.SpacesBeforeUnicode, u'   Text')
        self.assertEqual(resp.SpacesAfterByte, 'Text   ')
        self.assertEqual(resp.SpacesAfterUnicode, u'Text   ')
        self.assertEqual(resp.SpacesBeforeAndAfterByte, '   Text   ')
        self.assertEqual(resp.SpacesBeforeAndAfterUnicode, u'   Text   ')

    def test_none_property_value(self):
        # Act
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'NoneValue': None,
            })
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertFalse(hasattr(resp, 'NoneValue'))

    def test_binary_property_value(self):
        # Act
        binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'binary': EntityProperty('Edm.Binary', binary_data)
            })
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp.binary.type, 'Edm.Binary')
        self.assertEqual(resp.binary.value, binary_data)

    def test_timezone(self):
        # Act
        local_tz = tzoffset('BRST', -10800)
        local_date = datetime(2003, 9, 27, 9, 52, 43, tzinfo=local_tz)
        self._create_table(self.table_name)
        self.ts.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'date': local_date,
            })
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp.date, local_date.astimezone(tzutc()))
        self.assertEqual(resp.date.astimezone(local_tz), local_date)

    def test_sas_query(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)
        token = self.ts.generate_shared_access_signature(
            self.table_name,
            self._get_shared_access_policy(TableSharedAccessPermissions.QUERY),
        )

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        resp = self.ts.query_entities(self.table_name, None, 'age,sex')

        # Assert
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0].age, 39)
        self.assertEqual(resp[0].sex, 'male')
        self.assertFalse(hasattr(resp[0], "birthday"))
        self.assertFalse(hasattr(resp[0], "married"))
        self.assertFalse(hasattr(resp[0], "deceased"))

    def test_sas_add(self):
        # Arrange
        self._create_table(self.table_name)
        policy = self._get_shared_access_policy(TableSharedAccessPermissions.ADD)
        token = self.ts.generate_shared_access_signature(self.table_name, policy)

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        service.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'text': 'hello',
            })

        # Assert
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')
        self.assertIsNotNone(resp)
        self.assertEqual(resp.text, 'hello')

    def test_sas_add_inside_range(self):
        # Arrange
        self._create_table(self.table_name)
        policy = self._get_shared_access_policy(TableSharedAccessPermissions.ADD)
        policy.access_policy.start_pk = 'test'
        policy.access_policy.end_pk = 'test'
        policy.access_policy.start_rk = 'test1'
        policy.access_policy.end_rk = 'test1'
        token = self.ts.generate_shared_access_signature(self.table_name, policy)

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        service.insert_entity(
            self.table_name,
            {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'text': 'hello',
            })

        # Assert
        resp = self.ts.get_entity(self.table_name, 'test', 'test1')
        self.assertIsNotNone(resp)
        self.assertEqual(resp.text, 'hello')

    def test_sas_add_outside_range(self):
        # Arrange
        self._create_table(self.table_name)
        policy = self._get_shared_access_policy(TableSharedAccessPermissions.ADD)
        policy.access_policy.start_pk = 'test'
        policy.access_policy.end_pk = 'test'
        policy.access_policy.start_rk = 'test1'
        policy.access_policy.end_rk = 'test1'
        token = self.ts.generate_shared_access_signature(self.table_name, policy)

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        with self.assertRaises(WindowsAzureMissingResourceError):
            service.insert_entity(
                self.table_name,
                {
                    'PartitionKey': 'test',
                    'RowKey': 'test2',
                    'text': 'hello',
                })

        # Assert

    def test_sas_update(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)
        policy = self._get_shared_access_policy(TableSharedAccessPermissions.UPDATE)
        token = self.ts.generate_shared_access_signature(self.table_name, policy)

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        updated_entity = self._create_updated_entity_dict('MyPartition', '1')
        resp = service.update_entity(self.table_name, 'MyPartition', '1', updated_entity)

        # Assert
        received_entity = self.ts.get_entity(self.table_name, 'MyPartition', '1')
        self._assert_updated_entity(received_entity)

    def test_sas_delete(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)
        policy = self._get_shared_access_policy(TableSharedAccessPermissions.DELETE)
        token = self.ts.generate_shared_access_signature(self.table_name, policy)

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        service.delete_entity(self.table_name, 'MyPartition', '1')

        # Assert
        with self.assertRaises(WindowsAzureMissingResourceError):
            self.ts.get_entity(self.table_name, 'MyPartition', '1')

    def test_sas_signed_identifier(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 2)

        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2018-10-12'
        si.access_policy.permission = TableSharedAccessPermissions.QUERY
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.ts.set_table_acl(self.table_name, identifiers)

        token = self.ts.generate_shared_access_signature(
            self.table_name,
            SharedAccessPolicy(signed_identifier=si.id),
        )

        # Act
        service = TableService(
            credentials.getStorageServicesName(),
            sas_token=token,
        )
        set_service_options(service)
        resp = self.ts.query_entities(self.table_name, None, 'age,sex')

        # Assert
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0].age, 39)
        self.assertEqual(resp[0].sex, 'male')
        self.assertFalse(hasattr(resp[0], "birthday"))
        self.assertFalse(hasattr(resp[0], "married"))
        self.assertFalse(hasattr(resp[0], "deceased"))

    def test_get_table_acl(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        acl = self.ts.get_table_acl(self.table_name)

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_table_acl_iter(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        acl = self.ts.get_table_acl(self.table_name)
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)
        self.assertEqual(len(acl), 0)

    def test_get_table_acl_with_non_existing_container(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.get_table_acl(self.table_name)

        # Assert

    def test_set_table_acl(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        resp = self.ts.set_table_acl(self.table_name)

        # Assert
        self.assertIsNone(resp)
        acl = self.ts.get_table_acl(self.table_name)
        self.assertIsNotNone(acl)

    def test_set_table_acl_with_empty_signed_identifiers(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        identifiers = SignedIdentifiers()

        resp = self.ts.set_table_acl(self.table_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.ts.get_table_acl(self.table_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_set_table_acl_with_signed_identifiers(self):
        # Arrange
        self._create_table_with_default_entities(self.table_name, 1)

        # Act
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2011-10-12'
        si.access_policy.permission = TableSharedAccessPermissions.QUERY
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.ts.set_table_acl(self.table_name, identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.ts.get_table_acl(self.table_name)
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 1)
        self.assertEqual(len(acl), 1)
        self.assertEqual(acl.signed_identifiers[0].id, 'testid')
        self.assertEqual(acl[0].id, 'testid')

    def test_set_table_acl_with_non_existing_table(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.ts.set_table_acl(self.table_name)

        # Assert


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
