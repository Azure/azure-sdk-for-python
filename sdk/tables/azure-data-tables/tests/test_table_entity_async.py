# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from uuid import UUID
import pytest

from datetime import datetime, timedelta
from dateutil.tz import tzutc, tzoffset
from math import isnan

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ResourceModifiedError
)

from azure.data.tables import (
    TableSasPermissions,
    TableAccessPolicy,
    UpdateMode,
    generate_table_sas,
    TableEntity,
    EntityProperty,
    EdmType
)
from azure.data.tables.aio import TableServiceClient
from azure.data.tables._common_conversion import TZ_UTC

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async

TEST_GUID = UUID("1ca72025-f78c-437d-87df-9bcf0dd0d297")

class TestTableEntityAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_url_encoding_at_symbol(self, tables_storage_account_name, tables_primary_storage_account_key):

        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {
                u"PartitionKey": u"PK",
                u"RowKey": u"table@storage.com",
                u"Value": 100
            }

            await self.table.create_entity(entity)

            f = u"RowKey eq '{}'".format(entity["RowKey"])
            entities = self.table.query_entities(f)

            count = 0
            async for e in entities:
                assert e['PartitionKey'] == entity[u"PartitionKey"]
                assert e['RowKey'] == entity[u"RowKey"]
                assert e['Value'] == entity[u"Value"]
                await self.table.delete_entity(e['PartitionKey'], e['RowKey'])
                count += 1

            assert count == 1

            entities = self.table.query_entities(f)
            count = 0
            async for e in entities:
                count += 1
            assert count == 0

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_dictionary(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = await self.table.create_entity(entity=entity)

            # Assert
            assert resp is not None
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_hook(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_full_metadata(self, tables_storage_account_name,
                                                    tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_conflict(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with pytest.raises(ResourceExistsError):
                # self.table.create_entity(entity)
                await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_large_int32_value_throws(self, tables_storage_account_name,
                                                               tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_large_int64_value_throws(self, tables_storage_account_name,
                                                               tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_with_large_int_success(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_missing_pk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'RowKey': 'rk'}

            # Act
            with pytest.raises(ValueError) as error:
                resp = await self.table.create_entity(entity=entity)
                assert str(error).contains("PartitionKey must be present in an entity")
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_empty_string_pk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'RowKey': 'rk', 'PartitionKey': ''}

            # Act
            resp = await self.table.create_entity(entity=entity)
            self._assert_valid_metadata(resp)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_missing_rk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'PartitionKey': 'pk'}

            # Act
            with pytest.raises(ValueError) as error:
                resp = await self.table.create_entity(entity=entity)
                assert str(error).contains("PartitionKey must be present in an entity")
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_empty_string_rk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'PartitionKey': 'pk', 'RowKey': ''}

            # Act
            resp = await self.table.create_entity(entity=entity)
            self._assert_valid_metadata(resp)

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_too_many_properties(self, tables_storage_account_name,
                                                     tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_entity_property_name_too_long(self, tables_storage_account_name,
                                                        tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity['a' * 256] = 'badval'

            # Act
            with pytest.raises(HttpResponseError):
                resp = await self.table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_with_select(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'],
                                               select=['age', 'ratio'])
            resp.pop('_metadata', None)
            assert resp == {'age': 39, 'ratio': 3.1}
            resp = await self.table.get_entity(partition_key=entity['PartitionKey'],
                                               row_key=entity['RowKey'],
                                               select='age,ratio')
            resp.pop('_metadata', None)
            assert resp == {'age': 39, 'ratio': 3.1}

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_with_hook(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_if_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            entity = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey']
            )

            await self.table.delete_entity(
                entity,
                etag=etag,
                match_condition=MatchConditions.IfNotModified
            )

            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(
                    partition_key=entity['PartitionKey'],
                    row_key=entity['RowKey']
                )
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_if_match_entity_bad_etag(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, old_etag = await self._insert_random_entity()

            entity["value"] = 10
            await self.table.update_entity(entity)

            # Get Entity and set old etag
            e = await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            new_etag = e.metadata["etag"]
            e.metadata["etag"] = old_etag

            with pytest.raises(ResourceModifiedError):
                await self.table.delete_entity(e, match_condition=MatchConditions.IfNotModified)

            # Try delete with correct etag
            await self.table.delete_entity(e, etag=new_etag, match_condition=MatchConditions.IfNotModified)

        finally:
            await self._tear_down()
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_if_match_table_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()
            table_entity = TableEntity(**entity)

            entity = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey']
            )

            with pytest.raises(ValueError):
                await self.table.delete_entity(table_entity, match_condition=MatchConditions.IfNotModified)

            await self.table.delete_entity(table_entity, etag=etag, match_condition=MatchConditions.IfNotModified)

            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_full_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                entity['PartitionKey'],
                entity['RowKey'],
                headers={'accept': 'application/json;odata=fullmetadata'})

            # Assert
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity_json_full_metadata(resp)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey'],
                headers={'accept': 'application/json;odata=nometadata'})

            # Assert
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity_json_no_metadata(resp)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(partition_key=entity['PartitionKey'],
                                            row_key=entity['RowKey'])

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_entity_with_special_doubles(self, tables_storage_account_name,
                                                   tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert resp['inf'] ==  float('inf')
            assert resp['negativeinf'] ==  float('-inf')
            assert isnan(resp['nan'])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_update_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])

            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey'])

            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_update_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_update_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.update_entity(
                mode=UpdateMode.REPLACE,
                entity=sent_entity, etag=etag,
                match_condition=MatchConditions.IfNotModified)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_update_entity_with_if_doesnt_match(self, tables_storage_account_name,
                                                      tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceModifiedError):
                await self.table.update_entity(
                    mode=UpdateMode.REPLACE,
                    entity=sent_entity,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_or_merge_entity_with_existing_entity(self, tables_storage_account_name,
                                                               tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_or_merge_entity_with_non_existing_entity(self, tables_storage_account_name,
                                                                   tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_or_replace_entity_with_existing_entity(self, tables_storage_account_name,
                                                                 tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_insert_or_replace_entity_with_non_existing_entity(self, tables_storage_account_name,
                                                                     tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            assert resp is not None
            self._assert_updated_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_merge_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_merge_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_merge_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.update_entity(mode=UpdateMode.MERGE,
                                                  entity=sent_entity, etag=etag,
                                                  match_condition=MatchConditions.IfNotModified)

            # Assert
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])
            self._assert_valid_metadata(resp)
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_merge_entity_with_if_doesnt_match(self, tables_storage_account_name,
                                                     tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceModifiedError):
                await self.table.update_entity(mode=UpdateMode.MERGE,
                                               entity=sent_entity,
                                               etag='W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                                               match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(partition_key=entity['PartitionKey'], row_key=entity['RowKey'])

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            await self.table.delete_entity(entity['PartitionKey'], entity['RowKey'])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = await self._insert_random_entity()

            # Act
            resp = await self.table.delete_entity(
                entity['PartitionKey'],
                entity['RowKey'],
                etag=etag,
                match_condition=MatchConditions.IfNotModified
            )

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_with_if_doesnt_match(self, tables_storage_account_name,
                                                      tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            with pytest.raises(ResourceModifiedError):
                await self.table.delete_entity(
                    entity['PartitionKey'],
                    entity['RowKey'],
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified
                )

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_overloads(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            await self.table.delete_entity(entity)

            pk, rk = self._create_pk_rk("pk", "rk")
            pk, rk = pk + u"2", rk + u"2"
            entity2 = {
                u"PartitionKey": pk,
                u"RowKey": rk,
                u"Value": 100
            }
            await self.table.create_entity(entity2)

            await self.table.delete_entity(pk, rk)

            count = 0
            async for entity in self.table.list_entities():
                count += 1
            assert count == 0
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_entity_overloads_kwargs(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()

            # Act
            await self.table.delete_entity(entity=entity)

            pk, rk = self._create_pk_rk("pk", "rk")
            pk, rk = pk + u"2", rk + u"2"
            entity2 = {
                u"PartitionKey": pk,
                u"RowKey": rk,
                u"Value": 100
            }
            await self.table.create_entity(entity2)

            await self.table.delete_entity(partition_key=pk, row_key=rk)

            count = 0
            async for entity in self.table.list_entities():
                count += 1
            assert count == 0
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_unicode_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        ''' regression test for github issue #57'''
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(e)

            # Assert
            assert len(entities) ==  2
            assert entities[0]['Description'] ==  u'ꀕ'
            assert entities[1]['Description'] ==  u'ꀕ'
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_unicode_property_name(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(e)

            # Assert
            assert len(entities) ==  2
            assert entities[0][u'啊齄丂狛狜'] ==  u'ꀕ'
            assert entities[1][u'啊齄丂狛狜'] ==  u'hello'
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_operations_on_entity_with_partition_key_having_single_quote(self, tables_storage_account_name, tables_primary_storage_account_key):
        partition_key_with_single_quote = u"a''''b"
        row_key_with_single_quote = u"a''''b"
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity(pk=partition_key_with_single_quote,
                                                         rk=row_key_with_single_quote)

            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await self.table.upsert_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            self._assert_valid_metadata(resp)
            received_entity = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_updated_entity(received_entity)

            sent_entity['newField'] = u'newFieldValue'
            resp = await self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            self._assert_valid_metadata(resp)
            received_entity = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            self._assert_updated_entity(received_entity)
            assert received_entity['newField'] ==  'newFieldValue'
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_empty_and_spaces_property_value(self, tables_storage_account_name,
                                                   tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert resp['EmptyByte'] ==  b''
            assert resp['EmptyUnicode'] ==  u''
            assert resp['SpacesOnlyByte'] ==  b'   '
            assert resp['SpacesOnlyUnicode'] ==  u'   '
            assert resp['SpacesBeforeByte'] ==  b'   Text'
            assert resp['SpacesBeforeUnicode'] ==  u'   Text'
            assert resp['SpacesAfterByte'] ==  b'Text   '
            assert resp['SpacesAfterUnicode'] ==  u'Text   '
            assert resp['SpacesBeforeAndAfterByte'] ==  b'   Text   '
            assert resp['SpacesBeforeAndAfterUnicode'] ==  u'   Text   '
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_none_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_binary_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
            entity = self._create_random_base_entity_dict()
            entity.update({'binary': b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'})

            # Act
            await self.table.create_entity(entity=entity)
            resp = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert resp['binary'] ==  binary_data
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_timezone(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert resp['date'].astimezone(tzutc()) ==  local_date.astimezone(tzutc())
            assert resp['date'].astimezone(local_tz) ==  local_date
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(2)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_each_page(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            async for entity_page in self.table.query_entities(query_filter, results_per_page=2).by_page():

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_injection_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table_name = self.get_resource_name('queryasynctable')
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_special_chars(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table_name = self.get_resource_name('querytable')
            table = await self.ts.create_table_if_not_exists(table_name)
            entity_a = {'PartitionKey': u':@', 'RowKey': u'+,$', 'Chars': u"?'/!_^#"}
            entity_b = {'PartitionKey': u':@', 'RowKey': u'=& ', 'Chars': u'?"\\{}<>%'}
            await table.create_entity(entity_a)
            await table.create_entity(entity_b)

            entities = []
            all_entities = table.query_entities("PartitionKey eq ':@'")
            async for e in all_entities:
                entities.append(e)
            assert len(entities) == 2

            entities = []
            parameters = {'key': ':@'}
            all_entities = table.query_entities("PartitionKey eq @key", parameters=parameters)
            async for e in all_entities:
                entities.append(e)
            assert len(entities) == 2

            entities = []
            query = "PartitionKey eq ':@' and RowKey eq '+,$' and Chars eq '?''/!_^#'"
            query_entities = table.query_entities(query)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq @key and RowKey eq @row and Chars eq @quote"
            parameters = {'key': ':@', 'row': '+,$', 'quote': "?'/!_^#"}
            query_entities = table.query_entities(query, parameters=parameters)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq ':@' and RowKey eq '=& ' and Chars eq '?\"\\{}<>%'"
            query_entities = table.query_entities(query)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

            entities = []
            query = "PartitionKey eq @key and RowKey eq @row and Chars eq @quote"
            parameters = {'key': ':@', 'row': '=& ', 'quote': r'?"\{}<>%'}
            query_entities = table.query_entities(query, parameters=parameters)
            async for e in query_entities:
                entities.append(e)
            assert len(entities) == 1

        finally:
            await self.ts.delete_table(table_name)
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = await self._insert_two_opposite_entities()

            # Act
            entities = self.table.query_entities("married eq @my_param", parameters={'my_param': True})

            assert entities is not None
            length = 0
            async for e in entities:
                self._assert_default_entity(e)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_multiple_params(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': True,
                'rk': entity['RowKey']
            }
            entities = self.table.query_entities("married eq @my_param and RowKey eq @rk", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1
            assert length == 1

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_integers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': 40,
            }
            entities = self.table.query_entities("age lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_floats(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['ratio'] + 1,
            }
            entities = self.table.query_entities("ratio lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_datetimes(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['birthday'],
            }
            entities = self.table.query_entities("birthday eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_guids(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['clsid']
            }
            entities = self.table.query_entities("clsid eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_binary(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['binary']
            }
            entities = self.table.query_entities("binary eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_user_filter_int64(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_two_opposite_entities()
            large_entity = {
                u"PartitionKey": u"pk001",
                u"RowKey": u"rk001",
                u"large_int": EntityProperty(2 ** 40, EdmType.INT64),
            }
            await self.table.create_entity(large_entity)

            # Act
            parameters = {
                'my_param': large_entity['large_int'].value
            }
            entities = self.table.query_entities("large_int eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            async for entity in entities:
                # self._assert_default_entity(entity)
                assert large_entity['large_int'] == entity['large_int']
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_zero_entities(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(0)

            # Act
            entities = []
            async for t in table.list_entities():
                entities.append(t)

            # Assert
            assert len(entities) ==  0
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_full_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(2)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(2)

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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_with_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = await self._insert_random_entity()
            entity2, _ = await self._insert_random_entity(pk="foo" + entity['PartitionKey'])
            entity3, _ = await self._insert_random_entity(pk="bar" + entity['PartitionKey'])

            # Act
            entities = []
            async for t in self.table.query_entities(
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            assert entity['PartitionKey'] ==  entities[0]['PartitionKey']
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_invalid_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
                async for t in self.table.query_entities("aaa bbb ccc"):
                    _ = t
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_with_select(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(2)

            # Act
            entities = []
            async for t in table.list_entities(select=["age, sex"]):
                entities.append(t)

            # Assert
            assert len(entities) ==  2
            assert entities[0]['age'] ==  39
            assert entities[0]['sex'] ==  'male'
            assert not "birthday" in entities[0]
            assert not "married" in entities[0]
            assert not "deceased" in entities[0]
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_with_top(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = await self._create_query_table(3)
            # circular dependencies made this return a list not an item paged - problem when calling by page
            # Act
            entities = []
            async for t in table.list_entities(results_per_page=2).by_page():
                entities.append(t)

            # Assert
            assert len(entities) ==  2
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_query_entities_with_top_and_next(self, tables_storage_account_name,
                                                    tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_query(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")

        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            entities = []
            async for t in table.query_entities(
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_add(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_add_inside_range(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk='test', start_rk='test1',
                end_pk='test', end_rk='test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            entity = self._create_random_entity_dict('test', 'test1')
            await table.create_entity(entity=entity)

            # Assert
            resp = await self.table.get_entity('test', 'test1')
            self._assert_default_entity(resp)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_add_outside_range(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk='test', start_rk='test1',
                end_pk='test', end_rk='test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            with pytest.raises(HttpResponseError):
                entity = self._create_random_entity_dict()
                await table.create_entity(entity=entity)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(update=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            updated_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            resp = await table.update_entity(mode=UpdateMode.REPLACE, entity=updated_entity)
            received_entity = await self.table.get_entity(entity['PartitionKey'],
                                                          entity['RowKey'])

            # Assert
            self._assert_updated_entity(received_entity)
            assert resp is not None

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_delete(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            await table.delete_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_upper_case_table_name(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()

            # Table names are case insensitive, so simply upper case our existing table name to test
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name.upper(),
                permission=TableSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            entities = []
            async for t in table.query_entities(
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_sas_signed_identifier(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = await self._insert_random_entity()

            access_policy = TableAccessPolicy()
            access_policy.start = datetime(2011, 10, 11)
            access_policy.expiry = datetime(2025, 10, 12)
            access_policy.permission = TableSasPermissions(read=True)
            identifiers = {'testid': access_policy}

            await self.table.set_table_access_policy(identifiers)

            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                policy_id='testid',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(table_name=self.table_name)
            entities = []
            async for t in table.query_entities(
                    "PartitionKey eq '{}'".format(entity['PartitionKey'])):
                entities.append(t)

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_datetime_milliseconds(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_datetime_str_passthrough(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert received['datetime1'].tables_service_value == dotnet_timestamp

            received['datetime2'] = received['datetime1'].replace(year=2020)
            assert received['datetime2'].tables_service_value == ""

            await self.table.update_entity(received)
            updated = await self.table.get_entity(partition, row)
            assert isinstance(updated['datetime1'], datetime)
            assert isinstance(updated['datetime2'], datetime)
            assert updated['datetime1'].tables_service_value == dotnet_timestamp
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_datetime_duplicate_field(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        partition, row = self._create_pk_rk(None, None)

        entity = {
            'PartitionKey': partition,
            'RowKey': row,
            'Timestamp': datetime(year=1999, month=9, day=9, hour=9, minute=9, tzinfo=TZ_UTC)
        }
        try:
            await self.table.create_entity(entity)
            received = await self.table.get_entity(partition, row)

            assert 'Timestamp' not in received
            assert 'timestamp' in received.metadata
            assert isinstance(received.metadata['timestamp'], datetime)
            assert received.metadata['timestamp'].year > 2020

            received['timestamp'] = datetime(year=1999, month=9, day=9, hour=9, minute=9, tzinfo=TZ_UTC)
            await self.table.update_entity(received, mode=UpdateMode.REPLACE)
            received = await self.table.get_entity(partition, row)

            assert 'timestamp' in received
            assert isinstance(received['timestamp'], datetime)
            assert received['timestamp'].year == 1999
            assert isinstance(received.metadata['timestamp'], datetime)
            assert received.metadata['timestamp'].year > 2020
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_etag_duplicate_field(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        partition, row = self._create_pk_rk(None, None)

        entity = {
            'PartitionKey': partition,
            'RowKey': row,
            'ETag': u'foo',
            'etag': u'bar',
            'Etag': u'baz',
        }
        try:
            await self.table.create_entity(entity)
            created = await self.table.get_entity(partition, row)

            assert created['ETag'] == u'foo'
            assert created['etag'] == u'bar'
            assert created['Etag'] == u'baz'
            assert created.metadata['etag'].startswith(u'W/"datetime\'')

            entity['ETag'] = u'one'
            entity['etag'] = u'two'
            entity['Etag'] = u'three'
            with pytest.raises(ValueError):
                await self.table.update_entity(entity, match_condition=MatchConditions.IfNotModified)

            created['ETag'] = u'one'
            created['etag'] = u'two'
            created['Etag'] = u'three'
            await self.table.update_entity(created, match_condition=MatchConditions.IfNotModified)

            updated = await self.table.get_entity(partition, row)
            assert updated['ETag'] == u'one'
            assert updated['etag'] == u'two'
            assert updated['Etag'] == u'three'
            assert updated.metadata['etag'].startswith(u'W/"datetime\'')
            assert updated.metadata['etag'] != created.metadata['etag']
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_entity_create_response_echo(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        partition, row = self._create_pk_rk(None, None)

        entity = {
            'PartitionKey': partition,
            'RowKey': row,
            'Value': 'foobar',
            'Answer': 42
        }
        try:
            result = await self.table.create_entity(entity)
            assert 'preference_applied' not in result
            assert 'content' not in result
            await self.table.delete_entity(entity)

            result = await self.table.create_entity(entity, headers={'Prefer': 'return-no-content'})
            assert 'preference_applied' in result
            assert result['preference_applied'] == 'return-no-content'
            assert 'content' in result
            assert result['content'] is None
            await self.table.delete_entity(entity)

            result = await self.table.create_entity(entity, headers={'Prefer': 'return-content'})
            assert 'preference_applied' in result
            assert result['preference_applied'] == 'return-content'
            assert 'content' in result
            assert result['content']['PartitionKey'] == partition
            assert result['content']['Value'] == 'foobar'
            assert result['content']['Answer'] == 42
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_keys_with_specialchar(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference('table2')
            table2 = self.ts.get_table_client(table2_name)
            await table2.create_table()

            # Act
            entity1 = {
                'PartitionKey': "A'aaa\"_bbbb2",
                'RowKey': '"A\'aaa"_bbbb2',
                'test': '"A\'aaa"_bbbb2'
            }

            await self.table.create_entity(entity1.copy())
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1
            await self.table.upsert_entity(entity1.copy(), mode='merge')
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1
            await self.table.upsert_entity(entity1.copy(), mode='replace')
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1
            await self.table.update_entity(entity1.copy(), mode='merge')
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1
            await self.table.update_entity(entity1.copy(), mode='replace')
            get_entity = await self.table.get_entity(
                partition_key=entity1['PartitionKey'],
                row_key=entity1['RowKey'])
            assert get_entity == entity1

            entity_results = self.table.list_entities()
            async for entity in entity_results:
                assert entity == entity1
                get_entity = await self.table.get_entity(
                    partition_key=entity['PartitionKey'],
                    row_key=entity['RowKey'])
                assert get_entity == entity1

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_entity_with_edmtypes(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        partition, row = self._create_pk_rk(None, None)

        entity = {
            'PartitionKey': partition,
            'RowKey': row,
            "bool": ("false", "Edm.Boolean"),
            "text": (42, EdmType.STRING),
            "number": ("23", EdmType.INT32),
            "bigNumber": (64, EdmType.INT64),
            "bytes": ("test", "Edm.Binary"),
            "amount": ("0", EdmType.DOUBLE),
            "since": ("2008-07-10T00:00:00", EdmType.DATETIME),
            "guid": (TEST_GUID, EdmType.GUID)
        }
        try:
            await self.table.upsert_entity(entity)
            result = await self.table.get_entity(entity['PartitionKey'], entity['RowKey'])
            assert result['bool'] == False
            assert result['text'] == "42"
            assert result['number'] == 23
            assert result['bigNumber'][0] == 64
            assert result['bytes'] == b"test"
            assert result['amount'] == 0.0
            assert str(result['since']) == "2008-07-10 00:00:00+00:00"
            assert result['guid'] == entity["guid"][0]

            with pytest.raises(HttpResponseError) as e:
                entity = {
                    'PartitionKey': partition,
                    'RowKey': row,
                    "bool": ("not a bool", EdmType.BOOLEAN)
                }
                await self.table.upsert_entity(entity)
        finally:
            await self._tear_down()
