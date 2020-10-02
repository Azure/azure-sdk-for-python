# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
import msrest

import pytest

import uuid
from base64 import b64encode
from datetime import datetime, timedelta
from enum import Enum

from azure.data.tables import TableServiceClient, TableClient, generate_table_sas
from dateutil.tz import tzutc, tzoffset
from math import isnan

from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ResourceModifiedError)

from azure.data.tables._entity import TableEntity, EntityProperty, EdmType
from azure.data.tables._models import TableSasPermissions, AccessPolicy, UpdateMode

from _shared.testcase import TableTestCase, LogCaptured

from devtools_testutils import CachedResourceGroupPreparer, CachedStorageAccountPreparer


# ------------------------------------------------------------------------------
SERVICE_CLIENT_ENDPOINTS = [
    # 'table',
    'cosmos',
]
# {
#     TableServiceClient: 'table',
#     # TableClient: 'table',
#     TableServiceClient: 'cosmos',
#     # TableClient: 'cosmos',
# }
# ------------------------------------------------------------------------------

class StorageTableEntityTest(TableTestCase):

    def _set_up(self, storage_account, storage_account_key, url='table'):
        self.table_name = self.get_resource_name('uttable')
        self.ts = TableServiceClient(
            self.account_url(storage_account, url),
            credential=storage_account_key,
            table_name = self.table_name
        )
        # self.ts = TableServiceClient(self.account_url(storage_account, url), storage_account_key)
        # self.table_name = self.get_resource_name('uttable')
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live:
            try:
                self.ts.create_table(self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []

    def _tear_down(self):
        if self.is_live:
            try:
                self.ts.delete_table(self.table_name)
            except:
                pass

            try:
                for table_name in self.query_tables:
                    try:
                        self.ts.delete_table(table_name)
                    except:
                        pass
            except AttributeError:
                pass

    # --Helpers-----------------------------------------------------------------

    def _create_query_table(self, entity_count):
        """
        Creates a table with the specified name and adds entities with the
        default set of values. PartitionKey is set to 'MyPartition' and RowKey
        is set to a unique counter value starting at 1 (as a string).
        """
        table_name = self.get_resource_name('querytable')
        table = self.ts.create_table(table_name)
        self.query_tables.append(table_name)
        client = self.ts.get_table_client(table_name)
        entity = self._create_random_entity_dict()
        for i in range(1, entity_count + 1):
            entity['RowKey'] = entity['RowKey'] + str(i)
            client.create_entity(entity)
        # with self.ts.batch(table_name) as batch:
        #    for i in range(1, entity_count + 1):
        #        entity['RowKey'] = entity['RowKey'] + str(i)
        #        batch.create_entity(entity)
        return client

    def _create_random_base_entity_dict(self):
        """
        Creates a dict-based entity with only pk and rk.
        """
        # partition = self.get_resource_name('pk')
        # row = self.get_resource_name('rk')
        partition, row = self._create_pk_rk(None, None)
        return {
            'PartitionKey': partition,
            'RowKey': row,
        }

    def _create_pk_rk(self, pk, rk):
        try:
            pk = pk if pk is not None else self.get_resource_name('pk').decode('utf-8')
            rk = rk if rk is not None else self.get_resource_name('rk').decode('utf-8')
        except AttributeError:
            pk = pk if pk is not None else self.get_resource_name('pk')
            rk = rk if rk is not None else self.get_resource_name('rk')
        return pk, rk


    def _create_random_entity_dict(self, pk=None, rk=None):
        """
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        """
        # partition = pk if pk is not None else self.get_resource_name('pk').decode('utf-8')
        # row = rk if rk is not None else self.get_resource_name('rk').decode('utf-8')
        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            'PartitionKey': partition,
            'RowKey': row,
            'age': 39,
            'sex': u'male',
            'married': True,
            'deceased': False,
            'optional': None,
            'ratio': 3.1,
            'evenratio': 3.0,
            'large': 933311100,
            'Birthday': datetime(1973, 10, 4, tzinfo=tzutc()),
            'birthday': datetime(1970, 10, 4, tzinfo=tzutc()),
            'binary': b'binary',
            'other': EntityProperty(value=20, type=EdmType.INT32),
            'clsid': uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        }
        return TableEntity(**properties)

    def _insert_random_entity(self, pk=None, rk=None):
        entity = self._create_random_entity_dict(pk, rk)
        metadata = self.table.create_entity(entity)
        return entity, metadata['etag']

    def _create_updated_entity_dict(self, partition, row):
        """
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        """
        return {
            'PartitionKey': partition,
            'RowKey': row,
            'age': u'abc',
            'sex': u'female',
            'sign': u'aquarius',
            'birthday': datetime(1991, 10, 4, tzinfo=tzutc())
        }

    def _assert_default_entity(self, entity, headers=None):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEqual(entity['age'].value, 39)
        self.assertEqual(entity['sex'].value, 'male')
        self.assertEqual(entity['married'], True)
        self.assertEqual(entity['deceased'], False)
        self.assertFalse("optional" in entity)
        self.assertFalse("aquarius" in entity)
        self.assertEqual(entity['ratio'], 3.1)
        self.assertEqual(entity['evenratio'], 3.0)
        self.assertEqual(entity['large'].value, 933311100)
        self.assertEqual(entity['Birthday'], datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['birthday'], datetime(1970, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['binary'].value, b'binary')
        self.assertIsInstance(entity['other'], EntityProperty)
        self.assertEqual(entity['other'].type, EdmType.INT32)
        self.assertEqual(entity['other'].value, 20)
        self.assertEqual(entity['clsid'], uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833'))
        # self.assertTrue('metadata' in entity.odata)
        # self.assertIsNotNone(entity.metadata['timestamp'])
        # self.assertIsInstance(entity.metadata['timestamp'], datetime)
        # if headers:
        #    self.assertTrue("etag" in headers)

    def _assert_default_entity_json_full_metadata(self, entity, headers=None):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEqual(entity['age'].value, 39)
        self.assertEqual(entity['sex'].value, 'male')
        self.assertEqual(entity['married'], True)
        self.assertEqual(entity['deceased'], False)
        self.assertFalse("optional" in entity)
        self.assertFalse("aquarius" in entity)
        self.assertEqual(entity['ratio'], 3.1)
        self.assertEqual(entity['evenratio'], 3.0)
        self.assertEqual(entity['large'].value, 933311100)
        self.assertEqual(entity['Birthday'], datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['birthday'], datetime(1970, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity['binary'].value, b'binary')
        self.assertIsInstance(entity['other'], EntityProperty)
        self.assertEqual(entity['other'].type, EdmType.INT32)
        self.assertEqual(entity['other'].value, 20)
        self.assertEqual(entity['clsid'], uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833'))
        # self.assertTrue('metadata' in entity.odata)
        # self.assertTrue('id' in entity.odata)
        # self.assertTrue('type' in entity.odata)
        # self.assertTrue('etag' in entity.odata)
        # self.assertTrue('editLink' in entity.odata)

    def _assert_default_entity_json_no_metadata(self, entity, headers=None):
        '''
        Asserts that the entity passed in matches the default entity.
        '''
        self.assertEqual(entity['age'].value, 39)
        self.assertEqual(entity['sex'].value, 'male')
        self.assertEqual(entity['married'], True)
        self.assertEqual(entity['deceased'], False)
        self.assertFalse("optional" in entity)
        self.assertFalse("aquarius" in entity)
        self.assertEqual(entity['ratio'], 3.1)
        self.assertEqual(entity['evenratio'], 3.0)
        self.assertEqual(entity['large'].value, 933311100)
        self.assertTrue(entity['Birthday'].value.startswith('1973-10-04T00:00:00'))
        self.assertTrue(entity['birthday'].value.startswith('1970-10-04T00:00:00'))
        self.assertTrue(entity['Birthday'].value.endswith('00Z'))
        self.assertTrue(entity['birthday'].value.endswith('00Z'))
        self.assertEqual(entity['binary'].value, b64encode(b'binary').decode('utf-8'))
        self.assertIsInstance(entity['other'], EntityProperty)
        self.assertEqual(entity['other'].type, EdmType.INT32)
        self.assertEqual(entity['other'].value, 20)
        self.assertEqual(entity['clsid'].value, 'c9da6455-213d-42c9-9a79-3e9149a57833')
        # self.assertIsNone(entity.odata)
        # self.assertIsNotNone(entity.Timestamp)

    def _assert_updated_entity(self, entity):
        '''
        Asserts that the entity passed in matches the updated entity.
        '''
        self.assertEqual(entity.age.value, 'abc')
        self.assertEqual(entity.sex.value, 'female')
        self.assertFalse(hasattr(entity, "married"))
        self.assertFalse(hasattr(entity, "deceased"))
        self.assertEqual(entity.sign.value, 'aquarius')
        self.assertFalse(hasattr(entity, "optional"))
        self.assertFalse(hasattr(entity, "ratio"))
        self.assertFalse(hasattr(entity, "evenratio"))
        self.assertFalse(hasattr(entity, "large"))
        self.assertFalse(hasattr(entity, "Birthday"))
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertFalse(hasattr(entity, "other"))
        self.assertFalse(hasattr(entity, "clsid"))

    def _assert_merged_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity
        merged with the updated entity.
        '''
        self.assertEqual(entity.age.value, 'abc')
        self.assertEqual(entity.sex.value, 'female')
        self.assertEqual(entity.sign.value, 'aquarius')
        self.assertEqual(entity.married, True)
        self.assertEqual(entity.deceased, False)
        self.assertEqual(entity.sign.value, 'aquarius')
        self.assertEqual(entity.ratio, 3.1)
        self.assertEqual(entity.evenratio, 3.0)
        self.assertEqual(entity.large.value, 933311100)
        self.assertEqual(entity.Birthday, datetime(1973, 10, 4, tzinfo=tzutc()))
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertIsInstance(entity.other, EntityProperty)
        self.assertEqual(entity.other.type, EdmType.INT32)
        self.assertEqual(entity.other.value, 20)
        self.assertIsInstance(entity.clsid, uuid.UUID)
        self.assertEqual(str(entity.clsid), 'c9da6455-213d-42c9-9a79-3e9149a57833')

    def _assert_valid_metadata(self, metadata):
        keys = metadata.keys()
        self.assertIn("version", keys)
        self.assertIn("date", keys)
        self.assertIn("etag", keys)
        self.assertEqual(len(keys), 3)

    # --Test cases for entities ------------------------------------------
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_etag(self, resource_group, location, storage_account, storage_account_key):

        self._set_up(storage_account, storage_account_key)
        try:

            entity, _ = self._insert_random_entity()

            entity1 = self.table.get_entity(row_key=entity.RowKey, partition_key=entity.PartitionKey)

            with self.assertRaises(AttributeError):
                etag = entity1.etag

            self.assertIsNotNone(entity1.metadata())
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_user_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._insert_random_entity()

            # Act
            # resp = self.table.create_item(entity)
            resp = self.table.query_entities(filter="married eq @my_param", parameters={'my_param': 'True'})

            # Assert  --- Does this mean insert returns nothing?
            self.assertIsNotNone(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_dictionary(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            # resp = self.table.create_item(entity)
            resp = self.table.create_entity(entity=entity)

            # Assert
            self._assert_valid_metadata(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_hook(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = self.table.create_entity(entity=entity)
            received_entity = self.table.get_entity(
                row_key=entity['RowKey'],
                partition_key=entity['PartitionKey']
            )

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=nometadata'}
            # Act
            # response_hook=lambda e, h: (e, h)
            resp = self.table.create_entity(
                entity=entity,
                headers=headers,
            )
            received_entity = self.table.get_entity(
                row_key=entity['RowKey'],
                partition_key=entity['PartitionKey'],
                headers=headers
            )

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity_json_no_metadata(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_full_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=fullmetadata'}

            # Act
            resp = self.table.create_entity(
                entity=entity,
                headers={'Accept': 'application/json;odata=fullmetadata'},
            )
            received_entity = self.table.get_entity(
                row_key=entity['RowKey'],
                partition_key=entity['PartitionKey'],
                headers=headers
            )

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity_json_full_metadata(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_conflict(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            with self.assertRaises(ResourceExistsError):
                self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_large_int32_value_throws(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            dict32 = self._create_random_base_entity_dict()
            dict32['large'] = EntityProperty(2 ** 31, EdmType.INT32)

            # Assert
            with self.assertRaises(TypeError):
                self.table.create_entity(entity=dict32)

            dict32['large'] = EntityProperty(-(2 ** 31 + 1), EdmType.INT32)
            with self.assertRaises(TypeError):
                self.table.create_entity(entity=dict32)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_large_int64_value_throws(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 63, EdmType.INT64)

            # Assert
            with self.assertRaises(TypeError):
                self.table.create_entity(entity=dict64)

            dict64['large'] = EntityProperty(-(2 ** 63 + 1), EdmType.INT64)
            with self.assertRaises(TypeError):
                self.table.create_entity(entity=dict64)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_missing_pk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = {'RowKey': 'rk'}

            # Act
            with self.assertRaises(ValueError):
                # resp = self.table.create_item(entity)
                resp = self.table.create_entity(entity=entity)
            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_empty_string_pk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = {'RowKey': u'rk', 'PartitionKey': u''}

            # Act
            if 'cosmos' in self.table.url:
                with self.assertRaises(HttpResponseError):
                    self.table.create_entity(entity=entity)
            else:
                resp = self.table.create_entity(entity=entity)
                self._assert_valid_metadata(resp)

        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_missing_rk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = {'PartitionKey': 'pk'}

            # Act
            with self.assertRaises(ValueError):
                resp = self.table.create_entity(entity=entity)

        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_empty_string_rk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = {'PartitionKey': u'pk', 'RowKey': u''}

            # Act
            if 'cosmos' in self.table.url:
                with self.assertRaises(HttpResponseError):
                    self.table.create_entity(entity=entity)
            else:
                resp = self.table.create_entity(entity=entity)
                self._assert_valid_metadata(resp)

        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_too_many_properties(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        if 'cosmos' in self.table.url:
            pytest.skip("Cosmos supports large number of properties.")
        try:
            entity = self._create_random_base_entity_dict()
            for i in range(255):
                entity['key{0}'.format(i)] = 'value{0}'.format(i)

            # Act
            with self.assertRaises(HttpResponseError):
                resp = self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_property_name_too_long(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        if 'cosmos' in self.table.url:
            pytest.skip("Cosmos supports large property names.")
        try:
            entity = self._create_random_base_entity_dict()
            entity['a' * 256] = 'badval'

            # Act
            with self.assertRaises(HttpResponseError):
                resp = self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_entity_with_enums(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            # Act
            class Color(Enum):
                RED = 1
                BLUE = 2
                YELLOW = 3

            pk, rk = self._create_pk_rk(None, None)
            entity = TableEntity()
            entity.PartitionKey = pk
            entity.RowKey = rk
            entity.test1 = Color.YELLOW
            entity.test2 = Color.BLUE
            entity.test3 = Color.RED


            self.table.create_entity(entity=entity)
            resp_entity = self.table.get_entity(partition_key=pk, row_key=rk)
            assert str(entity.test1) == resp_entity.test1.value
            assert str(entity.test2) == resp_entity.test2.value
            assert str(entity.test3) == resp_entity.test3.value

        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])

            # Assert
            self.assertEqual(resp['PartitionKey'], entity['PartitionKey'])
            self.assertEqual(resp['RowKey'], entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_with_hook(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            # resp, headers
            # response_hook=lambda e, h: (e, h)
            resp = self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey'],
            )

            # Assert
            self.assertEqual(resp['PartitionKey'], entity['PartitionKey'])
            self.assertEqual(resp['RowKey'], entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_if_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = self._insert_random_entity()

            # Act
            # Do a get and confirm the etag is parsed correctly by using it
            # as a condition to delete.
            resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])

            self.table.delete_entity(
                partition_key=resp['PartitionKey'],
                row_key=resp['RowKey'],
                etag=etag,
                match_condition=MatchConditions.IfNotModified
            )

            with self.assertRaises(ResourceNotFoundError):
                resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                            row_key=entity['RowKey'])

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_full_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(
                entity.PartitionKey,
                entity.RowKey,
                headers={'accept': 'application/json;odata=fullmetadata'})

            # Assert
            self.assertEqual(resp.PartitionKey, entity.PartitionKey)
            self.assertEqual(resp.RowKey, entity.RowKey)
            self._assert_default_entity_json_full_metadata(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey,
                headers={'accept': 'application/json;odata=nometadata'})

            # Assert
            self.assertEqual(resp.PartitionKey, entity.PartitionKey)
            self.assertEqual(resp.RowKey, entity.RowKey)
            self._assert_default_entity_json_no_metadata(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            with self.assertRaises(ResourceNotFoundError):
                self.table.get_entity(partition_key=entity.PartitionKey,
                                      row_key=entity.RowKey)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_get_entity_with_special_doubles(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({
                'inf': float('inf'),
                'negativeinf': float('-inf'),
                'nan': float('nan')
            })
            self.table.create_entity(entity=entity)

            # Act
            received_entity = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])

            # Assert
            self.assertEqual(received_entity.inf, float('inf'))
            self.assertEqual(received_entity.negativeinf, float('-inf'))
            self.assertTrue(isnan(received_entity.nan))
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_update_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)

            # resp = self.table.update_item(sent_entity, response_hook=lambda e, h: h)
            resp = self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            #  self.assertTrue(resp)
            received_entity = self.table.get_entity(partition_key=entity.PartitionKey,
                                                    row_key=entity.RowKey)

            with self.assertRaises(KeyError):
                del received_entity['property_that_does_not_exist']
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_update_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with self.assertRaises(ResourceNotFoundError):
                self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_update_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)

            resp = self.table.update_entity(
                mode=UpdateMode.REPLACE, entity=sent_entity, etag=etag,
                match_condition=MatchConditions.IfNotModified)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_update_entity_with_if_doesnt_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with self.assertRaises(HttpResponseError):
                self.table.update_entity(
                    mode=UpdateMode.REPLACE,
                    entity=sent_entity,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)
            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_or_merge_entity_with_existing_entity(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_or_merge_entity_with_non_existing_entity(self, resource_group, location, storage_account,
                                                             storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity['PartitionKey'],
                                                    entity['RowKey'])
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_or_replace_entity_with_existing_entity(self, resource_group, location, storage_account,
                                                           storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_insert_or_replace_entity_with_non_existing_entity(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity['PartitionKey'],
                                                    entity['RowKey'])
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_merge_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_merge_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with self.assertRaises(ResourceNotFoundError):
                self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_merge_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = self.table.update_entity(
                mode=UpdateMode.MERGE,
                entity=sent_entity,
                etag=etag,
                match_condition=MatchConditions.IfNotModified)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_merge_entity_with_if_doesnt_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with self.assertRaises(HttpResponseError):
                self.table.update_entity(mode=UpdateMode.MERGE,
                                         entity=sent_entity,
                                         etag='W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                                         match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_delete_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.delete_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)

            # Assert
            self.assertIsNone(resp)
            with self.assertRaises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_delete_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            with self.assertRaises(ResourceNotFoundError):
                self.table.delete_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_delete_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = self._insert_random_entity()

            # Act
            resp = self.table.delete_entity(entity.PartitionKey, entity.RowKey, etag=etag,
                                            match_condition=MatchConditions.IfNotModified)

            # Assert
            self.assertIsNone(resp)
            with self.assertRaises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_delete_entity_with_if_doesnt_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            with self.assertRaises(HttpResponseError):
                self.table.delete_entity(
                    entity.PartitionKey, entity.RowKey,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_unicode_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity1 = entity.copy()
            entity1.update({'Description': u'ꀕ'})
            entity2 = entity.copy()
            entity2.update({'RowKey': u'test2', 'Description': u'ꀕ'})

            # Act
            self.table.create_entity(entity=entity1)
            self.table.create_entity(entity=entity2)
            entities = list(self.table.query_entities(
                filter="PartitionKey eq '{}'".format(entity['PartitionKey'])))

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].Description.value, u'ꀕ')
            self.assertEqual(entities[1].Description.value, u'ꀕ')
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_unicode_property_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity1 = entity.copy()
            entity1.update({u'啊齄丂狛狜': u'ꀕ'})
            entity2 = entity.copy()
            entity2.update({'RowKey': u'test2', u'啊齄丂狛狜': u'hello'})

            # Act
            self.table.create_entity(entity=entity1)
            self.table.create_entity(entity=entity2)
            entities = list(self.table.query_entities(
                filter="PartitionKey eq '{}'".format(entity['PartitionKey'])))

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0][u'啊齄丂狛狜'].value, u'ꀕ')
            self.assertEqual(entities[1][u'啊齄丂狛狜'].value, u'hello')
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_operations_on_entity_with_partition_key_having_single_quote(self, resource_group, location,
                                                                         storage_account, storage_account_key):

        # Arrange
        partition_key_with_single_quote = u"a''''b"
        row_key_with_single_quote = u"a''''b"
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity(pk=partition_key_with_single_quote, rk=row_key_with_single_quote)

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            # row key here only has 2 quotes
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)

            # Act
            sent_entity['newField'] = u'newFieldValue'
            resp = self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)
            self.assertEqual(received_entity['newField'].value, 'newFieldValue')

            # Act
            resp = self.table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            self.assertIsNone(resp)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_empty_and_spaces_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({
                'EmptyByte': b'',
                'EmptyUnicode': u'',
                'SpacesOnlyByte': b'   ',
                'SpacesOnlyUnicode': u'   ',
                'SpacesBeforeByte': b'   Text',
                'SpacesBeforeUnicode': u'   Text',
                'SpacesAfterByte': b'Text   ',
                'SpacesAfterUnicode': u'Text   ',
                'SpacesBeforeAndAfterByte': b'   Text   ',
                'SpacesBeforeAndAfterUnicode': u'   Text   ',
            })

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertEqual(resp.EmptyByte.value, b'')
            self.assertEqual(resp.EmptyUnicode.value, u'')
            self.assertEqual(resp.SpacesOnlyByte.value, b'   ')
            self.assertEqual(resp.SpacesOnlyUnicode.value, u'   ')
            self.assertEqual(resp.SpacesBeforeByte.value, b'   Text')
            self.assertEqual(resp.SpacesBeforeUnicode.value, u'   Text')
            self.assertEqual(resp.SpacesAfterByte.value, b'Text   ')
            self.assertEqual(resp.SpacesAfterUnicode.value, u'Text   ')
            self.assertEqual(resp.SpacesBeforeAndAfterByte.value, b'   Text   ')
            self.assertEqual(resp.SpacesBeforeAndAfterUnicode.value, u'   Text   ')
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_none_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({'NoneValue': None})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertFalse(hasattr(resp, 'NoneValue'))
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_binary_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
            entity = self._create_random_base_entity_dict()
            entity.update({'binary': b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertEqual(resp.binary.value, binary_data)
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_timezone(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            local_tz = tzoffset('BRST', -10800)
            local_date = datetime(2003, 9, 27, 9, 52, 43, tzinfo=local_tz)
            entity = self._create_random_base_entity_dict()
            entity.update({'date': local_date})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            # times are not equal because request is made after
            # self.assertEqual(resp.date.astimezone(tzutc()), local_date.astimezone(tzutc()))
            self.assertEqual(resp.date.astimezone(local_tz), local_date)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities())

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity(entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_zero_entities(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(0)

            # Act
            entities = list(table.list_entities())

            # Assert
            self.assertEqual(len(entities), 0)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_full_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(headers={'accept': 'application/json;odata=fullmetadata'}))

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity_json_full_metadata(entity)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(headers={'accept': 'application/json;odata=nometadata'}))

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity_json_no_metadata(entity)
        finally:
            self._tear_down()

    # TODO: move this over to the batch test file when merged
    @pytest.mark.skip("Batch not implemented")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_large(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        table_name = self._create_query_table(0)
        total_entities_count = 1000
        entities_per_batch = 50

        for j in range(total_entities_count // entities_per_batch):
            batch = TableBatch()
            for i in range(entities_per_batch):
                entity = Entity()
                entity.PartitionKey = 'large'
                entity.RowKey = 'batch{0}-item{1}'.format(j, i)
                entity.test = EntityProperty(True)
                entity.test2 = 'hello world;' * 100
                entity.test3 = 3
                entity.test4 = EntityProperty(1234567890)
                entity.test5 = datetime(2016, 12, 31, 11, 59, 59, 0)
                batch.create_entity(entity)
            self.ts.send_batch(table_name, batch)

        # Act
        start_time = datetime.now()
        entities = list(self.ts.query_entities(table_name))
        elapsed_time = datetime.now() - start_time

        # Assert
        print('query_entities took {0} secs.'.format(elapsed_time.total_seconds()))
        # azure allocates 5 seconds to execute a query
        # if it runs slowly, it will return fewer results and make the test fail
        self.assertEqual(len(entities), total_entities_count)

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_with_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            entities = list(self.table.query_entities(
                filter="PartitionKey eq '{}'".format(entity.PartitionKey)))

            # Assert
            self.assertEqual(len(entities), 1)
            self.assertEqual(entity.PartitionKey, entities[0].PartitionKey)
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_with_select(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(select=['age', 'sex']))

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].age.value, 39)
            self.assertEqual(entities[0].sex.value, 'male')
            self.assertFalse(hasattr(entities[0], "birthday"))
            self.assertFalse(hasattr(entities[0], "married"))
            self.assertFalse(hasattr(entities[0], "deceased"))
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_with_top(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(3)
            # circular dependencies made this return a list not an item paged - problem when calling by page
            # Act
            entities = list(next(table.list_entities(results_per_page=2).by_page()))

            # Assert
            self.assertEqual(len(entities), 2)
        finally:
            self._tear_down()

    # @pytest.mark.skip("pending")
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_query_entities_with_top_and_next(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        self._set_up(storage_account, storage_account_key)
        try:
            table = self._create_query_table(5)

            # Act
            resp1 = table.list_entities(results_per_page=2).by_page()
            next(resp1)
            resp2 = table.list_entities(results_per_page=2).by_page(
                continuation_token=resp1.continuation_token)
            next(resp2)
            resp3 = table.list_entities(results_per_page=2).by_page(
                continuation_token=resp2.continuation_token)
            next(resp3)

            entities1 = resp1._current_page
            entities2 = resp2._current_page
            entities3 = resp3._current_page

            # Assert
            self.assertEqual(len(entities1), 2)
            self.assertEqual(len(entities2), 2)
            self.assertEqual(len(entities3), 1)
            self._assert_default_entity(entities1[0])
            self._assert_default_entity(entities1[1])
            self._assert_default_entity(entities2[0])
            self._assert_default_entity(entities2[1])
            self._assert_default_entity(entities3[0])
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_query(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")

        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity['PartitionKey'])))

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_add(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)

            entity = self._create_random_entity_dict()
            table.create_entity(entity=entity)

            # Assert
            resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_add_inside_range(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk=u'test', start_rk=u'test1',
                end_pk=u'test', end_rk=u'test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entity = self._create_random_entity_dict(u'test', u'test1')
            table.create_entity(entity=entity)

            # Assert
            resp = self.table.get_entity('test', 'test1')
            self._assert_default_entity(resp)
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_add_outside_range(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk='test', start_rk='test1',
                end_pk='test', end_rk='test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            with self.assertRaises(HttpResponseError):
                entity = self._create_random_entity_dict()
                table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_update(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(update=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            updated_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = table.update_entity(mode=UpdateMode.REPLACE, entity=updated_entity)

            # Assert
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            self.assertIsNotNone(resp)
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_delete(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                permission=TableSasPermissions(delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            with self.assertRaises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()


    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_upper_case_table_name(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()

            # Table names are case insensitive, so simply upper case our existing table name to test
            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name.upper(),
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity['PartitionKey'])))

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    @pytest.mark.skip("pending")
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest")
    def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()

            access_policy = AccessPolicy()
            access_policy.start = datetime(2011, 10, 11)
            access_policy.expiry = datetime(2020, 10, 12)
            access_policy.permission = TableSasPermissions(read=True)
            identifiers = {'testid': access_policy}

            self.table.set_table_access_policy(identifiers)

            token = generate_table_sas(
                storage_account.name,
                storage_account_key,
                self.table_name,
                policy_id='testid',
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity.PartitionKey)))

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
