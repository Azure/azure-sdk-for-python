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
from enum import Enum
from math import isnan
import uuid

from devtools_testutils import AzureTestCase

from azure.data.tables import (
    TableServiceClient,
    TableClient,
    generate_table_sas,
    TableEntity,
    EntityProperty,
    EdmType,
    TableSasPermissions,
    AccessPolicy,
    UpdateMode
)

from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ResourceModifiedError,
)

from _shared.testcase import TableTestCase
from preparers import TablesPreparer

# ------------------------------------------------------------------------------

class StorageTableEntityTest(AzureTestCase, TableTestCase):

    def _set_up(self, tables_storage_account_name, tables_primary_storage_account_key, url='table'):
        self.table_name = self.get_resource_name('uttable')
        self.ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            table_name = self.table_name
        )
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
        return client

    def _create_random_base_entity_dict(self):
        """
        Creates a dict-based entity with only pk and rk.
        """
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

    def _insert_two_opposite_entities(self, pk=None, rk=None):
        entity1 = self._create_random_entity_dict()
        resp = self.table.create_entity(entity1)

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
        self.table.create_entity(entity)
        return entity1, resp

    def _create_random_entity_dict(self, pk=None, rk=None):
        """
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        """
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
    @TablesPreparer()
    def test_url_encoding_at_symbol(self, tables_storage_account_name, tables_primary_storage_account_key):

        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {
                u"PartitionKey": u"PK",
                u"RowKey": u"table@storage.com",
                u"Value": 100
            }

            for i in range(10):
                entity[u"RowKey"] += str(i)
                entity[u"Value"] += i
                self.table.create_entity(entity)

            f = u"RowKey eq '{}'".format(entity["RowKey"])
            entities = self.table.query_entities(filter=f)
            count = 0
            for e in entities:
                assert e.PartitionKey == entity[u"PartitionKey"]
                assert e.RowKey == entity[u"RowKey"]
                assert e.Value == entity[u"Value"]
                count += 1
                self.table.delete_entity(e.PartitionKey, e.RowKey)

            assert count == 1

            count = 0
            for e in self.table.query_entities(filter=f):
                count += 1
            assert count == 0
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_etag(self, tables_storage_account_name, tables_primary_storage_account_key):

        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:

            entity, _ = self._insert_random_entity()

            entity1 = self.table.get_entity(row_key=entity.RowKey, partition_key=entity.PartitionKey)

            with pytest.raises(AttributeError):
                etag = entity1.etag

            assert entity1.metadata() is not None
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            entities = self.table.query_entities(
                filter="married eq @my_param",
                parameters={'my_param': entity['married']}
            )

            assert entities is not None
            length = 0
            for e in entities:
                self._assert_default_entity(e)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter_multiple_params(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': True,
                'rk': entity['RowKey']
            }
            entities = self.table.query_entities(filter="married eq @my_param and RowKey eq @rk", parameters=parameters)

            length = 0
            assert entities is not None
            for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter_integers(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': 40,
            }
            entities = self.table.query_entities(filter="age lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter_floats(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['ratio'] + 1,
            }
            entities = self.table.query_entities(filter="ratio lt @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter_datetimes(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['birthday'],
            }
            entities = self.table.query_entities(filter="birthday eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_user_filter_guids(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_two_opposite_entities()

            # Act
            parameters = {
                'my_param': entity['clsid']
            }
            entities = self.table.query_entities(filter="clsid eq @my_param", parameters=parameters)

            length = 0
            assert entities is not None
            for entity in entities:
                self._assert_default_entity(entity)
                length += 1

            assert length == 1
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_invalid_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            base_entity = {
                u"PartitionKey": u"pk",
                u"RowKey": u"rk",
                u"value": 1
            }

            for i in range(5):
                base_entity[u"RowKey"] += str(i)
                base_entity[u"value"] += i
                self.table.create_entity(base_entity)
            # Act
            with pytest.raises(HttpResponseError):
                resp = self.table.query_entities(filter="aaa bbb ccc")
                for row in resp:
                    _ = row

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_dictionary(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            resp = self.table.create_entity(entity=entity)

            # Assert
            self._assert_valid_metadata(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_with_hook(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_entity_with_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_entity_with_full_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_entity_conflict(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            with pytest.raises(ResourceExistsError):
                self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_with_large_int32_value_throws(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            dict32 = self._create_random_base_entity_dict()
            dict32['large'] = EntityProperty(2 ** 31, EdmType.INT32)

            # Assert
            with pytest.raises(TypeError):
                self.table.create_entity(entity=dict32)

            dict32['large'] = EntityProperty(-(2 ** 31 + 1), EdmType.INT32)
            with pytest.raises(TypeError):
                self.table.create_entity(entity=dict32)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_with_large_int64_value_throws(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 63, EdmType.INT64)

            # Assert
            with pytest.raises(TypeError):
                self.table.create_entity(entity=dict64)

            dict64['large'] = EntityProperty(-(2 ** 63 + 1), EdmType.INT64)
            with pytest.raises(TypeError):
                self.table.create_entity(entity=dict64)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_with_large_int_success(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            dict64 = self._create_random_base_entity_dict()
            dict64['large'] = EntityProperty(2 ** 50, EdmType.INT64)

            # Assert
            self.table.create_entity(entity=dict64)

            received_entity = self.table.get_entity(dict64['PartitionKey'], dict64['RowKey'])
            assert received_entity['large'].value == dict64['large'].value

            dict64['RowKey'] = u'negative'
            dict64['large'] = EntityProperty(-(2 ** 50 + 1), EdmType.INT64)
            self.table.create_entity(entity=dict64)

            received_entity = self.table.get_entity(dict64['PartitionKey'], dict64['RowKey'])
            assert received_entity['large'].value == dict64['large'].value

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_missing_pk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'RowKey': 'rk'}

            # Act
            with pytest.raises(ValueError):
                resp = self.table.create_entity(entity=entity)
            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_empty_string_pk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'RowKey': u'rk', 'PartitionKey': u''}

            # Act
            resp = self.table.create_entity(entity=entity)
            self._assert_valid_metadata(resp)

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_missing_rk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'PartitionKey': 'pk'}

            # Act
            with pytest.raises(ValueError):
                resp = self.table.create_entity(entity=entity)

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_empty_string_rk(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = {'PartitionKey': u'pk', 'RowKey': u''}

            # Act
            resp = self.table.create_entity(entity=entity)
            self._assert_valid_metadata(resp)

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_too_many_properties(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            for i in range(255):
                entity['key{0}'.format(i)] = 'value{0}'.format(i)

            # Act
            with pytest.raises(HttpResponseError):
                resp = self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_property_name_too_long(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity['a' * 256] = 'badval'

            # Act
            with pytest.raises(HttpResponseError):
                resp = self.table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_entity_with_enums(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert str(entity.test1) == resp_entity.test1
            assert str(entity.test2) == resp_entity.test2
            assert str(entity.test3) == resp_entity.test3

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])

            # Assert
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_with_hook(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert resp['PartitionKey'] ==  entity['PartitionKey']
            assert resp['RowKey'] ==  entity['RowKey']
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_if_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

            with pytest.raises(ResourceNotFoundError):
                resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                            row_key=entity['RowKey'])

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_full_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(
                entity.PartitionKey,
                entity.RowKey,
                headers={'accept': 'application/json;odata=fullmetadata'})

            # Assert
            assert resp.PartitionKey ==  entity.PartitionKey
            assert resp.RowKey ==  entity.RowKey
            self._assert_default_entity_json_full_metadata(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.get_entity(
                partition_key=entity.PartitionKey,
                row_key=entity.RowKey,
                headers={'accept': 'application/json;odata=nometadata'})

            # Assert
            assert resp.PartitionKey ==  entity.PartitionKey
            assert resp.RowKey ==  entity.RowKey
            self._assert_default_entity_json_no_metadata(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            # Act
            with pytest.raises(ResourceNotFoundError):
                self.table.get_entity(partition_key=entity.PartitionKey,
                                      row_key=entity.RowKey)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_get_entity_with_special_doubles(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert received_entity.inf ==  float('inf')
            assert received_entity.negativeinf ==  float('-inf')
            assert isnan(received_entity.nan)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_update_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)

            # resp = self.table.update_item(sent_entity, response_hook=lambda e, h: h)
            resp = self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
            #  assert resp
            received_entity = self.table.get_entity(partition_key=entity.PartitionKey,
                                                    row_key=entity.RowKey)

            with pytest.raises(KeyError):
                del received_entity['property_that_does_not_exist']
            self._assert_valid_metadata(resp)
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_update_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                self.table.update_entity(mode=UpdateMode.REPLACE, entity=sent_entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_update_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_update_entity_with_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with pytest.raises(HttpResponseError):
                self.table.update_entity(
                    mode=UpdateMode.REPLACE,
                    entity=sent_entity,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)
            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_insert_or_merge_entity_with_existing_entity(self, tables_storage_account_name,
                                                         tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_or_merge_entity_with_non_existing_entity(self, tables_storage_account_name,
                                                             tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_or_replace_entity_with_existing_entity(self, tables_storage_account_name,
                                                           tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_insert_or_replace_entity_with_non_existing_entity(self, tables_storage_account_name,
                                                               tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_merge_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_merge_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            sent_entity = self._create_updated_entity_dict(entity['PartitionKey'], entity['RowKey'])
            with pytest.raises(ResourceNotFoundError):
                self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_merge_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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

    @TablesPreparer()
    def test_merge_entity_with_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            sent_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            with pytest.raises(HttpResponseError):
                self.table.update_entity(mode=UpdateMode.MERGE,
                                         entity=sent_entity,
                                         etag='W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                                         match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_delete_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            resp = self.table.delete_entity(partition_key=entity.PartitionKey, row_key=entity.RowKey)

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_delete_entity_not_existing(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()

            # Act
            with pytest.raises(ResourceNotFoundError):
                self.table.delete_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_delete_entity_with_if_matches(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, etag = self._insert_random_entity()

            # Act
            resp = self.table.delete_entity(entity.PartitionKey, entity.RowKey, etag=etag,
                                            match_condition=MatchConditions.IfNotModified)

            # Assert
            assert resp is None
            with pytest.raises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_delete_entity_with_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()

            # Act
            with pytest.raises(HttpResponseError):
                self.table.delete_entity(
                    entity.PartitionKey, entity.RowKey,
                    etag=u'W/"datetime\'2012-06-15T22%3A51%3A44.9662825Z\'"',
                    match_condition=MatchConditions.IfNotModified)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_unicode_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert len(entities) ==  2
            assert entities[0].Description ==  u'ꀕ'
            assert entities[1].Description ==  u'ꀕ'
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_unicode_property_name(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert len(entities) ==  2
            assert entities[0][u'啊齄丂狛狜'] ==  u'ꀕ'
            assert entities[1][u'啊齄丂狛狜'] ==  u'hello'
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_operations_on_entity_with_partition_key_having_single_quote(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        partition_key_with_single_quote = u"a''''b"
        row_key_with_single_quote = u"a''''b"
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert received_entity['newField'] ==  'newFieldValue'

            # Act
            resp = self.table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            assert resp is None
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_empty_and_spaces_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert resp is not None
            assert resp.EmptyByte.value ==  b''
            assert resp.EmptyUnicode ==  u''
            assert resp.SpacesOnlyByte.value ==  b'   '
            assert resp.SpacesOnlyUnicode ==  u'   '
            assert resp.SpacesBeforeByte.value ==  b'   Text'
            assert resp.SpacesBeforeUnicode ==  u'   Text'
            assert resp.SpacesAfterByte.value ==  b'Text   '
            assert resp.SpacesAfterUnicode ==  u'Text   '
            assert resp.SpacesBeforeAndAfterByte.value ==  b'   Text   '
            assert resp.SpacesBeforeAndAfterUnicode ==  u'   Text   '
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_none_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_base_entity_dict()
            entity.update({'NoneValue': None})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert not hasattr(resp, 'NoneValue')
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_binary_property_value(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            binary_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'
            entity = self._create_random_base_entity_dict()
            entity.update({'binary': b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n'})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            assert resp.binary.value ==  binary_data
        finally:
            self._tear_down()

    @pytest.mark.skip("response time is three hours before the given one")
    @TablesPreparer()
    def test_timezone(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            local_tz = tzoffset('BRST', -10800)
            local_date = datetime(2003, 9, 27, 9, 52, 43, tzinfo=local_tz)
            entity = self._create_random_base_entity_dict()
            entity.update({'date': local_date})

            # Act
            self.table.create_entity(entity=entity)
            resp = self.table.get_entity(entity['PartitionKey'], entity['RowKey'])

            # Assert
            assert resp is not None
            # times are not equal because request is made after
            # assert resp.date.astimezone(tzutc()) ==  local_date.astimezone(tzutc())
            assert resp.date.astimezone(local_tz) ==  local_date
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities())

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity(entity)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_each_page(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
                    self.table.create_entity(base_entity)
                except ResourceExistsError:
                    pass

            query_filter = u"PartitionKey eq 'pk'"

            entity_count = 0
            page_count = 0
            for entity_page in self.table.query_entities(filter=query_filter, results_per_page=2).by_page():

                temp_count = 0
                for ent in entity_page:
                    temp_count += 1

                assert temp_count <= 2
                page_count += 1
                entity_count += temp_count

            assert entity_count == 6
            assert page_count == 3

        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_zero_entities(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(0)

            # Act
            entities = list(table.list_entities())

            # Assert
            assert len(entities) ==  0
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_full_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(headers={'accept': 'application/json;odata=fullmetadata'}))

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity_json_full_metadata(entity)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_no_metadata(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(headers={'accept': 'application/json;odata=nometadata'}))

            # Assert
            assert len(entities) ==  2
            for entity in entities:
                self._assert_default_entity_json_no_metadata(entity)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_with_filter(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity, _ = self._insert_random_entity()
            entity2, _ = self._insert_random_entity(pk="foo" + entity.PartitionKey)
            entity3, _ = self._insert_random_entity(pk="bar" + entity.PartitionKey)

            # Act
            entities = list(self.table.query_entities(
                filter="PartitionKey eq '{}'".format(entity.PartitionKey),
                results_per_page=1))

            # Assert
            assert len(entities) ==  1
            assert entity.PartitionKey ==  entities[0].PartitionKey
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_with_select(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(2)

            # Act
            entities = list(table.list_entities(select=['age', 'sex']))

            # Assert
            assert len(entities) ==  2
            assert entities[0].age ==  39
            assert entities[0].sex ==  'male'
            assert not hasattr(entities[0], "birthday")
            assert not hasattr(entities[0], "married")
            assert not hasattr(entities[0], "deceased")
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_with_top(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table = self._create_query_table(3)
            # circular dependencies made this return a list not an item paged - problem when calling by page
            # Act
            entities = list(next(table.list_entities(results_per_page=2).by_page()))

            # Assert
            assert len(entities) ==  2
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_query_entities_with_top_and_next(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
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
            assert len(entities1) ==  2
            assert len(entities2) ==  2
            assert len(entities3) ==  1
            self._assert_default_entity(entities1[0])
            self._assert_default_entity(entities1[1])
            self._assert_default_entity(entities2[0])
            self._assert_default_entity(entities2[1])
            self._assert_default_entity(entities3[0])
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_query(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")

        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
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
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity['PartitionKey'])))

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_add(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
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
            table.create_entity(entity=entity)

            # Assert
            resp = self.table.get_entity(partition_key=entity['PartitionKey'],
                                         row_key=entity['RowKey'])
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_add_inside_range(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start_pk=u'test', start_rk=u'test1',
                end_pk=u'test', end_rk=u'test1',
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            entity = self._create_random_entity_dict(u'test', u'test1')
            table.create_entity(entity=entity)

            # Assert
            resp = self.table.get_entity('test', 'test1')
            self._assert_default_entity(resp)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_add_outside_range(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
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
                table.create_entity(entity=entity)

            # Assert
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(update=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )
            # token = generate_table_sas(
            #     tables_storage_account_name,
            #     tables_primary_storage_account_key,
            #     self.table_name,
            #     permission=TableSasPermissions(update=True),
            #     expiry=datetime.utcnow() + timedelta(hours=1),
            # )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            updated_entity = self._create_updated_entity_dict(entity.PartitionKey, entity.RowKey)
            resp = table.update_entity(mode=UpdateMode.REPLACE, entity=updated_entity)

            # Assert
            received_entity = self.table.get_entity(entity.PartitionKey, entity.RowKey)
            assert resp is not None
            self._assert_updated_entity(received_entity)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_delete(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()
            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
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
            table.delete_entity(entity.PartitionKey, entity.RowKey)

            # Assert
            with pytest.raises(ResourceNotFoundError):
                self.table.get_entity(entity.PartitionKey, entity.RowKey)
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_upper_case_table_name(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()

            access_policy = AccessPolicy()
            access_policy.start = datetime(2011, 10, 11)
            access_policy.expiry = datetime(2025, 10, 12)
            access_policy.permission = TableSasPermissions(read=True)
            identifiers = {'testid': access_policy}

            self.table.set_table_access_policy(identifiers)

            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
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
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity.PartitionKey)))

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_sas_signed_identifier(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Arrange
            entity, _ = self._insert_random_entity()

            access_policy = AccessPolicy()
            access_policy.start = datetime(2011, 10, 11)
            access_policy.expiry = datetime(2025, 10, 12)
            access_policy.permission = TableSasPermissions(read=True)
            identifiers = {'testid': access_policy}

            self.table.set_table_access_policy(identifiers)

            token = self.generate_sas(
                generate_table_sas,
                tables_storage_account_name,
                tables_primary_storage_account_key,
                self.table_name,
                policy_id='testid'
            )

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=AzureSasCredential(token),
            )
            table = service.get_table_client(self.table_name)
            entities = list(table.query_entities(
                filter="PartitionKey eq '{}'".format(entity.PartitionKey)))

            # Assert
            assert len(entities) ==  1
            self._assert_default_entity(entities[0])
        finally:
            self._tear_down()

    @TablesPreparer()
    def test_datetime_milliseconds(self, tables_storage_account_name, tables_primary_storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        url = self.account_url(tables_storage_account_name, "table")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()

            entity['milliseconds'] = datetime(2011, 11, 4, 0, 5, 23, 283000, tzinfo=tzutc())

            self.table.create_entity(entity)

            received_entity = self.table.get_entity(
                partition_key=entity['PartitionKey'],
                row_key=entity['RowKey']
            )

            assert entity['milliseconds'] == received_entity['milliseconds']

        finally:
            self._tear_down()
