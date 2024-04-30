# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import pytest
import json
import uuid
import enum
from urllib.parse import quote
from datetime import datetime, timezone
from math import isnan

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import RequestsTransport
from azure.data.tables import TableClient, TableEntityEncoder, EdmType, EntityProperty, UpdateMode
from azure.data.tables._common_conversion import _encode_base64, _to_utc_datetime
from azure.data.tables._serialize import _add_entity_properties

from _shared.testcase import TableTestCase

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live
from preparers import tables_decorator

DEFAULT_ENCODER = TableEntityEncoder()

class MyEncoder(TableEntityEncoder):
    def prepare_key(self, key):
        """Custom key preparer to support key in type UUID, int, float or bool."""
        if isinstance(key, uuid.UUID) or isinstance(key, int) or isinstance(key, float) or isinstance(key, bool):
            key = str(key)
        elif isinstance(key, datetime):
            key = _to_utc_datetime(key)
        elif isinstance(key, bytes):
            key = str(_encode_base64(key))
        elif isinstance(key, enum.Enum): # Support enum in key's value
            key = key.value
        return super().prepare_key(key)

#     def encode_property(self, name, value):
#         if isinstance(value, enum.Enum): # Support enum in normal property's value
#             value = value.value
#         return super().encode_property(name, value)


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


class EncoderVerificationTransport(RequestsTransport):
    def _clean(self, entity):
        cleaned = {}
        for key, value in entity.items():
            if isinstance(value, datetime):
                value = value.astimezone(timezone.utc)
                try:
                    value = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
            if isinstance(value, float) and isnan(value):
                value = "NaN"
            cleaned[key] = value
        return cleaned

    def send(self, request, **kwargs):
        if "verify_payload" in kwargs:
            verification = kwargs.pop("verify_payload")
            sorted_request_body = json.dumps(json.loads(request.body), sort_keys=True)
            assert (
                sorted_request_body == verification
            ), f"Request body:\n'{sorted_request_body}'\ndoes not match expected:\n'{verification}'."
        if "verify_url" in kwargs:
            verification = kwargs.pop("verify_url")
            assert request.url.endswith(
                verification
            ), f"Request URL: '{request.url}' does not match expected: '{verification}'."
        if "verify_headers" in kwargs:
            verification = kwargs.pop("verify_headers")
            for key, value in verification.items():
                try:
                    assert (
                        request.headers[key] == value
                    ), f"Request header: '{key}' with value '{request.headers[key]}' does not match expected: '{value}'."
                except KeyError:
                    raise AssertionError(f"Request missing expected header '{key}' from set: '{request.headers}'.")
        if "verify_response" in kwargs:
            verify, expected = kwargs.pop("verify_response")
            response = super().send(request, **kwargs)
            if response.status_code not in [200, 201, 202, 204]:
                return response
            result = self._clean(verify())
            expected = self._clean(expected)
            assert result == expected, f"The response entity:\n'{result}'\ndoes not match expected:\n'{expected}'"
            return response
        return super().send(request, **kwargs)


def _check_backcompat(entity, new_encoding):
    old_encoding = _add_entity_properties(entity)
    old_encoding = {k: v for k, v in old_encoding.items() if not("@odata.type" in k and v in ["Edm.String", "Edm.Int32", "Edm.Boolean"])}
    new_encoding = {k: v for k, v in new_encoding.items() if v is not None}
    assert old_encoding == new_encoding, f"Old:\n'{old_encoding}'\ndoes not match new:\n'{new_encoding}'."


class TestTableEncoder(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_custom_encoder_entity_keys(self, tables_storage_account_name, tables_primary_storage_account_key):
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
            "PartitionKey": _encode_base64(entity6["PartitionKey"]),
            "RowKey": "1234"
        }
        
        encoded_entity1 = DEFAULT_ENCODER.encode_entity(entity1)
        assert json.dumps(encoded_entity1, sort_keys=True) == json.dumps(expected_entity1, sort_keys=True)
        encoded_entity2 = MyEncoder().encode_entity(entity2)
        assert json.dumps(encoded_entity2, sort_keys=True) == json.dumps(expected_entity2, sort_keys=True)
        encoded_entity3 = MyEncoder().encode_entity(entity3)
        assert json.dumps(encoded_entity3, sort_keys=True) == json.dumps(expected_entity3, sort_keys=True)
        encoded_entity4 = MyEncoder().encode_entity(entity4)
        assert json.dumps(encoded_entity4, sort_keys=True) == json.dumps(expected_entity4, sort_keys=True)
        encoded_entity5 = MyEncoder().encode_entity(entity5)
        assert json.dumps(encoded_entity5, sort_keys=True) == json.dumps(expected_entity5, sort_keys=True)
        encoded_entity6 = MyEncoder().encode_entity(entity6)
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
    def test_custom_encoder_entity_type_conversion(self, tables_storage_account_name, tables_primary_storage_account_key):
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
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity, sort_keys=True)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity)            
            client.delete_entity(entity)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_custom_encoder_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
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
        expected_entity1 = {
            "PartitionKey": "PK",
            "RowKey": "RK",
            "Data1": 12345,
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(entity1["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(entity1["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
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
            "Data1@odata.type": "Edm.Int32",
            "Data2": False,
            "Data2@odata.type": "Edm.Boolean",
            "Data3": _encode_base64(b"testdata"),
            "Data3@odata.type": "Edm.Binary",
            "Data4": _to_utc_datetime(entity1["Data4"][0]),
            "Data4@odata.type": "Edm.DateTime",
            "Data5": str(entity1["Data5"][0]),
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": 3.14,
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity1)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity1, sort_keys=True)
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity2)
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
    def test_custom_encoder_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key):
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
        # We keep the odata type when customer provides
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
            "Data4": entity["Data4"],
            "Data4@odata.type": "Edm.DateTime",
            "Data5": entity["Data5"],
            "Data5@odata.type": "Edm.Guid",
            "Data6": "Foobar",
            "Data6@odata.type": "Edm.String",
            "Data7": "3.14",
            "Data7@odata.type": "Edm.Double",
            "Data8": "1152921504606846976",
            "Data8@odata.type": "Edm.Int64"
        }
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity, sort_keys=True)
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity)
            client.delete_entity(entity)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_custom_encoder_entity_atypical_values(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        entity1 = {
            "PartitionKey": "PK1",
            "RowKey": "你好",
            "Data":  "你好"
        }
        # Test big int value
        # previousely, we throw an error when value is not in range.
        # TODO: This will likely change if we move to post-request validation.
        max_int64 = 2 ** 63
        entity2 = {
            "PartitionKey": "PK2",
            "RowKey": "RK",
            "Data": max_int64
        }
        entity3 = {
            "PartitionKey": "PK3",
            "RowKey": "RK",
            "Data": (max_int64, "Edm.Int64") # Bad request, InvalidInput
        }
        expected_entity3 = {
            "PartitionKey": "PK3",
            "RowKey": "RK",
            "Data": str(max_int64),
            "Data@odata.type": "Edm.Int64"
        }
        # Test infinite float values
        entity4 = {
            "PartitionKey": "PK4",
            "RowKey": "RK",
            "Data1": float('nan'),
            "Data2": float('inf'),
            "Data3": float('-inf')
        }
        expected_entity4 = {
            "PartitionKey": "PK4",
            "RowKey": "RK",
            "Data1":  "NaN",
            "Data1@odata.type": "Edm.Double",
            "Data2": "Infinity",
            "Data2@odata.type": "Edm.Double",
            "Data3": "-Infinity",
            "Data3@odata.type": "Edm.Double"
        }
        # Test Non-string keys
        entity5 = {
            "PartitionKey": "PK5",
            "RowKey": "RK",
            123: 456
        }
        expected_entity5 = {
            "PartitionKey": "PK5",
            "RowKey": "RK",
            123: 456 # HttpResponseError, code: PropertyNameInvalid
        }
        # Test enums
        # TBD: support it in default encoder?
        entity6 = {
            "PartitionKey": "PK6",
            "RowKey": EnumBasicOptions.ONE,
            "Data": EnumBasicOptions.TWO
        }
        # Support the enum by adding conversions in a customized encoder
        expected_entity6 = {
            "PartitionKey": "PK6",
            "RowKey": "One",
            "Data": "Two"
        }
        entity7 = {
            "PartitionKey": "PK7",
            "RowKey": EnumIntOptions.ONE,
            "Data": EnumIntOptions.TWO
        }
        # Key's value always be string type
        # For enum value in normal properties: EnumIntOptions -> int, EnumBasicOptions/EnumStrOptions -> string
        expected_entity7 = {
            "PartitionKey": "PK7",
            "RowKey": "1",
            "Data": 2
        }
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity1)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(entity1, sort_keys=True)
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity2)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(entity2, sort_keys=True)
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity3)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity3, sort_keys=True)
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity4)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity4, sort_keys=True)
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity5)
        assert encoded_entity == expected_entity5
        encoded_entity = DEFAULT_ENCODER.encode_entity(entity6)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity6, sort_keys=True)
        encoded_entity = MyEncoder().encode_entity(entity7)
        assert json.dumps(encoded_entity, sort_keys=True) == json.dumps(expected_entity7, sort_keys=True)

        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity1) # no edm type in get and list results
            client.delete_entity(entity1)
            client.create_entity(entity2)
            client.delete_entity(entity2)
            with pytest.raises(HttpResponseError) as exc:
                client.create_entity(entity3)
            assert ("Operation returned an invalid status 'Bad Request'") in str(exc.value)
            assert exc.value.response.json()['odata.error']['code'] == "InvalidInput"
            client.create_entity(entity4)
            client.delete_entity(entity4)
            with pytest.raises(HttpResponseError) as exc:
                client.create_entity(entity5)
            assert ("Operation returned an invalid status 'Bad Request'") in str(exc.value)
            assert exc.value.response.json()['odata.error']['code'] == "PropertyNameInvalid"
            client.create_entity(entity6)
            client.delete_entity(entity6)
            client.create_entity(entity7, encoder=MyEncoder())
            client.delete_entity(entity7, encoder=MyEncoder())
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable01")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 1,
                "Data2": True,
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK'@*$!%"
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(test_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = {"PartitionKey": "PK", "RowKey": 1}
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = {"PartitionKey": "PK", "RowKey": True}
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {"PartitionKey": "PK", "RowKey": 3.14, "RowKey@odata.type": "Edm.Double"}
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable02")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {
                "PartitionKey": self.get_datetime(),
                "RowKey": recorded_uuid,
            }
            expected_entity = {
                "PartitionKey": _to_utc_datetime(test_entity["PartitionKey"]),
                "PartitionKey@odata.type": "Edm.DateTime",
                "RowKey": str(test_entity["RowKey"]),
                "RowKey@odata.type": "Edm.Guid",
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"

            test_entity = {
                "PartitionKey": b"binarydata",
                "RowKey": 1234,
            }
            expected_entity = {
                "PartitionKey": _encode_base64(test_entity["PartitionKey"]),
                "PartitionKey@odata.type": "Edm.Binary",
                "RowKey": 1234,
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable03")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": recorded_uuid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": None,
            }
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(test_entity["Data4"]),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(test_entity["Data5"]),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
                "Data8": None,
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(
                    lambda: client.get_entity("PK", "RK"),
                    {k: v for k, v in test_entity.items() if v is not None},
                ),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable04")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": (12345, EdmType.INT32),
                "Data2": (False, "Edm.Boolean"),
                "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
                "Data4": EntityProperty(
                    datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                    "Edm.DateTime",
                ),
                "Data5": EntityProperty(recorded_uuid, "Edm.Guid"),
                "Data6": ("Foobar", EdmType.STRING),
                "Data7": (3.14, EdmType.DOUBLE),
                "Data8": (2**60, "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data1@odata.type": "Edm.Int32", # diff: this is not in old encoded result
                "Data2": False,
                "Data2@odata.type": "Edm.Boolean", # diff: this is not in old encoded result
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(test_entity["Data4"][0]),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(test_entity["Data5"][0]),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String", # diff: this is not in old encoded result
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
            }
            # expected_backcompat_entity = {
            #     "PartitionKey": "PK1",
            #     "RowKey": "RK1",
            #     "Data1": 12345,
            #     "Data2": False,
            #     "Data3": _encode_base64(b"testdata"),
            #     "Data3@odata.type": "Edm.Binary",
            #     "Data4": _to_utc_datetime(test_entity["Data4"][0]),
            #     "Data4@odata.type": "Edm.DateTime",
            #     "Data5": str(test_entity["Data5"][0]),
            #     "Data5@odata.type": "Edm.Guid",
            #     "Data6": "Foobar",
            #     "Data7": 3.14,
            #     "Data7@odata.type": "Edm.Double",
            #     "Data8": "1152921504606846976",
            #     "Data8@odata.type": "Edm.Int64"
            # }
            response_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                "Data5": test_entity["Data5"][0],
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": EntityProperty(2**60, EdmType.INT64),
            }
            # _check_backcompat(test_entity, expected_entity) # will fail
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": ("12345", EdmType.INT32),
                "Data2": ("False", "Edm.Boolean"),
                "Data3": (None, EdmType.STRING),
                "Data4": EntityProperty(
                    _to_utc_datetime(datetime(2022, 4, 1, 9, 30, 45, tzinfo=timezone.utc)), "Edm.DateTime"
                ),
                "Data5": EntityProperty("9b8fbe91-a1d8-46bb-99b6-09e1a6afd9cf", "Edm.Guid"),
                "Data6": (None, EdmType.BOOLEAN),
                "Data7": EntityProperty("3.14", "Edm.Double"),
                "Data8": ("9223372036854775807", "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": None,
                "Data3@odata.type": "Edm.String",
                "Data4": test_entity["Data4"][0],
                "Data4@odata.type": "Edm.DateTime",
                "Data5": test_entity["Data5"][0],
                "Data5@odata.type": "Edm.Guid",
                "Data6": None,
                "Data6@odata.type": "Edm.Boolean",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "9223372036854775807",
                "Data8@odata.type": "Edm.Int64",
            }
            # expected_backcompat_entity = {
            #     "PartitionKey": "PK2",
            #     "RowKey": "RK2",
            #     "Data1": 12345, # diff: is "12345" in new encoded result
            #     "Data1@odata.type": "Edm.Int32",
            #     "Data2": "False",
            #     "Data2@odata.type": "Edm.Boolean",
            #     "Data4": test_entity["Data4"][0],
            #     "Data4@odata.type": "Edm.DateTime",
            #     "Data5": test_entity["Data5"][0],
            #     "Data5@odata.type": "Edm.Guid",
            #     "Data7": "3.14",
            #     "Data7@odata.type": "Edm.Double",
            #     "Data8": "9223372036854775807",
            #     "Data8@odata.type": "Edm.Int64",
            # }
            response_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data2": False,
                "Data4": datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc),
                "Data5": uuid.UUID(test_entity["Data5"][0]),
                "Data7": 3.14,
                "Data8": (9223372036854775807, "Edm.Int64"),
            }
            # _check_backcompat(test_entity, expected_entity) # will fail
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable05")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            dt = self.get_datetime()
            guid = recorded_uuid
            test_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": b"testdata",
                "Data3@odata.type": "Edm.Binary",
                "Data4": dt,
                "Data4@odata.type": "Edm.DateTime",
                "Data5": guid,
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
            }
            expected_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
            }
            # expected_backcompat_entity = {
            #     "PartitionKey": "PK",
            #     "PartitionKey@odata.type": "Edm.String",
            #     "PartitionKey@odata.type@odata.type": "Edm.String", # this is not correct in old encoder
            #     "RowKey": "RK",
            #     "RowKey@odata.type": "Edm.String",
            #     "RowKey@odata.type@odata.type": "Edm.String",
            #     "Data1": "12345",
            #     "Data1@odata.type": "Edm.Int32",
            #     "Data1@odata.type@odata.type": "Edm.String",
            #     "Data2": "False",
            #     "Data2@odata.type": "Edm.Boolean",
            #     "Data2@odata.type@odata.type": "Edm.String",
            #     "Data3": "dGVzdGRhdGE=",
            #     "Data3@odata.type": "Edm.Binary",
            #     "Data3@odata.type@odata.type": "Edm.String",
            #     "Data4": "2022-04-01T09:30:45.000000Z",
            #     "Data4@odata.type": "Edm.DateTime",
            #     "Data4@odata.type@odata.type": "Edm.String",
            #     "Data5": "5cda0aeb-9b88-4811-b522-c0d0a96f55c2",
            #     "Data5@odata.type": "Edm.Guid",
            #     "Data5@odata.type@odata.type": "Edm.String",
            #     "Data6": "Foobar",
            #     "Data6@odata.type": "Edm.String",
            #     "Data6@odata.type@odata.type": "Edm.String",
            #     "Data7": "3.14",
            #     "Data7@odata.type": "Edm.Double",
            #     "Data7@odata.type@odata.type": "Edm.String",
            #     "Data8": "1152921504606846976",
            #     "Data8@odata.type": "Edm.Int64",
            #     "Data8@odata.type@odata.type": "Edm.String"
            # }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": dt,
                "Data5": guid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (1152921504606846976, "Edm.Int64"),
            }
            # _check_backcompat(test_entity, expected_entity) # will fail
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_create_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable06")
        url = self.account_url(tables_storage_account_name, "table")
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            # Non-UTF8 characters in both keys and properties
            test_entity = {"PartitionKey": "PK", "RowKey": "你好", "Data": "你好"}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "你好",
                "Data": "你好"
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "你好"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            # TODO: Check whether other languages support big int32. Also Cosmos.
            # TODO: This will likely change if we move to post-request validation.
            max_int64 = 9223372036854775808
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int(max_int64 * 1000)}
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data": int(max_int64 * 1000)
            }
            # _check_backcompat(test_entity, expected_entity) # this will fail, as the old encoder has int value range validation.
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK1", "RK1"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 - 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 - 1),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            # _check_backcompat(test_entity, expected_entity) # this will fail, as the old encoder has int value range validation.
            with pytest.raises(HttpResponseError) as error:
                resp = client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert ("Operation returned an invalid status 'Bad Request'") in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "InvalidInput"

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK4", "RK4"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                123: 456,
            }
            # expected_backcompat_entity = {
            #     "PartitionKey": "PK",
            #     "PartitionKey@odata.type": "Edm.String",
            #     "RowKey": "RK",
            #     "RowKey@odata.type": "Edm.String",
            #     123: 456,
            # }
            # _check_backcompat(test_entity, expected_entity) # will fail, TypeError: argument of type 'int' is not iterable
            with pytest.raises(HttpResponseError) as error:
                client.create_entity(
                    test_entity,
                    # verify_payload=expected_entity, # this will fail as the request body is: {"123": 456, "PartitionKey": "PK", "RowKey": "RK"}
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert error.value.response.json()['odata.error']['code'] == "PropertyNameInvalid"

            # Test enums - it is not supported in old encoder
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "One",
                "Data": "Two",
            }
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", EnumBasicOptions.ONE.value), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumStrOptions.TWO, "Data": EnumStrOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "Two",
                "Data": "Two",
            }
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            if not is_live() and sys.version_info < (3, 11):
                pytest.skip("The recording works in python3.11 and later.")
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data": EnumIntOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data": 2,
            }
            resp = client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable07")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 1,
                "Data2": True,
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK'@*$!%",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = {"PartitionKey": "PK", "RowKey": "1"}
            expected_backcompat_entity = {"PartitionKey": "PK", "RowKey": 1}
            response_entity = {"PartitionKey": "PK", "RowKey": 1}
            _check_backcompat(test_entity, expected_backcompat_entity) # this will fail, as odata type were added for pk and rk
            client.upsert_entity(test_entity, mode="merge")
            resp = client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.upsert_entity(test_entity, mode="replace")
            resp = client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "1"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = {"PartitionKey": "PK", "RowKey": "True"}
            _check_backcompat(test_entity, expected_entity) # this will fail, as odata type were added for pk and rk
            client.upsert_entity(test_entity, mode="merge")
            resp = client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='True')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "True"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.upsert_entity(test_entity, mode="replace")
            resp = client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='True')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "True"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 3.14,                          
                "RowKey@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity) # this will fail, as odata type were added for pk and rk
            client.upsert_entity(test_entity, mode="merge")
            resp = client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='True')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "True"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                client.upsert_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable08")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            client.create_table()
            test_entity = {
                "PartitionKey": self.get_datetime(),
                "RowKey": recorded_uuid,
                "Data": True,
            }
            pk = _to_utc_datetime(test_entity["PartitionKey"])
            rk = str(test_entity["RowKey"])
            expected_entity = {
                "PartitionKey": pk,
                "RowKey": rk,
                "Data": True,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": True}
            # _check_backcompat(test_entity, expected_entity) # this will fail, as odata type were added for pk and rk
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"{table_name}(PartitionKey='{quote(pk)}',RowKey='{quote(rk)}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{quote(rk)}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": b"binarydata", "RowKey": "1234", "Data": 1}
            pk = _encode_base64(test_entity["PartitionKey"])
            rk = test_entity["RowKey"]
            expected_entity = {
                "PartitionKey": pk,
                "RowKey": rk,
                "Data": 1,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": 1}
            # _check_backcompat(test_entity, expected_entity) # this will fail, as odata type were added for pk and rk
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable09")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            test_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": recorded_uuid,
                "Data6": "Foobar",
                "Data7": 3.14,
            }
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(test_entity["Data4"]),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(test_entity["Data5"]),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable10")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            dt = datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc)
            guid = recorded_uuid
            test_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": (12345, EdmType.INT32),
                "Data2": (False, "Edm.Boolean"),
                "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
                "Data4": EntityProperty(dt, "Edm.DateTime"),
                "Data5": EntityProperty(guid, "Edm.Guid"),
                "Data6": ("Foobar", EdmType.STRING),
                "Data7": (3.14, EdmType.DOUBLE),
                "Data8": (2**60, "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data1@odata.type": "Edm.INT32",
                "Data2": False,
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.STRING",
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
            }
            response_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": dt,
                "Data5": guid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (2**60, "Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": ("12345", EdmType.INT32),
                "Data2": ("False", "Edm.Boolean"),
                "Data3": (None, EdmType.STRING),
                "Data4": EntityProperty(_to_utc_datetime(dt), "Edm.DateTime"),
                "Data5": EntityProperty(str(guid), "Edm.Guid"),
                "Data6": (None, EdmType.BOOLEAN),
                "Data7": EntityProperty("3.14", "Edm.Double"),
                "Data8": ("9223372036854775807", "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data1@odata.type": "Edm.INT32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": None,
                "Data3@odata.type": "Edm.STRING",
                "Data4": test_entity["Data4"][0],
                "Data4@odata.type": "Edm.DateTime",
                "Data5": test_entity["Data5"][0],
                "Data5@odata.type": "Edm.Guid",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "9223372036854775807",
                "Data8@odata.type": "Edm.Int64",
            }
            response_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data2": False,
                "Data4": dt,
                "Data5": guid,
                "Data7": 3.14,
                "Data8": (9223372036854775807, "Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable11")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            dt = self.get_datetime()
            guid = recorded_uuid
            test_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",  # EdmType.INT32,  TODO: Should we fix enums?
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
                "Data9": b"testdata",
                "Data9@odata.type": "Edm.Binary",
                "Data10": dt,
                "Data10@odata.type": "Edm.DateTime",
                "Data11": guid,
                "Data11@odata.type": "Edm.Guid",
            }
            expected_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
                "Data9": _encode_base64(b"testdata"),
                "Data9@odata.type": "Edm.Binary",
                "Data10": _to_utc_datetime(dt),
                "Data10@odata.type": "Edm.DateTime",
                "Data11": str(guid),
                "Data11@odata.type": "Edm.Guid",
            }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": dt,
                "Data5": guid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (1152921504606846976, "Edm.Int64"),
                "Data9": b"testdata",
                "Data10": dt,
                "Data11": guid,
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_upsert_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable12")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            # Non-UTF8 characters in both keys and properties
            test_entity = {"PartitionKey": "PK", "RowKey": "你好", "Data": "你好"}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "你好",
                "Data": "你好",
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "你好"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "你好"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            # TODO: Check with other languages whether they can support big int32. Also Cosmos.
            # TODO: This will likely change if we move to post-request validation.
            max_int64 = 9223372036854775808
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int(max_int64 * 1000)}
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data": int(max_int64 * 1000),
            }
            with pytest.raises(TypeError):
                _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError):
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK1", "RK1"), test_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
            with pytest.raises(TypeError):
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK1", "RK1"), test_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 - 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 - 1),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK2", "RK2"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK2", "RK2"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            with pytest.raises(TypeError):
                _check_backcompat(test_entity, expected_entity)
            # with pytest.raises(HttpResponseError) as error:
            with pytest.raises(TypeError) as error:
                client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            # assert error.value.error_code == "InvalidInput"
            # with pytest.raises(HttpResponseError) as error:
            with pytest.raises(TypeError) as error:
                client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            # assert error.value.error_code == "InvalidInput"

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK4',RowKey='RK4')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK4", "RK4"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK4',RowKey='RK4')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK4", "RK4"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                123: 456,
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            # TODO: The code introduced to serialize to support odata types raises a TypeError here. Need to investigate the best approach.
            with pytest.raises(HttpResponseError) as error:
                client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert error.value.error_code == "PropertyNameInvalid"
            with pytest.raises(HttpResponseError) as error:
                client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert error.value.error_code == "PropertyNameInvalid"

            # Test enums
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            # TODO: This looks like it was always broken
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "EnumBasicOptions.ONE",
                "Data": "EnumBasicOptions.TWO",
            }
            response_entity = {"PartitionKey": "PK", "RowKey": "EnumBasicOptions.ONE", "Data": "EnumBasicOptions.TWO"}
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "EnumBasicOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "EnumBasicOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumStrOptions.ONE, "Data": EnumStrOptions.TWO}
            # TODO: This looks like it was always broken
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "EnumStrOptions.ONE",
                "Data": "EnumStrOptions.TWO",
            }
            response_entity = {"PartitionKey": "PK", "RowKey": "EnumStrOptions.ONE", "Data": "EnumStrOptions.TWO"}
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity)
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "EnumStrOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "EnumStrOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            if not is_live() and sys.version_info < (3, 11):
                pytest.skip("The recording works in python3.11 and later.")
            test_entity = {"PartitionKey": "PK", "RowKey": EnumIntOptions.ONE, "Data": EnumIntOptions.TWO}
            # TODO: This is a bit weird
            # TODO: This changes between Python 3.10 and 3.11
            if sys.version_info >= (3, 11):
                expected_entity = {
                    "PartitionKey": "PK",
                    "RowKey": "1",
                    "Data": "2",
                }
                response_entity = {"PartitionKey": "PK", "RowKey": "1", "Data": "2"}
                _check_backcompat(test_entity, expected_entity)
                verification = json.dumps(expected_entity)
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK", "1"), response_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK", "1"), response_entity),
                )
            else:
                expected_entity = {
                    "PartitionKey": "PK",
                    "RowKey": "EnumIntOptions.ONE",
                    "Data": "EnumIntOptions.TWO",
                }
                response_entity = {"PartitionKey": "PK", "RowKey": "EnumIntOptions.ONE", "Data": "EnumIntOptions.TWO"}
                _check_backcompat(test_entity, expected_entity)
                verification = json.dumps(expected_entity)
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumIntOptions.ONE')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK", "EnumIntOptions.ONE"), response_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
                resp = client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumIntOptions.ONE')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    verify_response=(lambda: client.get_entity("PK", "EnumIntOptions.ONE"), response_entity),
                )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable13")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 1,
                "Data2": True,
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            resp = client.update_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%", "Data": True}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK'@*$!%",
                "Data": True,
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK'@*$!%"})
            resp = client.update_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = {"PartitionKey": "PK", "RowKey": 1}
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = {"PartitionKey": "PK", "RowKey": True}
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 3.14,
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable14")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            test_entity = {
                "PartitionKey": self.get_datetime(),
                "RowKey": recorded_uuid,
                "Data": True,
            }
            pk = _to_utc_datetime(test_entity["PartitionKey"])
            rk = str(test_entity["RowKey"])
            expected_entity = {
                "PartitionKey": pk,
                "RowKey": rk,
                "Data": True,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": True}
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": pk, "RowKey": rk})
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{quote(rk)}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{quote(rk)}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": b"binarydata", "RowKey": "1234", "Data": 1}
            pk = _encode_base64(test_entity["PartitionKey"])
            rk = str(test_entity["RowKey"])
            expected_entity = {
                "PartitionKey": pk,
                "RowKey": rk,
                "Data": 1,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": 1}
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": pk, "RowKey": rk})
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable15")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            test_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": recorded_uuid,
                "Data6": "Foobar",
                "Data7": 3.14,
            }
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(test_entity["Data4"]),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(test_entity["Data5"]),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable16")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            dt = datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc)
            guid = recorded_uuid
            test_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": (12345, EdmType.INT32),
                "Data2": (False, "Edm.Boolean"),
                "Data3": EntityProperty(value=b"testdata", edm_type=EdmType.BINARY),
                "Data4": EntityProperty(dt, "Edm.DateTime"),
                "Data5": EntityProperty(guid, "Edm.Guid"),
                "Data6": ("Foobar", EdmType.STRING),
                "Data7": (3.14, EdmType.DOUBLE),
                "Data8": (2**60, "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data1@odata.type": "Edm.Int32",
                "Data2": False,
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": 3.14,
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
            }
            response_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": dt,
                "Data5": guid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (2**60, "Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK1", "RowKey": "RK1"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": ("12345", EdmType.INT32),
                "Data2": ("False", "Edm.Boolean"),
                "Data3": (None, EdmType.STRING),
                "Data4": EntityProperty(_to_utc_datetime(dt), "Edm.DateTime"),
                "Data5": EntityProperty(str(guid), "Edm.Guid"),
                "Data6": (None, EdmType.BOOLEAN),
                "Data7": EntityProperty("3.14", "Edm.Double"),
                "Data8": ("9223372036854775807", "Edm.Int64"),
            }
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": None,
                "Data3@odata.type": "EdmType.STRING",
                "Data4": test_entity["Data4"][0],
                "Data4@odata.type": "Edm.DateTime",
                "Data5": test_entity["Data5"][0],
                "Data5@odata.type": "Edm.Guid",
                "Data6": None,
                "Data6@odata.type": "EdmType.BOOLEAN",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "9223372036854775807",
                "Data8@odata.type": "Edm.Int64",
            }
            response_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data2": False,
                "Data4": dt,
                "Data5": guid,
                "Data7": 3.14,
                "Data8": (9223372036854775807, "Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK2", "RowKey": "RK2"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable17")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            dt = self.get_datetime()
            guid = recorded_uuid
            test_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",  # EdmType.INT32,  TODO: Should we fix enums?
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
                "Data9": b"testdata",
                "Data9@odata.type": "Edm.Binary",
                "Data10": dt,
                "Data10@odata.type": "Edm.DateTime",
                "Data11": guid,
                "Data11@odata.type": "Edm.Guid",
            }
            expected_entity = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "12345",
                "Data1@odata.type": "Edm.Int32",
                "Data2": "False",
                "Data2@odata.type": "Edm.Boolean",
                "Data3": _encode_base64(b"testdata"),
                "Data3@odata.type": "Edm.Binary",
                "Data4": _to_utc_datetime(dt),
                "Data4@odata.type": "Edm.DateTime",
                "Data5": str(guid),
                "Data5@odata.type": "Edm.Guid",
                "Data6": "Foobar",
                "Data6@odata.type": "Edm.String",
                "Data7": "3.14",
                "Data7@odata.type": "Edm.Double",
                "Data8": "1152921504606846976",
                "Data8@odata.type": "Edm.Int64",
                "Data9": _encode_base64(b"testdata"),
                "Data9@odata.type": "Edm.Binary",
                "Data10": _to_utc_datetime(dt),
                "Data10@odata.type": "Edm.DateTime",
                "Data11": str(guid),
                "Data11@odata.type": "Edm.Guid",
            }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": dt,
                "Data5": guid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (1152921504606846976, "Edm.Int64"),
                "Data9": b"testdata",
                "Data10": dt,
                "Data11": guid,
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()
        return recorded_variables

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_update_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable18")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            # Non-UTF8 characters in both keys and properties
            test_entity = {"PartitionKey": "PK", "RowKey": "你好", "Data": "你好"}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "你好",
                "Data": "你好",
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "你好"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "你好"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "你好"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            # TODO: Check with other languages whether they can support big int32. Also Cosmos.
            # TODO: This will likely change if we move to post-request validation.
            max_int64 = 9223372036854775808
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int(max_int64 * 1000)}
            expected_entity = {
                "PartitionKey": "PK1",
                "RowKey": "RK1",
                "Data": int(max_int64 * 1000),
            }
            client.upsert_entity({"PartitionKey": "PK1", "RowKey": "RK1"})
            with pytest.raises(TypeError):
                _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError):
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK1", "RK1"), test_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
            with pytest.raises(TypeError):
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK1", "RK1"), test_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 - 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 - 1),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK2", "RowKey": "RK2"})
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity),
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            with pytest.raises(TypeError):
                _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK3", "RowKey": "RK3"})
            # with pytest.raises(HttpResponseError) as error:
            with pytest.raises(TypeError):
                client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            # assert error.value.error_code == "InvalidInput"
            # with pytest.raises(HttpResponseError) as error:
            with pytest.raises(TypeError):
                client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity),
                    verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            # assert error.value.error_code == "InvalidInput"

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK4",
                "RowKey": "RK4",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK4", "RowKey": "RK4"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK4',RowKey='RK4')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK4", "RK4"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK4',RowKey='RK4')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK4", "RK4"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                123: 456,
            }
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity)
            # TODO: The code introduced to serialize to support odata types raises a TypeError here. Need to investigate the best approach.
            with pytest.raises(HttpResponseError) as error:
                client.update_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert error.value.error_code == "PropertyNameInvalid"
            with pytest.raises(HttpResponseError) as error:
                client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert error.value.error_code == "PropertyNameInvalid"

            # Test enums
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            # TODO: This looks like it was always broken
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "EnumBasicOptions.ONE",
                "Data": "EnumBasicOptions.TWO",
            }
            response_entity = {"PartitionKey": "PK", "RowKey": "EnumBasicOptions.ONE", "Data": "EnumBasicOptions.TWO"}
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "EnumBasicOptions.ONE"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "EnumBasicOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumBasicOptions.ONE')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "EnumBasicOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumStrOptions.ONE, "Data": EnumStrOptions.TWO}
            # TODO: This looks like it was always broken
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "EnumStrOptions.ONE",
                "Data": "EnumStrOptions.TWO",
            }
            response_entity = {"PartitionKey": "PK", "RowKey": "EnumStrOptions.ONE", "Data": "EnumStrOptions.TWO"}
            _check_backcompat(test_entity, expected_entity)
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "EnumStrOptions.ONE"})
            verification = json.dumps(expected_entity)
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "EnumStrOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumStrOptions.ONE')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "EnumStrOptions.ONE"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            if not is_live() and sys.version_info < (3, 11):
                pytest.skip("The recording works in python3.11 and later.")
            test_entity = {"PartitionKey": "PK", "RowKey": EnumIntOptions.ONE, "Data": EnumIntOptions.TWO}
            # TODO: This is a bit weird
            # TODO: This changes between Python 3.10 and 3.11
            if sys.version_info >= (3, 11):
                expected_entity = {
                    "PartitionKey": "PK",
                    "RowKey": "1",
                    "Data": "2",
                }
                response_entity = {"PartitionKey": "PK", "RowKey": "1", "Data": "2"}
                _check_backcompat(test_entity, expected_entity)
                client.upsert_entity({"PartitionKey": "PK", "RowKey": "1"})
                verification = json.dumps(expected_entity)
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK", "1"), response_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='1')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK", "1"), response_entity),
                )
            else:
                expected_entity = {
                    "PartitionKey": "PK",
                    "RowKey": "EnumIntOptions.ONE",
                    "Data": "EnumIntOptions.TWO",
                }
                response_entity = {"PartitionKey": "PK", "RowKey": "EnumIntOptions.ONE", "Data": "EnumIntOptions.TWO"}
                _check_backcompat(test_entity, expected_entity)
                client.upsert_entity({"PartitionKey": "PK", "RowKey": "EnumIntOptions.ONE"})
                verification = json.dumps(expected_entity)
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumIntOptions.ONE')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK", "EnumIntOptions.ONE"), response_entity),
                )
                assert list(resp.keys()) == ["date", "etag", "version"]
                resp = client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='EnumIntOptions.ONE')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                    verify_response=(lambda: client.get_entity("PK", "EnumIntOptions.ONE"), response_entity),
                )
            assert list(resp.keys()) == ["date", "etag", "version"]
        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_delete_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable19")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            client.upsert_entity({"PartitionKey": "foo", "RowKey": "bar"})
            resp = client.delete_entity(
                "foo",
                "bar",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            client.upsert_entity({"PartitionKey": "foo", "RowKey": "bar"})
            resp = client.delete_entity(
                {"PartitionKey": "foo", "RowKey": "bar"},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            client.upsert_entity({"PartitionKey": "foo", "RowKey": "RK'@*$!%"})
            resp = client.delete_entity(
                "foo",
                "RK'@*$!%",  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            client.upsert_entity({"PartitionKey": "foo", "RowKey": "RK'@*$!%"})
            resp = client.delete_entity(
                {"PartitionKey": "foo", "RowKey": "RK'@*$!%"},  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

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

        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_delete_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable20")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )

        with pytest.raises(TypeError):
            client.delete_entity("foo", self.get_datetime())
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": self.get_datetime()})
        with pytest.raises(TypeError):
            client.delete_entity("foo", recorded_uuid)
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": recorded_uuid})
        with pytest.raises(TypeError):
            client.delete_entity("foo", b"binarydata")
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": b"binarydata"})

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_delete_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable21")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )

        with pytest.raises(TypeError):
            client.delete_entity("foo", EntityProperty("bar", "Edm.String"))
        with pytest.raises(TypeError):
            client.delete_entity({"PartitionKey": "foo", "RowKey": ("bar", EdmType.STRING)})

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_delete_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable22")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Test enums in both keys and properties
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            # Non-UTF8 characters in both keys and properties
            client.upsert_entity({"PartitionKey": "PK", "RowKey": "你好"})
            resp = client.delete_entity(
                "PK",
                "你好",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            client.upsert_entity({"PartitionKey": "PK", "RowKey": "你好"})
            resp = client.delete_entity(
                {"PartitionKey": "PK", "RowKey": "你好"},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            with pytest.raises(TypeError):
                client.delete_entity("foo", EnumBasicOptions.ONE)
            with pytest.raises(TypeError):
                client.delete_entity({"PartitionKey": "foo", "RowKey": EnumBasicOptions.ONE})
            with pytest.raises(TypeError):
                client.delete_entity("foo", EnumIntOptions.ONE)
            with pytest.raises(TypeError):
                client.delete_entity({"PartitionKey": "foo", "RowKey": EnumIntOptions.ONE})

            client.upsert_entity({"PartitionKey": "foo", "RowKey": "One"})
            resp = client.delete_entity(
                "foo",
                EnumStrOptions.ONE,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            client.upsert_entity({"PartitionKey": "foo", "RowKey": "One"})
            resp = client.delete_entity(
                {"PartitionKey": "foo", "RowKey": EnumStrOptions.ONE},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None
        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_get_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable23")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            test_entity = {"PartitionKey": "foo", "RowKey": "bar"}
            client.upsert_entity(test_entity)
            resp = client.get_entity(
                "foo",
                "bar",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            test_entity = {"PartitionKey": "foo", "RowKey": "RK'@*$!%"}
            client.upsert_entity(test_entity)
            resp = client.get_entity(
                "foo",
                "RK'@*$!%",  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            with pytest.raises(TypeError):
                client.get_entity("foo", 1)
            with pytest.raises(TypeError):
                client.get_entity("foo", True)
            with pytest.raises(TypeError):
                client.get_entity("foo", 3.14)

        finally:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_get_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable24")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )

        with pytest.raises(TypeError):
            client.get_entity("foo", self.get_datetime())
        with pytest.raises(TypeError):
            client.get_entity("foo", recorded_uuid)
        with pytest.raises(TypeError):
            client.get_entity("foo", b"binarydata")

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_get_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable25")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )

        with pytest.raises(TypeError):
            client.get_entity("foo", EntityProperty("bar", "Edm.String"))

    @tables_decorator
    @recorded_by_proxy
    def test_encoder_get_entity_atypical_values(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable26")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Test enums in both keys and properties
        client = TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        )
        client.create_table()
        try:
            # Non-UTF8 characters in both keys and properties
            test_entity = {"PartitionKey": "PK", "RowKey": "你好"}
            client.upsert_entity(test_entity)
            resp = client.get_entity(
                "PK",
                "你好",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='%E4%BD%A0%E5%A5%BD')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            with pytest.raises(TypeError):
                client.get_entity("foo", EnumBasicOptions.ONE)
            with pytest.raises(TypeError):
                client.get_entity("foo", EnumIntOptions.ONE)

            test_entity = {"PartitionKey": "foo", "RowKey": "One"}
            client.upsert_entity(test_entity)
            resp = client.get_entity(
                "foo",
                EnumStrOptions.ONE,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity
        finally:
            client.delete_table()
