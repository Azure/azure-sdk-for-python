# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import json
import uuid
import enum
from urllib.parse import quote
from datetime import datetime, timezone

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import HttpTransport
from azure.data.tables import TableClient, TableEntityEncoder, EdmType, EntityProperty, UpdateMode
from azure.data.tables._base_client import _DEV_CONN_STRING
from azure.data.tables._common_conversion import _encode_base64, _to_utc_datetime

from _shared.testcase import TableTestCase

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import tables_decorator


class MyEncoder(TableEntityEncoder):
    def prepare_key(self, key):
        """Custom key preparer to support key in type UUID, int, float or bool."""
        if isinstance(key, uuid.UUID) or isinstance(key, int) or isinstance(key, float) or isinstance(key, bool):
            key = str(key)
        elif isinstance(key, datetime):
            key = str(_to_utc_datetime(key))
        elif isinstance(key, bytes):
            key = str(_encode_base64(key))
        elif isinstance(key, enum.Enum): # Support enum in key's value
            key = key.value
        return super().prepare_key(key)

    def encode_property(self, name, value):
        if isinstance(value, enum.Enum): # Support enum in normal property's value
            value = value.value
        return super().encode_property(name, value)


class EnumBasicOptions(enum.Enum):
    ONE = "One"
    TWO = "Two"
    THREE = "Three"


class EnumStrOptions(str, enum.Enum):
    ONE = "One"
    TWO = "Two"
    THREE = "Three"


class EnumIntOptions(enum.IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


class VerificationSuccessful(Exception):
    """Raise from test transport in the case that the body was serialized as expected."""


class EncoderVerificationTransport(HttpTransport):

    def send(self, request, **kwargs):
        if "verify_payload" in kwargs:
            verification = kwargs["verify_payload"]
            assert request.body == verification, f"Request body '{request.body}' does not match expected: '{verification}'."
        if "verify_url" in kwargs:
            verification = kwargs["verify_url"]
            assert request.url.endswith(kwargs["verify_url"]), f"Request URL '{request.url}' does not match expected: '{verification}'."
        if "verify_headers" in kwargs:
            verification = kwargs["verify_headers"]
            for key, value in verification.items():
                try:
                    assert request.headers[key] == value, f"Request header '{key}' with value '{request.headers[key]}' does not match expected: '{value}'."
                except KeyError:
                    raise AssertionError(f"Request missing expected header '{key}' from set: '{request.headers}'.")
        raise VerificationSuccessful()

    def open(self):
        pass

    def close(self):
        pass

    def __exit__(self, *args):
        self.close()


class TestTableEncoder(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_keys(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Test basic string, int32, float and bool type in PartitionKey or RowKey.
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # TableEntity keys in basic type string, int32, float and bool.
        entity1 = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 1,
            "Data2": True
        }
        expected_entity1 = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 1,
            "Data2": True
        }
        entity2 = {"PartitionKey": "PK", "RowKey": 1}
        expected_entity2 = {
            "PartitionKey": "PK",
            "RowKey": "1"
        }
        entity3 = {"PartitionKey": "PK", "RowKey": True} # Will get InvalidInput error if pass boolean value to service
        expected_entity3 = {
            "PartitionKey": "PK",
            "RowKey": "True"
        }
        entity4 = {"PartitionKey": "PK", "RowKey": 3.14}
        expected_entity4 = {
            "PartitionKey": "PK",
            "RowKey": "3.14"
        }
        # TableEntity keys in complex type datetime, UUID and binary.
        entity5 = {
            "PartitionKey": datetime.now(),
            "RowKey": uuid.uuid4()
        }
        expected_entity5 = {
            "PartitionKey": _to_utc_datetime(entity5["PartitionKey"]),
            "RowKey": str(entity5["RowKey"])
        }
        entity6 = {
            "PartitionKey": b"binarydata",
            "RowKey": 1234
        }
        expected_entity6 = {
            "PartitionKey": str(_encode_base64(entity6["PartitionKey"])),
            "RowKey": "1234"
        }
        
        encoder = MyEncoder()
        encoded_entity1 = encoder.encode_entity(entity1)
        assert json.dumps(encoded_entity1, sort_keys=True) == json.dumps(expected_entity1, sort_keys=True)
        encoded_entity2 = encoder.encode_entity(entity2)
        assert json.dumps(encoded_entity2, sort_keys=True) == json.dumps(expected_entity2, sort_keys=True)
        encoded_entity3 = encoder.encode_entity(entity3)
        assert json.dumps(encoded_entity3, sort_keys=True) == json.dumps(expected_entity3, sort_keys=True)
        encoded_entity4 = encoder.encode_entity(entity4)
        assert json.dumps(encoded_entity4, sort_keys=True) == json.dumps(expected_entity4, sort_keys=True)
        encoded_entity5 = encoder.encode_entity(entity5)
        assert json.dumps(encoded_entity5, sort_keys=True) == json.dumps(expected_entity5, sort_keys=True)
        encoded_entity6 = encoder.encode_entity(entity6)
        assert json.dumps(encoded_entity6, sort_keys=True) == json.dumps(expected_entity6, sort_keys=True)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()

            client.create_entity(entity1)
            entity1 = client.get_entity(entity1["PartitionKey"], entity1["RowKey"])
            client.delete_entity(entity1["PartitionKey"], entity1["RowKey"])

            client.create_entity(entity2, encoder=MyEncoder())
            entity2 = client.get_entity(entity2["PartitionKey"], entity2["RowKey"], encoder=MyEncoder())
            client.delete_entity(entity2, encoder=MyEncoder())

            client.create_entity(entity3, encoder=MyEncoder())
            entity3 = client.get_entity(entity3["PartitionKey"], entity3["RowKey"], encoder=MyEncoder())
            client.delete_entity(entity3, encoder=MyEncoder())

            client.create_entity(entity4, encoder=MyEncoder())
            entity4 = client.get_entity(entity4["PartitionKey"], entity4["RowKey"], encoder=MyEncoder())
            client.delete_entity(entity4, encoder=MyEncoder())

            client.create_entity(entity5, encoder=MyEncoder())
            entity5 = client.get_entity(entity5["PartitionKey"], entity5["RowKey"], encoder=MyEncoder())
            client.delete_entity(entity5, encoder=MyEncoder())

            client.create_entity(entity6, encoder=MyEncoder())
            entity6 = client.get_entity(entity6["PartitionKey"], entity6["RowKey"], encoder=MyEncoder())
            client.delete_entity(entity6, encoder=MyEncoder())

            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_type_conversion(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": b"testdata",
            "Data4": datetime.now(),
            "Data5": uuid.uuid4(),
            "Data6": "Foobar",
            "Data7": 3.14
        }
        expected_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(entity["Data4"]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(entity["Data5"]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double"
        }
        encoder = MyEncoder()
        entity = encoder.encode_entity(entity)
        assert json.dumps(entity, sort_keys=True) == json.dumps(expected_entity, sort_keys=True)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity, encoder=encoder)            
            client.delete_entity(entity, encoder=encoder)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        entity1 = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
            "Data4": EntityProperty(datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc), "Edm.DateTime"),
            "Data5": EntityProperty(uuid.uuid4(), "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": (3.14, EdmType.DOUBLE),
            "Data8": (2 ** 60, "Edm.Int64")
        }
        expected_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(entity1["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(entity1["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        entity2 = {
            "PartitionKey": "PK2",
            "RowKey": "RK2",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
            "Data4": EntityProperty(entity1["Data4"][0], "Edm.DateTime"),
            "Data5": EntityProperty(entity1["Data5"][0], "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": EntityProperty(3.14, "Edm.Double"),
            "Data8": ("1152921504606846976", "Edm.Int64")
        }
        expected_entity2 = {
            "PartitionKey": "PK2",
            "RowKey": "RK2",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(entity1["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(entity1["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        encoder = TableEntityEncoder()
        encoded_entity = encoder.encode_entity(entity1)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity, sort_keys=True)
        encoded_entity = encoder.encode_entity(entity2)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity2, sort_keys=True)
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity1)
            client.delete_entity(entity1)
            client.create_entity(entity2)
            client.delete_entity(entity2)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(datetime.now()),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(uuid.uuid4()),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": "3.14",
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        expected_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": entity["Data4"],
            "Data4@odata.type": "Edm.DateTime",
            "Data5": entity["Data5"],
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data7": "3.14",
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        encoder = TableEntityEncoder()
        encoded_entity = encoder.encode_entity(entity)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity, sort_keys=True)
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity)
            client.delete_entity(entity)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_atypical_values(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        entity1 = {
            "PartitionKey": "PK1",
            "RowKey": "你好",
            "Data":  "你好"
        }
        # Invalid int32 and int64 values
        # TODO: This will likely change if we move to post-request validation.
        entity2 = {
            "PartitionKey": "PK2",
            "RowKey": "RK",
            "Data":  2 ** 65 # 2 ** 70 also works
        }
        max_int64 = 9223372036854775807
        entity3 = {
            "PartitionKey": "PK3",
            "RowKey": "RK",
            "Data": (max_int64, "Edm.Int64")
        }
        expected_entity3 = {
            "PartitionKey": "PK3",
            "RowKey": "RK",
            "Data": str(max_int64),
            "Data@odata.type": "Edm.Int64"
        }
        # Test data out of int64 range
        entity4 = {
            "PartitionKey": "PK4",
            "RowKey": "RK",
            "Data": (max_int64 + 1, "Edm.Int64") # Bad request, InvalidInput
        }
        # Infinite float values
        entity5 = {
            "PartitionKey": "PK5",
            "RowKey": "RK",
            "Data1":  float('nan'),
            "Data2": float('inf'),
            "Data3": float('-inf')
        }
        expected_entity5 = {
            "PartitionKey": "PK5",
            "RowKey": "RK",
            "Data1":  "NaN",
            "Data1@odata.type": "Edm.Double",
            "Data2": "Infinity",
            "Data2@odata.type": "Edm.Double",
            "Data3": "-Infinity",
            "Data3@odata.type": "Edm.Double"
        }
        # Non-string keys
        entity6 = {
            "PartitionKey": "PK6",
            "RowKey": "RK",
            123:  456
        }
        expected_entity6 = {
            "PartitionKey": "PK6",
            "RowKey": "RK",
            "123":  456 # HttpResponseError, code: PropertyNameInvalid
        }
        # Test enums
        # TBD: support it in default encoder?
        entity7 = {
            "PartitionKey": "PK7",
            "RowKey": EnumBasicOptions.ONE,
            "Data": EnumBasicOptions.TWO
        }
        # Support the enum by adding conversions in a customized encoder
        expected_entity7 = {
            "PartitionKey": "PK7",
            "RowKey": "One",
            "Data": "Two"
        }
        entity8 = {
            "PartitionKey": "PK8",
            "RowKey": EnumIntOptions.ONE,
            "Data": EnumIntOptions.TWO
        }
        # Key's value always be string type
        # For enum value in normal properties: EnumIntOptions -> int, EnumBasicOptions/EnumStrOptions -> string
        expected_entity8 = {
            "PartitionKey": "PK8",
            "RowKey": "1",
            "Data": 2
        }
        entity9 = {
            "PartitionKey": "PK9",
            "RowKey": EnumStrOptions.ONE,
            "Data": EnumStrOptions.TWO
        }
        expected_entity9 = {
            "PartitionKey": "PK9",
            "RowKey": "One",
            "Data": "Two"
        }
        encoder = TableEntityEncoder()
        encoded_entity = encoder.encode_entity(entity1)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(entity1, sort_keys=True)
        encoded_entity = encoder.encode_entity(entity2)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(entity2, sort_keys=True)
        encoded_entity = encoder.encode_entity(entity3)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity3, sort_keys=True)
        encoded_entity = encoder.encode_entity(entity5)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity5, sort_keys=True)
        encoded_entity = MyEncoder().encode_entity(entity6)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity6, sort_keys=True)
        encoded_entity = MyEncoder().encode_entity(entity7)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity7, sort_keys=True)
        encoded_entity = MyEncoder().encode_entity(entity8)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity8, sort_keys=True)
        encoded_entity = MyEncoder().encode_entity(entity9)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity9, sort_keys=True)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity1) # no edm type in get and list results
            client.delete_entity(entity1)
            client.create_entity(entity2)
            client.delete_entity(entity2)
            client.create_entity(entity3)
            client.delete_entity(entity3)
            with pytest.raises(HttpResponseError) as exc:
                client.create_entity(entity4)
            assert ("Operation returned an invalid status 'Bad Request'") in str(exc.value)
            client.create_entity(entity5)
            client.delete_entity(entity5)
            with pytest.raises(HttpResponseError) as exc:
                client.create_entity(entity6)
            assert ("Operation returned an invalid status 'Bad Request'") in str(exc.value)
            with pytest.raises(HttpResponseError) as exc:
                client.create_entity(entity6, encoder=MyEncoder())
            assert ("Operation returned an invalid status 'Bad Request'") in str(exc.value)
            client.create_entity(entity7, encoder=MyEncoder())
            client.delete_entity(entity7, encoder=MyEncoder())
            client.create_entity(entity8, encoder=MyEncoder())
            client.delete_entity(entity8, encoder=MyEncoder())
            client.create_entity(entity9, encoder=MyEncoder())
            client.delete_entity(entity9, encoder=MyEncoder())
            client.delete_table()


class TestTableEncoderUnitTests(TableTestCase):
    def test_encoder_upsert_entity_basic(self):
        # Test basic string, int32 and bool data
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 1,
            "Data2": True
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 1,
            "Data2": True
        }
        verification = json.dumps(expected_entity)

        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": 1}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": True}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": 3.14}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": 1}, mode=UpdateMode.REPLACE)
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": True}, mode=UpdateMode.REPLACE)
        with pytest.raises(TypeError):
            client.upsert_entity({"PartitionKey": "foo", "RowKey": 3.14}, mode=UpdateMode.REPLACE)

    def test_encoder_upsert_entity_complex_keys(self):
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": datetime.now(),
            "RowKey": uuid.uuid4(),
        }
        expected_entity = {
            "PartitionKey": _to_utc_datetime(test_entity["PartitionKey"]),
            "PartitionKey@odata.type": "Edm.DateTime",
            "RowKey": str(test_entity["RowKey"]),
            "RowKey@odata.type": "Edm.Guid"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        test_entity = {
            "PartitionKey": "foo",
            "RowKey": b"foo",
        }
        expected_entity = {
            "PartitionKey": "foo",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": _encode_base64(test_entity["RowKey"]),
            "RowKey@odata.type": "Edm.Binary"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    def test_encoder_upsert_entity_type_conversion(self):
        # All automatically detected data types
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": b"testdata",
            "Data4": datetime.now(),
            "Data5": uuid.uuid4(),
            "Data6": "Foobar",
            "Data7": 3.14
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(test_entity["Data4"]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(test_entity["Data5"]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",

        }
        verification = json.dumps(expected_entity)

        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    def test_encoder_upsert_entity_tuples(self):
        # Explicit datatypes using Tuple definition
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
            "Data4": EntityProperty(datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc), "Edm.DateTime"),
            "Data5": EntityProperty(uuid.uuid4(), "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": (3.14, EdmType.DOUBLE),
            "Data8": (2 ** 60, "Edm.Int64")
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(test_entity["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(test_entity["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64",

        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),  # TODO: Not sure what to do about this
            "Data4": EntityProperty(_to_utc_datetime(test_entity["Data4"][0]), "Edm.DateTime"),
            "Data5": EntityProperty(str(test_entity["Data5"][0]), "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": EntityProperty(3.14, "Edm.Double"),
            "Data8": ("1152921504606846976", "Edm.Int64")
        }
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    @pytest.mark.xfail()  # Not supported yet
    def test_encoder_upsert_entity_raw(self):
        # Raw payload with existing EdmTypes
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(datetime.now()),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(uuid.uuid4()),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": "3.14",
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64",

        }
        verification = json.dumps(test_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    def test_encoder_upsert_entity_atypical_values(self):
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        # Non-UTF8 characters in both keys and properties
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "你好",
            "Data":  "你好"
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "你好",
            "RowKey@odata.type": "Edm.String",
            "Data": "你好",
            "Data@odata.type": "Edm.String"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Invalid int32 and int64 values
        # TODO: This will likely change if we move to post-request validation.
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data":  2 ** 65
        }
        with pytest.raises(TypeError):
            client.upsert_entity(test_entity, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.upsert_entity(test_entity, mode=UpdateMode.REPLACE)
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data":  (2 ** 70, "Edm.Int64")
        }
        with pytest.raises(TypeError):
            client.upsert_entity(test_entity, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.upsert_entity(test_entity, mode=UpdateMode.REPLACE)

        # Infinite float values
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1":  float('nan'),
            "Data2": float('inf'),
            "Data3": float('-inf'),
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": "NaN",
            "Data1@odata.type": "Edm.Double",
            "Data2": "Infinity",
            "Data2@odata.type": "Edm.Double",
            "Data3": "-Infinity",
            "Data3@odata.type": "Edm.Double",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Non-string keys
        # TODO: This seems broken? Not sure what the live service will do with a non-string key.
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            123:  456
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            123:  456
        }
        verification = json.dumps(expected_entity)
        # TODO: The code introduced to serialize to support odata types raises a TypeError here. Need to investigate the best approach.
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Test enums
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumBasicOptions.ONE,
            "Data": EnumBasicOptions.TWO
        }
        # TODO: This looks like it was always broken
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "EnumBasicOptions.ONE",
            "RowKey@odata.type": "Edm.String",
            "Data": "EnumBasicOptions.TWO",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumIntOptions.ONE,
            "Data": EnumIntOptions.TWO
        }
        # TODO: This is a bit weird
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "1",
            "RowKey@odata.type": "Edm.String",
            "Data": "2",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        # TODO: This changes between Python 3.10 and 3.11
        # with pytest.raises(VerificationSuccessful):
        #     client.upsert_entity(
        #         test_entity,
        #         mode=UpdateMode.MERGE,
        #         verify_payload=verification,
        #         verify_url="/foo(PartitionKey='PK',RowKey='1')",
        #         verify_headers={
        #             "Content-Type":"application/json",
        #             "Accept":"application/json",
        #         }
        #     )
        # with pytest.raises(VerificationSuccessful):
        #     client.upsert_entity(
        #         test_entity,
        #         mode=UpdateMode.REPLACE,
        #         verify_payload=verification,
        #         verify_url="/foo(PartitionKey='PK',RowKey='1')",
        #         verify_headers={
        #             "Content-Type":"application/json",
        #             "Accept":"application/json",
        #         }
        #     )

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumStrOptions.ONE,
            "Data": EnumStrOptions.TWO
        }
        # TODO: This looks like it was always broken
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "EnumStrOptions.ONE",
            "RowKey@odata.type": "Edm.String",
            "Data": "EnumStrOptions.TWO",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    def test_encoder_update_entity_basic(self):
        # Test basic string, int32 and bool data
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 1,
            "Data2": True
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 1,
            "Data2": True
        }
        verification = json.dumps(expected_entity)

        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": 1}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": True}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": 3.14}, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": 1}, mode=UpdateMode.REPLACE)
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": True}, mode=UpdateMode.REPLACE)
        with pytest.raises(TypeError):
            client.update_entity({"PartitionKey": "foo", "RowKey": 3.14}, mode=UpdateMode.REPLACE)

    def test_encoder_update_entity_complex_keys(self):
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": datetime.now(),
            "RowKey": uuid.uuid4(),
        }
        expected_entity = {
            "PartitionKey": _to_utc_datetime(test_entity["PartitionKey"]),
            "PartitionKey@odata.type": "Edm.DateTime",
            "RowKey": str(test_entity["RowKey"]),
            "RowKey@odata.type": "Edm.Guid"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        test_entity = {
            "PartitionKey": "foo",
            "RowKey": b"foo",
        }
        expected_entity = {
            "PartitionKey": "foo",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": _encode_base64(test_entity["RowKey"]),
            "RowKey@odata.type": "Edm.Binary"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/foo(PartitionKey='{quote(expected_entity['PartitionKey'])}',RowKey='{expected_entity['RowKey']}')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )

    def test_encoder_update_entity_type_conversion(self):
        # All automatically detected data types
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data2": False,
            "Data3": b"testdata",
            "Data4": datetime.now(),
            "Data5": uuid.uuid4(),
            "Data6": "Foobar",
            "Data7": 3.14
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data2": False,
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(test_entity["Data4"]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(test_entity["Data5"]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",

        }
        verification = json.dumps(expected_entity)

        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )

    def test_encoder_update_entity_tuples(self):
        # Explicit datatypes using Tuple definition
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
            "Data4": EntityProperty(datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc), "Edm.DateTime"),
            "Data5": EntityProperty(uuid.uuid4(), "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": (3.14, EdmType.DOUBLE),
            "Data8": (2 ** 60, "Edm.Int64")
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(test_entity["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(test_entity["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64",

        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": (12345, EdmType.INT32),
            "Data2": (False, "Edm.Boolean"),
            "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),  # TODO: Not sure what to do about this
            "Data4": EntityProperty(_to_utc_datetime(test_entity["Data4"][0]), "Edm.DateTime"),
            "Data5": EntityProperty(str(test_entity["Data5"][0]), "Edm.Guid"),
            "Data6": ("Foobar", EdmType.STRING),
            "Data7": EntityProperty(3.14, "Edm.Double"),
            "Data8": ("1152921504606846976", "Edm.Int64")
        }
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )

    @pytest.mark.xfail()  # Not supported yet
    def test_encoder_update_entity_raw(self):
        # Raw payload with existing EdmTypes
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        test_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(datetime.now()),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(uuid.uuid4()),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": "3.14",
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64",

        }
        verification = json.dumps(test_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                    "If-Match": "*"
                }
            )

    def test_encoder_update_entity_atypical_values(self):
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        # Non-UTF8 characters in both keys and properties
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "你好",
            "Data":  "你好"
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "你好",
            "RowKey@odata.type": "Edm.String",
            "Data": "你好",
            "Data@odata.type": "Edm.String"
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Invalid int32 and int64 values
        # TODO: This will likely change if we move to post-request validation.
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data":  2 ** 65
        }
        with pytest.raises(TypeError):
            client.update_entity(test_entity, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.update_entity(test_entity, mode=UpdateMode.REPLACE)
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data":  (2 ** 70, "Edm.Int64")
        }
        with pytest.raises(TypeError):
            client.update_entity(test_entity, mode=UpdateMode.MERGE)
        with pytest.raises(TypeError):
            client.update_entity(test_entity, mode=UpdateMode.REPLACE)

        # Infinite float values
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1":  float('nan'),
            "Data2": float('inf'),
            "Data3": float('-inf'),
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            "Data1": "NaN",
            "Data1@odata.type": "Edm.Double",
            "Data2": "Infinity",
            "Data2@odata.type": "Edm.Double",
            "Data3": "-Infinity",
            "Data3@odata.type": "Edm.Double",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Non-string keys
        # TODO: This seems broken? Not sure what the live service will do with a non-string key.
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            123:  456
        }
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "RK",
            "RowKey@odata.type": "Edm.String",
            123:  456
        }
        verification = json.dumps(expected_entity)
        # TODO: The code introduced to serialize to support odata types raises a TypeError here. Need to investigate the best approach.
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

        # Test enums
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumBasicOptions.ONE,
            "Data": EnumBasicOptions.TWO
        }
        # TODO: This looks like it was always broken
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "EnumBasicOptions.ONE",
            "RowKey@odata.type": "Edm.String",
            "Data": "EnumBasicOptions.TWO",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumIntOptions.ONE,
            "Data": EnumIntOptions.TWO
        }
        # TODO: This is a bit weird
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "1",
            "RowKey@odata.type": "Edm.String",
            "Data": "2",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        # TODO: This changes between Python 3.10 and 3.11
        # with pytest.raises(VerificationSuccessful):
        #     client.update_entity(
        #         test_entity,
        #         mode=UpdateMode.MERGE,
        #         verify_payload=verification,
        #         verify_url="/foo(PartitionKey='PK',RowKey='1')",
        #         verify_headers={
        #             "Content-Type":"application/json",
        #             "Accept":"application/json",
        #         }
        #     )
        # with pytest.raises(VerificationSuccessful):
        #     client.update_entity(
        #         test_entity,
        #         mode=UpdateMode.REPLACE,
        #         verify_payload=verification,
        #         verify_url="/foo(PartitionKey='PK',RowKey='1')",
        #         verify_headers={
        #             "Content-Type":"application/json",
        #             "Accept":"application/json",
        #         }
        #     )

        test_entity = {
            "PartitionKey": "PK",
            "RowKey": EnumStrOptions.ONE,
            "Data": EnumStrOptions.TWO
        }
        # TODO: This looks like it was always broken
        expected_entity = {
            "PartitionKey": "PK",
            "PartitionKey@odata.type": "Edm.String",
            "RowKey": "EnumStrOptions.ONE",
            "RowKey@odata.type": "Edm.String",
            "Data": "EnumStrOptions.TWO",
            "Data@odata.type": "Edm.String",
        }
        verification = json.dumps(expected_entity)
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url="/foo(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type":"application/json",
                    "Accept":"application/json",
                }
            )

    def test_encoder_delete_entity_basic(self):
        # Test basic string, int32 and bool data
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())
        
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                "foo",
                "bar",
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='bar')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                {"PartitionKey": "foo","RowKey": "bar"},
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='bar')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                "foo",
                "bar'baz",  # cspell:disable-line
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='bar%27%27baz')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                {"PartitionKey": "foo","RowKey": "bar'baz"},  # cspell:disable-line
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='bar%27%27baz')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(TypeError):
            client.delete_entity("foo", 1)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": 1})
        with pytest.raises(TypeError):
            client.delete_entity("foo", True)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": True})
        with pytest.raises(TypeError):
            client.delete_entity("foo", 3.14)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": 3.14})

    def test_encoder_delete_entity_complex_keys(self):
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())
        
        with pytest.raises(TypeError):
            client.delete_entity("foo", datetime.now())
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": datetime.now()})
        with pytest.raises(TypeError):
            client.delete_entity("foo", uuid.uuid4())
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": uuid.uuid4()})
        with pytest.raises(TypeError):
            client.delete_entity("foo", b"binarydata")
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": b"binarydata"})

    def test_encoder_delete_entity_tuples(self):
        # Explicit datatypes using Tuple definition
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())
        
        with pytest.raises(TypeError):
            client.delete_entity("foo", EntityProperty("bar", "Edm.String"))
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": ("bar", EdmType.STRING)})

    def test_encoder_delete_entity_atypical_values(self):
        # Non-UTF8 characters in both keys and properties
        # Test enums in both keys and properties
        client = TableClient.from_connection_string(
            _DEV_CONN_STRING,
            table_name="foo",
            transport=EncoderVerificationTransport())

        # Non-UTF8 characters in both keys and properties
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                "PK",
                "你好",
                verify_payload=None,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                {"PartitionKey": "PK", "RowKey": "你好"},
                verify_payload=None,
                verify_url="/foo(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        
        with pytest.raises(TypeError):
            client.delete_entity("foo", EnumBasicOptions.ONE)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": EnumBasicOptions.ONE})
        with pytest.raises(TypeError):
            client.delete_entity("foo", EnumIntOptions.ONE)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": EnumIntOptions.ONE})
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                "foo",
                EnumStrOptions.ONE,
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='One')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
        with pytest.raises(VerificationSuccessful):
            client.delete_entity(
                {"PartitionKey": "foo", "RowKey": EnumStrOptions.ONE},
                verify_payload=None,
                verify_url="/foo(PartitionKey='foo',RowKey='One')",
                verify_headers={
                    "Accept":"application/json;odata=minimalmetadata",
                    "If-Match": "*"
                }
            )
