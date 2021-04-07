# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from base64 import b64encode
from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzoffset
from math import isnan
from time import sleep
import uuid

from devtools_testutils import AzureTestCase

from azure.data.tables import (
    generate_table_sas,
    TableEntity,
    EntityProperty,
    EdmType,
    TableSasPermissions,
    AccessPolicy,
    UpdateMode
)
from azure.data.tables.aio import TableServiceClient

from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
)

from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import SLEEP_DELAY
from preparers import CosmosPreparer
# ------------------------------------------------------------------------------
# TODO: change to `with table_client as client:` to close sessions
# ------------------------------------------------------------------------------

class StorageTableEntityTest(AzureTestCase, AsyncTableTestCase):

    async def _set_up(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        account_url = self.account_url(tables_cosmos_account_name, "cosmos")
        self.ts = TableServiceClient(account_url, tables_primary_cosmos_account_key)
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
            async with self.ts as t:
                try:
                    await t.delete_table(self.table_name)
                except:
                    pass

                for table_name in self.query_tables:
                    try:
                        await t.delete_table(table_name)
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

    def _create_pk_rk(self, pk, rk):
        try:
            pk = pk if pk is not None else self.get_resource_name('pk').decode('utf-8')
            rk = rk if rk is not None else self.get_resource_name('rk').decode('utf-8')
        except AttributeError:
            pk = pk if pk is not None else self.get_resource_name('pk')
            rk = rk if rk is not None else self.get_resource_name('rk')
        return pk, rk

    async def _insert_two_opposite_entities(self, pk=None, rk=None):
        entity1 = self._create_random_entity_dict()
        resp = await self.table.create_entity(entity1)

        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            'PartitionKey': partition + u'1',
            'RowKey': row + u'1',
            'age': 49,
            'sex': u'female',
            'married': False,
            'deceased': True,
            'optional': None,
            'ratio': 5.2,
            'evenratio': 6.0,
            'large': 39999011,
            'Birthday': datetime(1993, 4, 1, tzinfo=tzutc()),
            'birthday': datetime(1990, 4, 1, tzinfo=tzutc()),
            'binary': b'binary-binary',
            'other': EntityProperty(value=40, type=EdmType.INT32),
            'clsid': uuid.UUID('c8da6455-213e-42d9-9b79-3f9149a57833')
        }
        entity = TableEntity(**properties)
        await self.table.create_entity(entity)
        return entity1, resp

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
        assert entity['age'] ==  39
        assert entity['sex'] ==  'male'
        assert entity['married'] ==  True
        assert entity['deceased'] ==  False
        assert not "optional" in entity
        assert not "aquarius" in entity
        assert entity['ratio'] ==  3.1
        assert entity['evenratio'] ==  3.0
        assert entity['large'] ==  933311100
        assert entity['Birthday'] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity['birthday'] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity['binary'].value ==  b'binary'
        assert entity['other'] ==  20
        assert entity['clsid'] ==  uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')

    def _assert_default_entity_json_full_metadata(self, entity, headers=None):
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
        assert entity['Birthday'] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity['birthday'] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity['binary'].value ==  b'binary'
        assert entity['other'] ==  20
        assert entity['clsid'] ==  uuid.UUID('c9da6455-213d-42c9-9a79-3e9149a57833')

    def _assert_default_entity_json_no_metadata(self, entity, headers=None):
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
        assert entity['Birthday'].startswith('1973-10-04T00:00:00')
        assert entity['birthday'].startswith('1970-10-04T00:00:00')
        assert entity['Birthday'].endswith('00Z')
        assert entity['birthday'].endswith('00Z')
        assert entity['binary'] ==  b64encode(b'binary').decode('utf-8')
        assert entity['other'] ==  20
        assert entity['clsid'] ==  'c9da6455-213d-42c9-9a79-3e9149a57833'

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

    def _assert_merged_entity(self, entity):
        '''
        Asserts that the entity passed in matches the default entity
        merged with the updated entity.
        '''
        assert entity.age ==  'abc'
        assert entity.sex ==  'female'
        assert entity.sign ==  'aquarius'
        assert entity.married ==  True
        assert entity.deceased ==  False
        assert entity.ratio ==  3.1
        assert entity.evenratio ==  3.0
        assert entity.large ==  933311100
        assert entity.Birthday, datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity.birthday, datetime(1991, 10, 4, tzinfo=tzutc())
        assert entity.other ==  20
        assert isinstance(entity.clsid,  uuid.UUID)
        assert str(entity.clsid) ==  'c9da6455-213d-42c9-9a79-3e9149a57833'

    def _assert_valid_metadata(self, metadata):
        keys = metadata.keys()
        assert "version" in  keys
        assert "date" in  keys
        assert "etag" in  keys
        assert len(keys) ==  3

    # --Test cases for entities ------------------------------------------
    @pytest.mark.skip("Forbidden operation")
    @CosmosPreparer()
    async def test_url_encoding_at_symbol(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):

        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = {
                u"PartitionKey": u"PK",
                u"RowKey": u"table@storage.com",
                u"Value": 100
            }

            await self.table.create_entity(entity)

            f = u"RowKey eq '{}'".format(entity["RowKey"])
            entities = self.table.query_entities(filter=f)

            count = 0
            async for e in entities:
                assert e.PartitionKey == entity[u"PartitionKey"]
                assert e.RowKey == entity[u"RowKey"]
                assert e.Value == entity[u"Value"]
                await self.table.delete_entity(e.PartitionKey, e.RowKey)
                count += 1

            assert count == 1

            entities = self.table.query_entities(filter=f)
            count = 0
            async for e in entities:
                count += 1
            assert count == 0

        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_insert_entity_dictionary(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            # resp = self.table.create_item(entity)
            resp = await self.table.create_entity(entity=entity)

            # Assert  --- Does this mean insert returns nothing?
            assert resp is not None
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_hook(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_no_metadata(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=nometadata'}

            # Act
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_full_metadata(self, tables_cosmos_account_name,
                                                    tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()
            headers = {'Accept': 'application/json;odata=fullmetadata'}

            # Act
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_conflict(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with pytest.raises(ResourceExistsError):
                # self.table.create_item(entity)
                await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_large_int32_value_throws(self, tables_cosmos_account_name,
                                                               tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            dict32 = self._create_random_base_entity_dict()
            dict32['large'] = EntityProperty(2 ** 31, EdmType.INT32) # TODO: this is outside the range of int32

            # Assert
            with pytest.raises(TypeError):
                await self.table.create_entity(entity=dict32)

            dict32['large'] = EntityProperty(-(2 ** 31 + 1), EdmType.INT32)  # TODO: this is outside the range of int32
            with pytest.raises(TypeError):
                await self.table.create_entity(entity=dict32)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_large_int64_value_throws(self, tables_cosmos_account_name,
                                                               tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 63, EdmType.INT64)

            # Assert
            with pytest.raises(TypeError):
                await self.table.create_entity(entity=dict64)

            dict64['large'] = EntityProperty(-(2 ** 63 + 1), EdmType.INT64)
            with pytest.raises(TypeError):
                await self.table.create_entity(entity=dict64)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_with_large_int_success(self, tables_cosmos_account_name,
                                                         tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 50, EdmType.INT64)

            # Assert
            await self.table.create_entity(entity=dict64)

            received_entity = await self.table.get_entity(dict64['PartitionKey'], dict64['RowKey'])
            assert received_entity['large'].value == dict64['large'].value

            dict64['RowKey'] = 'negative'
            dict64['large'] = EntityProperty(-(2 ** 50 + 1), EdmType.INT64)
            await self.table.create_entity(entity=dict64)

            received_entity = await self.table.get_entity(dict64['PartitionKey'], dict64['RowKey'])
            assert received_entity['large'].value == dict64['large'].value

        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_missing_pk(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = {'RowKey': 'rk'}

            # Act
            with pytest.raises(ValueError):
                # resp = self.table.create_item(entity)
                resp = await self.table.create_entity(entity=entity)
            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_empty_string_pk(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = {'RowKey': 'rk', 'PartitionKey': ''}

            # Act
            with pytest.raises(HttpResponseError):
                await self.table.create_entity(entity=entity)

                # Assert
            #  assert resp is None
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_missing_rk(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = {'PartitionKey': 'pk'}

            # Act
            with pytest.raises(ValueError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_insert_entity_empty_string_rk(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = {'PartitionKey': 'pk', 'RowKey': ''}

            # Act
            with pytest.raises(HttpResponseError):
                await self.table.create_entity(entity=entity)

                # Assert
            #  assert resp is None
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos does not have this limitation")
    @CosmosPreparer()
    async def test_insert_entity_too_many_properties(self, tables_cosmos_account_name,
                                                     tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            for i in range(255):
                entity['key{0}'.format(i)] = 'value{0}'.format(i)

            # Act
            with pytest.raises(HttpResponseError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos does not have this limitation")
    @CosmosPreparer()
    async def test_insert_entity_property_name_too_long(self, tables_cosmos_account_name,
                                                        tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity['a' * 256] = 'badval'

            # Act
            with pytest.raises(HttpResponseError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'])

            # Assert
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_with_hook(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_if_match(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_full_metadata(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                entity.PartitionKey,
                entity.RowKey,
                headers={'accept': 'application/json;odata=fullmetadata'})

            # Assert
            assert resp.PartitionKey ==  entity.PartitionKey
            assert resp.RowKey ==  entity.RowKey
            self._assert_default_entity_json_full_metadata(resp)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_no_metadata(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey,
                headers={'accept': 'application/json;odata=nometadata'})

            # Assert
            assert resp.PartitionKey ==  entity.PartitionKey
            assert resp.RowKey ==  entity.RowKey
            self._assert_default_entity_json_no_metadata(resp)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_not_existing(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(partition_key=entity.PartitionKey,
                                            row_key=entity.RowKey)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_get_entity_with_special_doubles(self, tables_cosmos_account_name,
                                                   tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            assert resp.inf ==  float('inf')
            assert resp.negativeinf ==  float('-inf')
            assert isnan(resp.nan)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_update_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)

            # resp = self.table.update_item(sent_entity, response_hook=lambda e, h: h)
            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            #  assert resp
            received_entity = await self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey)

            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_update_entity_not_existing(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_update_entity_with_if_matches(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            #, response_hook=lambda e, h: h)
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            await self.table.update_entity(
                mode=UpdateMode.REPLACE,
                entity=sent_entity, etag=etag,
                match_condition=MatchConditions.IfNotModified)

            # Assert
            # assert resp
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_update_entity_with_if_doesnt_match(self, tables_cosmos_account_name,
                                                      tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with pytest.raises(HttpResponseError):
                await self.table.update_entity(
                    mode=UpdateMode.REPLACE,
                    entity=sent_entity,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_insert_or_merge_entity_with_existing_entity(self, tables_cosmos_account_name,
                                                               tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_insert_or_merge_entity_with_non_existing_entity(self, tables_cosmos_account_name,
                                                                   tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_insert_or_replace_entity_with_existing_entity(self, tables_cosmos_account_name,
                                                                 tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            # assert resp is None
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_insert_or_replace_entity_with_non_existing_entity(self, tables_cosmos_account_name,
                                                                     tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_merge_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_merge_entity_not_existing(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_merge_entity_with_if_matches(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.update_entity(mode=UpdateMode.MERGE,
                                                  entity=sent_entity, etag=etag,
                                                  match_condition=MatchConditions.IfNotModified)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Merge operation fails from Tables SDK, issue #13844")
    @CosmosPreparer()
    async def test_merge_entity_with_if_doesnt_match(self, tables_cosmos_account_name,
                                                     tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with pytest.raises(HttpResponseError):
                await self.table.update_entity(mode=UpdateMode.MERGE,
                                               entity=sent_entity,
                                               etag='W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                                               match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_delete_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_delete_entity_not_existing(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            with pytest.raises(ResourceNotFoundError):
                await self.table.delete_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_delete_entity_with_if_matches(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(entity.PartitionKey, entity.RowKey, etag=etag,
                                                  match_condition=MatchConditions.IfNotModified)

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_delete_entity_with_if_doesnt_match(self, tables_cosmos_account_name,
                                                      tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with pytest.raises(HttpResponseError):
                await self.table.delete_entity(
                    entity.PartitionKey, entity.RowKey,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_unicode_property_value(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        ''' regression test for github issue #57'''
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            assert len(entities) ==  2
            assert entities[0].Description ==  u'ꀕ'
            assert entities[1].Description ==  u'ꀕ'
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_unicode_property_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            assert len(entities) ==  2
            assert entities[0][u'啊齄丂狛狜'] ==  u'ꀕ'
            assert entities[1][u'啊齄丂狛狜'] ==  u'hello'
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Bad Request: Cosmos cannot handle single quotes in a PK/RK (confirm)")
    @CosmosPreparer()
    async def test_operations_on_entity_with_partition_key_having_single_quote(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        partition_key_with_single_quote = "a''''b"
        row_key_with_single_quote = "a''''b"
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity(pk=partition_key_with_single_quote,
                                                         rk=row_key_with_single_quote)

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            assert resp is None
            # row key here only has 2 quotes
            received_entity = await self.table.get_entity(
                entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)

            # Act
            sent_entity['newField'] = 'newFieldValue'
            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            assert resp is None
            received_entity = await self.table.get_entity(
                entity.PartitionKey, entity.RowKey)
            self._assert_updated_entity(received_entity)
            assert received_entity['newField'] ==  'newFieldValue'

            # Act
            resp = await self.table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            assert resp is None
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_empty_and_spaces_property_value(self, tables_cosmos_account_name,
                                                   tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
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
            assert resp is not None
            assert resp.EmptyByte ==  ''
            assert resp.EmptyUnicode ==  u''
            assert resp.SpacesOnlyByte ==  '   '
            assert resp.SpacesOnlyUnicode ==  u'   '
            assert resp.SpacesBeforeByte ==  '   Text'
            assert resp.SpacesBeforeUnicode ==  u'   Text'
            assert resp.SpacesAfterByte ==  'Text   '
            assert resp.SpacesAfterUnicode ==  u'Text   '
            assert resp.SpacesBeforeAndAfterByte ==  '   Text   '
            assert resp.SpacesBeforeAndAfterUnicode ==  u'   Text   '
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_none_property_value(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({'NoneValue': None})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert not hasattr(resp, 'NoneValue')
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_binary_property_value(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
            entity = self._create_random_base_entity_dict()
            entity.update({'binary': b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert resp.binary.value ==  binary_data
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("response time is three hours before the given one")
    @CosmosPreparer()
    async def test_timezone(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            local_tz = tzoffset('BRST', -10800)
            local_date = datetime(2003, 9, 27, 9, 52, 43, tzinfo=local_tz)
            entity = self._create_random_base_entity_dict()
            entity.update({'date': local_date})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            # times are not equal because request is made after
        #  assert resp.date.astimezone(tzutc()) ==  local_date.astimezone(tzutc())
        # assert resp.date.astimezone(local_tz) ==  local_date
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(2) as table:

                # Act
                entities = []
                async for t in table.list_entities():
                    entities.append(t)

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity(entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_each_page(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            base_entity = {
                "PartitionKey": u"pk",
                "RowKey": u"1",
            }

            for i in range(10):
                if i > 5:
                    base_entity['PartitionKey'] += str(i)
                base_entity['RowKey'] += str(i)
                base_entity['value'] = i
                try:
                    await self.table.create_entity(base_entity)
                except ResourceExistsError:
                    pass

            query_filter = u"PartitionKey eq 'pk'"

            entity_count = 0
            page_count = 0
            async for entity_page in self.table.query_entities(filter=query_filter, results_per_page=2).by_page():

                temp_count = 0
                async for ent in entity_page:
                    temp_count += 1

                assert temp_count <= 2
                page_count += 1
                entity_count += temp_count

            assert entity_count == 6
            assert page_count == 3

        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = await self._insert_two_opposite_entities()

            # Act
            entities = self.table.query_entities(filter="married eq @my_param", parameters={'my_param': True})

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1

        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter_multiple_params(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': True,
                'rk': entity['RowKey']
            }
            entities = self.table.query_entities(filter="married eq @my_param and RowKey eq @rk", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter_integers(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': 40,
            }
            entities = self.table.query_entities(filter="age lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter_floats(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['ratio'] + 1.0,
            }
            entities = self.table.query_entities(filter="ratio lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter_datetimes(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['birthday'],
            }
            entities = self.table.query_entities(filter="birthday eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_user_filter_guids(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['clsid']
            }
            entities = self.table.query_entities(filter="clsid eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_zero_entities(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(0) as table:

                # Act
                entities = []
                async for t in table.list_entities():
                    entities.append(t)

            # Assert
            assert len(entities) ==  0
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_full_metadata(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(2) as table:

                # Act
                entities = []
                async for t in table.list_entities(headers={'accept': 'application/json;odata=fullmetadata'}):
                    entities.append(t)

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity_json_full_metadata(entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_no_metadata(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(2) as table:

                # Act
                entities = []
                async for t in table.list_entities(headers={'accept': 'application/json;odata=nometadata'}):
                    entities.append(t)

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity_json_no_metadata(entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_with_filter(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity, _ = await self._insert_random_entity()
            entity2, _ = await self._insert_random_entity(pk="foo" + entity.PartitionKey)
            entity3, _ = await self._insert_random_entity(pk="bar" + entity.PartitionKey)

            # Act
            entities = []
            async for t in self.table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity.PartitionKey)):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            assert entity.PartitionKey ==  entities[0].PartitionKey
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_injection_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            table_name = self.get_resource_name('querytable')
            table = await self.ts.create_table_if_not_exists(table_name)
            entity_a = {'PartitionKey': 'foo', 'RowKey': 'bar1', 'IsAdmin': 'admin'}
            entity_b = {'PartitionKey': 'foo', 'RowKey': 'bar2', 'IsAdmin': ''}
            await table.create_entity(entity_a)
            await table.create_entity(entity_b)

            is_user_admin = "PartitionKey eq @first and IsAdmin eq 'admin'"
            entity_query = table.query_entities(is_user_admin, parameters={'first': 'foo'})
            entities = []
            async for e in entity_query:
                entities.append(e)
            assert len(entities) ==  1

            injection = "foo' or RowKey eq 'bar2"
            injected_query = "PartitionKey eq '{}' and IsAdmin eq 'admin'".format(injection)
            entity_query = table.query_entities(injected_query)
            entities = []
            async for e in entity_query:
                entities.append(e)
            assert len(entities) ==  2

            entity_query = table.query_entities(is_user_admin, parameters={'first': injection})           
            entities = []
            async for e in entity_query:
                entities.append(e)
            assert len(entities) ==  0
        finally:
            await self.ts.delete_table(table_name)
            await self._tear_down()

    @CosmosPreparer()
    async def test_query_special_chars(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            table_name = self.get_resource_name('querytable')
            table = await self.ts.create_table_if_not_exists(table_name)
            entity_a = {'PartitionKey': u'foo', 'RowKey': u'bar1', 'Chars': u":@?'/!_^#+,$"}
            entity_b = {'PartitionKey': u'foo', 'RowKey': u'bar2', 'Chars': u'=& ?"\\{}<>%'}
            await table.create_entity(entity_a)
            await table.create_entity(entity_b)

            entities = []
            all_entities = table.query_entities("PartitionKey eq 'foo'")
            async for e in all_entities:
                entities.append(e)
            assert len(entities) == 2
        
            entities = []
            parameters = {'key': 'foo'}
            all_entities = table.query_entities("PartitionKey eq @key", parameters=parameters)
            async for e in all_entities:
                entities.append(e)
            assert len(entities) == 2
            
            entities = []
            query = "PartitionKey eq 'foo' and RowKey eq 'bar1' and Chars eq ':@?''/!_^#+,$'"
            query_entities = table.query_entities(query)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq @key and RowKey eq @row and Chars eq @quote"
            parameters = {'key': 'foo', 'row': 'bar1', 'quote': ":@?'/!_^#+,$"}
            query_entities = table.query_entities(query, parameters=parameters)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq 'foo' and RowKey eq 'bar2' and Chars eq '=& ?\"\\{}<>%'"
            query_entities = table.query_entities(query)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq @key and RowKey eq @row and Chars eq @quote"
            parameters = {'key': 'foo', 'row': 'bar2', 'quote': r'=& ?"\{}<>%'}
            query_entities = table.query_entities(query, parameters=parameters)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

        finally:
            await self.ts.delete_table(table_name)
            await self._tear_down()

    @CosmosPreparer()
    async def test_query_invalid_filter(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            base_entity = {
                u"PartitionKey": u"pk",
                u"RowKey": u"rk",
                u"value": 1
            }

            for i in range(5):
                base_entity[u"RowKey"] += str(i)
                base_entity[u"value"] += i
                await self.table.create_entity(base_entity)
            # Act
            with pytest.raises(HttpResponseError):
                async for t in self.table.query_entities(filter="aaa bbb ccc"):
                    _ = t
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("returns ' sex' instead of deserializing into just 'sex'")
    @CosmosPreparer()
    async def test_query_entities_with_select(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities(select=["age, sex"]):
                entities.append(t)

            # Assert
            assert len(entities) ==  2
            assert entities[0].age ==  39
            assert entities[0].sex ==  'male'
            assert not hasattr(entities[0], "birthday")
            assert not hasattr(entities[0], "married")
            assert not hasattr(entities[0], "deceased")
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_with_top(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(3) as table:

                entities = []
                async for t in table.list_entities(results_per_page=2).by_page():
                    entities.append(t)
            # Assert
            assert len(entities) ==  2
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_query_entities_with_top_and_next(self, tables_cosmos_account_name,
                                                    tables_primary_cosmos_account_key):
        # Arrange
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            async with await self._create_query_table(5) as table:

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
            assert len(entities1) ==  2
            assert len(entities2) ==  2
            assert len(entities3) ==  1
            self._assert_default_entity(entities1[0])
            self._assert_default_entity(entities1[1])
            self._assert_default_entity(entities2[0])
            self._assert_default_entity(entities2[1])
            self._assert_default_entity(entities3[0])
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_query(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")

        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entities = []
            async for t in table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)


    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_add(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_add_inside_range(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk='test', start_rk='test1',
                end_pk='test', end_rk='test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
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
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_add_outside_range(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk='test', start_rk='test1',
                end_pk='test', end_rk='test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            with pytest.raises(HttpResponseError):
                entity = self._create_random_entity_dict()
                await table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_update(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(update=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            updated_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            await table.update_entity(mode=UpdateMode.REPLACE, entity=updated_entity)

            # Assert
            received_entity = await self.table.get_entity(entity.PartitionKey,
                                                          entity.RowKey)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_delete(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            await table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @pytest.mark.skip("Cosmos Tables does not yet support sas")
    @pytest.mark.live_test_only
    @CosmosPreparer()
    async def test_sas_upper_case_table_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()

            # Table names are case insensitive, so simply upper case our existing table name to test
            token = generate_table_sas(
                tables_cosmos_account_name,
                tables_primary_cosmos_account_key,
                self.table_name.upper(),
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)
            entities = []
            async for t in table.query_entities(
                    filter="PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()
            if self.is_live:
                sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_datetime_milliseconds(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        try:
            entity = self._create_random_entity_dict()

            entity['milliseconds'] = datetime(2011, 11, 4, 0, 5, 23, 283000, tzinfo=tzutc())

            await self.table.create_entity(entity)

            received_entity = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey']
            )

            assert entity['milliseconds'] == received_entity['milliseconds']

        finally:
            await self._tear_down()
            self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    async def test_datetime_str_passthrough(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        await self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key)
        partition, row = self._create_pk_rk(None, None)

        dotnet_timestamp = "2013-08-22T01:12:06.2608595Z"
        entity = {
            'PartitionKey': partition,
            'RowKey': row,
            'datetime1': EntityProperty(dotnet_timestamp, EdmType.DATETIME)
        }
        try:
            await self.table.create_entity(entity)
            received = await self.table.get_entity(partition, row)
            assert isinstance(received['datetime1'], datetime)
            assert received.datetime1.tables_service_value == dotnet_timestamp

            received['datetime2'] = received.datetime1.replace(year=2020)
            assert received['datetime2'].tables_service_value == ""

            await self.table.update_entity(received, mode=UpdateMode.REPLACE)
            updated = await self.table.get_entity(partition, row)
            assert isinstance(updated['datetime1'], datetime)
            assert isinstance(updated['datetime2'], datetime)
            assert updated.datetime1.tables_service_value == dotnet_timestamp
        finally:
            await self._tear_down()