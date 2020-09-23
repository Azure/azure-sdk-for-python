# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest

import pytest

import uuid
from base64 import b64encode
from datetime import datetime, timedelta

from azure.data.tables import generate_table_sas
from azure.data.tables._generated.models import QueryOptions
from azure.data.tables.aio import TableServiceClient
from dateutil.tz import tzutc, tzoffset
from math import isnan

from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

from azure.data.tables._entity import TableEntity, EntityProperty, EdmType
from azure.data.tables import TableSasPermissions, AccessPolicy, UpdateMode

from _shared.testcase import GlobalStorageAccountPreparer, TableTestCase, LogCaptured


# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

class StorageTableEntityTest(TableTestCase):

    async def _set_up(self, storage_account, storage_account_key):
        self.ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        self.table_name = self.get_resource_name('uttable')
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live:
            try:
                await self.ts.create_table(table_name=self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []

    async def _tear_down(self):
        if self.is_live:
            try:
                await self.ts.delete_table(self.table_name)
            except:
                pass

            for table_name in self.query_tables:
                try:
                    await self.ts.delete_table(table_name)
                except:
                    pass

    # --Helpers-----------------------------------------------------------------

    async def _create_query_table(self, entity_count):
        """
        Creates a table with the specified name and adds entities with the
        default set of values. PartitionKey is set to 'MyPartition' and RowKey
        is set to a unique counter value starting at 1 (as a string).
        """
        table_name = self.get_resource_name('querytable')
        table = await self.ts.create_table(table_name)
        self.query_tables.append(table_name)
        client = self.ts.get_table_client(table_name)
        entity = self._create_random_entity_dict()
        for i in range(1, entity_count + 1):
            entity['RowKey'] = entity['RowKey'] + str(i)
            await client.create_entity(entity=entity)
        # with self.ts.batch(table_name) as batch:
        #    for i in range(1, entity_count + 1):
        #        entity['RowKey'] = entity['RowKey'] + str(i)
        #        batch.create_entity(entity)
        return client

    def _create_random_base_entity_dict(self):
        """
        Creates a dict-based entity with only pk and rk.
        """
        partition = self.get_resource_name('pk')
        row = self.get_resource_name('rk')
        return {
            'PartitionKey': partition,
            'RowKey': row,
        }

    def _create_random_entity_dict(self, pk=None, rk=None):
        """
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        """
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
            'other': EntityProperty(value=20, type=EdmType.INT32),
            'clsid': uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')
        }
        return TableEntity(**properties)

    async def _insert_random_entity(self, pk=None, rk=None):
        entity = self._create_random_entity_dict(pk, rk)
        # , response_hook=lambda e, h: h['etag']
        metadata = await self.table.create_entity(entity=entity)
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
            'age': 'abc',
            'sex': 'female',
            'sign': 'aquarius',
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
        self.assertEqual(entity['binary'].value, b'binary') # TODO: added the ".value" portion, verify this is correct
        self.assertIsInstance(entity['other'], EntityProperty)
        self.assertEqual(entity['other'].type, EdmType.INT32)
        self.assertEqual(entity['other'].value, 20)
        self.assertEqual(entity['clsid'], uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833'))
        # self.assertTrue('metadata' in entity.odata)

        # TODO: these are commented out / nonexistent in sync code, should we have them?
        # self.assertIsNotNone(entity.Timestamp)
        # self.assertIsInstance(entity.Timestamp, datetime)
        if headers:
            self.assertTrue("etag" in headers)
            self.assertIsNotNone(headers['etag'])

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

        # TODO: commented out in sync, should we have these?
        # self.assertIsNotNone(entity.Timestamp)
        # self.assertIsInstance(entity.Timestamp, datetime)
        # if headers:
        #     self.assertTrue("etag" in headers)
        #     self.assertIsNotNone(headers['etag'])

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
        # self.assertIsInstance(entity.Timestamp, datetime)
        if headers:
            self.assertTrue("etag" in headers)
            self.assertIsNotNone(headers['etag'])

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
        # self.assertEqual(entity.birthday, "1991-10-04 00:00:00+00:00")
        self.assertEqual(entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc()))
        self.assertFalse(hasattr(entity, "other"))
        self.assertFalse(hasattr(entity, "clsid"))
        # TODO: should these all be commented out?
        #        self.assertIsNotNone(entity.odata.etag)
        # self.assertIsNotNone(entity.Timestamp)
        # self.assertIsInstance(entity.timestamp, datetime)

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
        # TODO: should these all be commented out?
        # self.assertIsNotNone(entity.etag)
        # self.assertIsNotNone(entity.odata['etag'])
        # self.assertIsNotNone(entity.Timestamp)
        # self.assertIsInstance(entity.Timestamp, datetime)

    def _assert_valid_metadata(self, metadata):
        keys = metadata.keys()
        self.assertIn("version", keys)
        self.assertIn("date", keys)
        self.assertIn("etag", keys)
        self.assertEqual(len(keys), 3)

    # --Test cases for entities ------------------------------------------
    @GlobalStorageAccountPreparer()
    async def test_insert_entity_dictionary(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = await self.table.create_entity(entity=entity)

            # Assert
            self._assert_valid_metadata(resp)
        finally:
            await self._tear_down()

    @GlobalStorageAccountPreparer()
    async def test_insert_entity_with_hook(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = await self.table.create_entity(entity=entity)
            received_entity = await self.table.get_entity(
                partition_key=entity["PartitionKey"],
                row_key=entity["RowKey"]
            )
            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity(received_entity)
        finally:
            await self._tear_down()

    @GlobalStorageAccountPreparer()
    async def test_insert_entity_with_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=nometadata'}
            # Act
            # response_hook = lambda e, h: (e, h)
            resp = await self.table.create_entity(
                entity=entity,
                headers={'Accept': 'application/json;odata=nometadata'},
            )
            received_entity = await self.table.get_entity(
                partition_key=entity["PartitionKey"],
                row_key=entity["RowKey"],
                headers=headers
            )

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity_json_no_metadata(received_entity)
        finally:
            await self._tear_down()

    @GlobalStorageAccountPreparer()
    async def test_insert_entity_with_full_metadata(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=fullmetadata'}

            # Act
            # response_hook=lambda e, h: (e, h)
            resp = await self.table.create_entity(
                entity=entity,
                headers=headers
            )
            received_entity = await self.table.get_entity(
                partition_key=entity["PartitionKey"],
                row_key=entity["RowKey"],
                headers=headers
            )

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_default_entity_json_full_metadata(received_entity)
        finally:
            await self._tear_down()

    @GlobalStorageAccountPreparer()
    async def test_insert_entity_conflict(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with self.assertRaises(ResourceExistsError):
                # self.table.create_item(entity)
                await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()

    @GlobalStorageAccountPreparer()
    async def test_insert_entity_with_large_int32_value_throws(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            # Act
            dict32 = self._create_random_base_entity_dict()
            dict32['large'] = EntityProperty(2 ** 31, EdmType.INT32) # TODO: this is outside the range of int32

            # Assert
            with self.assertRaises(TypeError):
                await self.table.create_entity(entity=dict32)

            dict32['large'] = EntityProperty(-(2 ** 31 + 1), EdmType.INT32)  # TODO: this is outside the range of int32
            with self.assertRaises(TypeError):
                await self.table.create_entity(entity=dict32)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_with_large_int64_value_throws(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 63, EdmType.INT64)

            # Assert
            with self.assertRaises(TypeError):
                await self.table.create_entity(entity=dict64)

            dict64['large'] = EntityProperty(-(2 ** 63 + 1), EdmType.INT64)
            with self.assertRaises(TypeError):
                await self.table.create_entity(entity=dict64)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_missing_pk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = {'RowKey': 'rk'}

            # Act
            with self.assertRaises(ValueError):
                resp = await self.table.create_entity(entity=entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_empty_string_pk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = {'RowKey': 'rk', 'PartitionKey': ''}

            # Act
            if 'cosmos' in self.table.url:
                with self.assertRaises(HttpResponseError):
                    await self.table.create_entity(entity=entity)
            else:
                resp = await self.table.create_entity(entity=entity)
                self._assert_valid_metadata(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_missing_rk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = {'PartitionKey': 'pk'}

            # Act
            with self.assertRaises(ValueError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_empty_string_rk(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = {'PartitionKey': 'pk', 'RowKey': ''}

            # Act
            if 'cosmos' in self.table.url:
                with self.assertRaises(HttpResponseError):
                    await self.table.create_entity(entity=entity)
            else:
                resp = await self.table.create_entity(entity=entity)
                self._assert_valid_metadata(resp)

                # Assert
            #  self.assertIsNone(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_too_many_properties(self, resource_group, location, storage_account,
                                                     storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        if 'cosmos' in self.table.url:
            pytest.skip("Cosmos supports large number of properties.")
        try:
            entity = self._create_random_base_entity_dict()
            for i in range(255):
                entity['key{0}'.format(i)] = 'value{0}'.format(i)

            # Act
            with self.assertRaises(HttpResponseError):
                resp = await self.table.create_entity(entity=entity)
            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_entity_property_name_too_long(self, resource_group, location, storage_account,
                                                        storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        if 'cosmos' in self.table.url:
            pytest.skip("Cosmos supports large property names.")
        try:
            entity = self._create_random_base_entity_dict()
            entity['a' * 256] = 'badval'

            # Act
            with self.assertRaises(HttpResponseError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'])

            # Assert
            self.assertEqual(resp['PartitionKey'], entity['PartitionKey'])
            self.assertEqual(resp['RowKey'], entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_with_hook(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            # resp, headers
            # response_hook=lambda e, h: (e, h)
            resp = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey'],
            )

            # Assert
            self.assertEqual(resp['PartitionKey'], entity['PartitionKey'])
            self.assertEqual(resp['RowKey'], entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_if_match(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            # Do a get and confirm the etag is parsed correctly by using it
            # as a condition to delete.
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'])

            await self.table.delete_entity(
                partition_key=resp['PartitionKey'],
                row_key=resp['RowKey'],
                etag=etag,
                match_condition=MatchConditions.IfNotModified
            )

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_full_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                entity.PartitionKey,
                entity.RowKey,
                headers={'accept': 'application/json;odata=fullmetadata'})

            # Assert
            self.assertEqual(resp.PartitionKey, entity.PartitionKey)
            self.assertEqual(resp.RowKey, entity.RowKey)
            self._assert_default_entity_json_full_metadata(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey,
                headers={'accept': 'application/json;odata=nometadata'})

            # Assert
            self.assertEqual(resp.PartitionKey, entity.PartitionKey)
            self.assertEqual(resp.RowKey, entity.RowKey)
            self._assert_default_entity_json_no_metadata(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            with self.assertRaises(ResourceNotFoundError):
                await self.table.get_entity(partition_key=entity.PartitionKey,
                                            row_key=entity.RowKey)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_get_entity_with_special_doubles(self, resource_group, location, storage_account,
                                                   storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({
                'inf': float('inf'),
                'negativeinf': float('-inf'),
                'nan': float('nan')
            })
            await self.table.create_entity(entity=entity)

            # Act
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'])

            # Assert
            self.assertEqual(resp.inf, float('inf'))
            self.assertEqual(resp.negativeinf, float('-inf'))
            self.assertTrue(isnan(resp.nan))
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_update_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)

            # resp = self.table.update_item(sent_entity, response_hook=lambda e, h: h)
            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            #  self.assertTrue(resp)
            received_entity = await self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey)

            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_update_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with self.assertRaises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_update_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.update_entity(
                mode=UpdateMode.REPLACE,
                entity=sent_entity, etag=etag,
                match_condition=MatchConditions.IfNotModified)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_update_entity_with_if_doesnt_match(self, resource_group, location, storage_account,
                                                      storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with self.assertRaises(HttpResponseError):
                await self.table.update_entity(
                    mode=UpdateMode.REPLACE,
                    entity=sent_entity,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_or_merge_entity_with_existing_entity(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_or_merge_entity_with_non_existing_entity(self, resource_group, location, storage_account,
                                                                   storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_or_replace_entity_with_existing_entity(self, resource_group, location, storage_account,
                                                                 storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_insert_or_replace_entity_with_non_existing_entity(self, resource_group, location, storage_account,
                                                                     storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self.assertIsNotNone(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_merge_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_merge_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with self.assertRaises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_merge_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.update_entity(mode=UpdateMode.MERGE,
                                                  entity=sent_entity, etag=etag,
                                                  match_condition=MatchConditions.IfNotModified)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_merge_entity_with_if_doesnt_match(self, resource_group, location, storage_account,
                                                     storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with self.assertRaises(HttpResponseError):
                await self.table.update_entity(mode=UpdateMode.MERGE,
                                               entity=sent_entity,
                                               etag='W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                                               match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_delete_entity(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)

            # Assert
            self.assertIsNone(resp)
            with self.assertRaises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_delete_entity_not_existing(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            with self.assertRaises(ResourceNotFoundError):
                await self.table.delete_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_delete_entity_with_if_matches(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(entity.PartitionKey, entity.RowKey, etag=etag,
                                                  match_condition=MatchConditions.IfNotModified)

            # Assert
            self.assertIsNone(resp)
            with self.assertRaises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_delete_entity_with_if_doesnt_match(self, resource_group, location, storage_account,
                                                      storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with self.assertRaises(HttpResponseError):
                await self.table.delete_entity(
                    entity.PartitionKey, entity.RowKey,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_unicode_property_value(self, resource_group, location, storage_account, storage_account_key):
        ''' regression test for github issue #57'''
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity1 = entity.copy()
            entity1.update({'Description': u'ꀕ'})
            entity2 = entity.copy()
            entity2.update({'RowKey': 'test2', 'Description': 'ꀕ'})

            # Act
            await self.table.create_entity(entity=entity1)
            await self.table.create_entity(entity=entity2)
            entities = []
            async for e in self.table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(e)

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].Description.value, u'ꀕ')
            self.assertEqual(entities[1].Description.value, u'ꀕ')
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_unicode_property_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity1 = entity.copy()
            entity1.update({u'啊齄丂狛狜': u'ꀕ'})
            entity2 = entity.copy()
            entity2.update({'RowKey': 'test2', u'啊齄丂狛狜': 'hello'})

            # Act
            await self.table.create_entity(entity=entity1)
            await self.table.create_entity(entity=entity2)
            entities = []
            async for e in self.table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(e)

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0][u'啊齄丂狛狜'].value, u'ꀕ')
            self.assertEqual(entities[1][u'啊齄丂狛狜'].value, u'hello')
        finally:
            await self._tear_down()

    @pytest.mark.skip("Authentication and conflict error")
    @GlobalStorageAccountPreparer()
    async def test_operations_on_entity_with_partition_key_having_single_quote(self, resource_group, location,
                                                                               storage_account, storage_account_key):

        # Arrange
        partition_key_with_single_quote = "a''''b"
        row_key_with_single_quote = "a''''b"
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity(pk=partition_key_with_single_quote,
                                                         rk=row_key_with_single_quote)

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            self._assert_valid_metadata(resp)
            # row key here only has 2 quotes
            received_entity = await self.table.get_entity(
                entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)

            # Act
            sent_entity['newField'] = 'newFieldValue'
            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)
            received_entity = await self.table.get_entity(
                entity.PartitionKey, entity.RowKey)

            # Assert
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
            self.assertEqual(received_entity['newField'], 'newFieldValue')

            # Act
            resp = await self.table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            self.assertIsNone(resp)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_empty_and_spaces_property_value(self, resource_group, location, storage_account,
                                                   storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({
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

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertEqual(resp.EmptyByte.value, '')
            self.assertEqual(resp.EmptyUnicode.value, u'')
            self.assertEqual(resp.SpacesOnlyByte.value, '   ')
            self.assertEqual(resp.SpacesOnlyUnicode.value, u'   ')
            self.assertEqual(resp.SpacesBeforeByte.value, '   Text')
            self.assertEqual(resp.SpacesBeforeUnicode.value, u'   Text')
            self.assertEqual(resp.SpacesAfterByte.value, 'Text   ')
            self.assertEqual(resp.SpacesAfterUnicode.value, u'Text   ')
            self.assertEqual(resp.SpacesBeforeAndAfterByte.value, '   Text   ')
            self.assertEqual(resp.SpacesBeforeAndAfterUnicode.value, u'   Text   ')
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_none_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({'NoneValue': None})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertFalse(hasattr(resp, 'NoneValue'))
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_binary_property_value(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
            entity = self._create_random_base_entity_dict()
            entity.update({'binary': b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            self.assertEqual(resp.binary.value, binary_data)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_timezone(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            local_tz = tzoffset('BRST', -10800)
            local_date = datetime(2003, 9, 27, 9, 52, 43, tzinfo=local_tz)
            entity = self._create_random_base_entity_dict()
            entity.update({'date': local_date})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            self.assertIsNotNone(resp)
            # times are not equal because request is made after
        #  self.assertEqual(resp.date.astimezone(tzutc()), local_date.astimezone(tzutc()))
        # self.assertEqual(resp.date.astimezone(local_tz), local_date)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities():
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity(entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_zero_entities(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(0)

            # Act
            entities = []
            async for t in table.list_entities():
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 0)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities_full_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities(headers={'accept': 'application/json;odata=fullmetadata'}):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity_json_full_metadata(entity)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities_no_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities(headers={'accept': 'application/json;odata=nometadata'}):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 2)
            for entity in entities:
                self._assert_default_entity_json_no_metadata(entity)
        finally:
            await self._tear_down()

    # TODO: move this over to the batch test file when merged
    @pytest.mark.skip("Batch not implemented")
    @GlobalStorageAccountPreparer()
    def test_query_entities_large(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        table_name = self._create_query_table(0)
        total_entities_count = 1000
        entities_per_batch = 50

        for j in range(total_entities_count // entities_per_batch):
            batch = TableBatch()
            for i in range(entities_per_batch):
                entity = TableEntity()
                entity.PartitionKey = 'large'
                entity.RowKey = 'batch{0}-item{1}'.format(j, i)
                entity.test = EntityProperty(True)
                entity.test2 = 'hello world;' * 100
                entity.test3 = 3
                entity.test4 = EntityProperty(1234567890)
                entity.test5 = datetime(2016, 12, 31, 11, 59, 59, 0)
                batch.create_entity(entity)
            self.ts.commit_batch(table_name, batch)

        # Act
        start_time = datetime.now()
        entities = list(self.ts.query_entities(table_name))
        elapsed_time = datetime.now() - start_time

        # Assert
        print('query_entities took {0} secs.'.format(elapsed_time.total_seconds()))
        # azure allocates 5 seconds to execute a query
        # if it runs slowly, it will return fewer results and make the test fail
        self.assertEqual(len(entities), total_entities_count)


    @GlobalStorageAccountPreparer()
    async def test_query_entities_with_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            entities = []
            async for t in self.table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity.PartitionKey)):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 1)
            self.assertEqual(entity.PartitionKey, entities[0].PartitionKey)
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities_with_select(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities(select=["age, sex"]):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 2)
            self.assertEqual(entities[0].age.value, 39)
            self.assertEqual(entities[0].sex.value, 'male')
            self.assertFalse(hasattr(entities[0], "birthday"))
            self.assertFalse(hasattr(entities[0], "married"))
            self.assertFalse(hasattr(entities[0], "deceased"))
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities_with_top(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(3)
            # circular dependencies made this return a list not an item paged - problem when calling by page
            # Act
            entities = []
            async for t in table.list_entities(results_per_page=2).by_page():
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 2)
        finally:
            await self._tear_down()


    @GlobalStorageAccountPreparer()
    async def test_query_entities_with_top_and_next(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # Arrange
        await self._set_up(storage_account, storage_account_key)
        try:
            table = await self._create_query_table(5)

            # Act
            resp1 = table.list_entities(results_per_page=2).by_page()
            entities1 = []
            async for el in await resp1.__anext__():
                entities1.append(el)
            resp2 = table.list_entities(results_per_page=2).by_page(
                continuation_token=resp1.continuation_token)
            entities2 = []
            async for el in await resp2.__anext__():
                entities2.append(el)
            resp3 = table.list_entities(results_per_page=2).by_page(
                continuation_token=resp2.continuation_token)
            entities3 = []
            async for el in await resp3.__anext__():
                entities3.append(el)

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
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_query(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")

        await self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
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
            entities = []
            async for t in table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_add(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
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
            await table.create_entity(entity=entity)

            # Assert
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_add_inside_range(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
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
            entity = self._create_random_entity_dict('test', 'test1')
            await table.create_entity(entity=entity)

            # Assert
            resp = await self.table.get_entity('test', 'test1')
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_add_outside_range(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
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
                await table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_update(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
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
            resp = await table.update_entity(mode=UpdateMode.REPLACE, entity=updated_entity)
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)

            # Assert
            self._assert_updated_entity(received_entity)
            self.assertIsNotNone(resp)

        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_delete(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
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
            await table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            with self.assertRaises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_upper_case_table_name(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()

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
            entities = []
            async for t in table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()


    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        await self._set_up(storage_account, storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()

            access_policy = AccessPolicy()
            access_policy.start = datetime(2011, 10, 11)
            access_policy.expiry = datetime(2020, 10, 12)
            access_policy.permission = TableSasPermissions(read=True)
            identifiers = {'testid': access_policy}

            await self.table.set_table_access_policy(identifiers)

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
            table = service.get_table_client(table_name=self.table_name)
            entities = []
            async for t in table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity.PartitionKey)):
                entities.append(t)

            # Assert
            self.assertEqual(len(entities), 1)
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
