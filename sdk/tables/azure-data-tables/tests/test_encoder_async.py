# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import json
import uuid
from urllib.parse import quote
from datetime import datetime, timezone
from math import isnan

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AioHttpTransport
from azure.data.tables import EdmType, EntityProperty, UpdateMode
from azure.data.tables.aio import TableClient
from azure.data.tables._common_conversion import _encode_base64, _to_utc_datetime

from _shared.asynctestcase import AsyncTableTestCase

from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import tables_decorator_async
from test_encoder import (
    EnumBasicOptions,
    EnumStrOptions,
    EnumIntOptions,
    EncoderVerificationTransport,
    _check_backcompat,
)


class EncoderVerificationTransport(AioHttpTransport):
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

    async def send(self, request, **kwargs):
        if "verify_payload" in kwargs:
            verification = kwargs.pop("verify_payload")
            if verification is not None:
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
            response = await super().send(request, **kwargs)
            if response.status_code not in [200, 201, 202, 204]:
                return response
            result = self._clean(await verify())
            expected = self._clean(expected)
            assert result == expected, f"The response entity:\n'{result}'\ndoes not match expected:\n'{expected}'"
            return response
        return await super().send(request, **kwargs)


class TestTableEncoderAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable01")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 3.14,
                "RowKey@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable02")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )

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
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable03")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            resp = await client.create_entity(
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
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable04")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
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
                "Data1": 12345,
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
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_raw(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable05")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_create_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable06")
        url = self.account_url(tables_storage_account_name, "table")
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char, "Data": non_utf8_char}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", non_utf8_char), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            max_int64 = 9223372036854775807
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int((max_int64 + 1) * 1000)}
            with pytest.raises(TypeError) as error:
                await client.create_entity(test_entity)
            assert "is too large to be cast to" in str(error.value)

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 + 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 + 1),
                "Data@odata.type": "Edm.Int64",
            }
            with pytest.raises(TypeError) as error:
                _check_backcompat(test_entity, expected_entity)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(HttpResponseError) as error:
                resp = await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"An error occurred while processing this request.'
                in str(error.value)
            )

            # Valid int64 value with Edm
            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK3", "RK3"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Valid int64 value without Edm
            test_entity = {"PartitionKey": "PK4", "RowKey": "RK4", "Data": max_int64}
            with pytest.raises(TypeError) as error:
                await client.create_entity(test_entity)
            assert "is too large to be cast to" in str(error.value)

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK5", "RK5"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = test_entity
            expected_payload_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "123": 456,  # "123" is an invalid property name
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(HttpResponseError) as error:
                await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_payload_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"odata.error":{"code":"PropertyNameInvalid","message":{"lang":"en-US","value":"The property name is invalid.'
                in str(error.value)
            )

            # Test enums - it is not supported in old encoder
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "One",
                "Data": "Two",
            }
            resp = await client.create_entity(
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
            resp = await client.create_entity(
                test_entity,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}",
                verify_headers={"Content-Type": "application/json;odata=nometadata"},
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumIntOptions.ONE, "Data": EnumIntOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 1,
                "Data": 2,
            }
            with pytest.raises(HttpResponseError) as error:
                resp = await client.create_entity(
                    test_entity,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}",
                    verify_headers={"Content-Type": "application/json;odata=nometadata"},
                    verify_response=(lambda: client.get_entity("PK", "1"), expected_entity),
                )
            assert "Operation returned an invalid status 'Bad Request'" in str(error.value)
            assert (
                '"code":"InvalidInput","message":{"lang":"en-US","value":"One of the request inputs is not valid.'
                in str(error.value)
            )
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable07")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            resp = await client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            resp = await client.upsert_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 3.14,
                "RowKey@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable08")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {
                "PartitionKey": self.get_datetime(),
                "RowKey": recorded_uuid,
                "Data": True,
            }
            pk = _to_utc_datetime(test_entity["PartitionKey"])
            rk = str(test_entity["RowKey"])
            expected_entity = {
                "PartitionKey": pk,
                "PartitionKey@odata.type": "Edm.DateTime",
                "RowKey": rk,
                "RowKey@odata.type": "Edm.Guid",
                "Data": True,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": True}
            _check_backcompat(test_entity, expected_entity)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
                "PartitionKey@odata.type": "Edm.Binary",
                "RowKey": rk,
                "Data": 1,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": 1}
            _check_backcompat(test_entity, expected_entity)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable09")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable10X")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
            response_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data2": False,
                "Data4": dt,
                "Data5": guid,
                "Data7": 3.14,
                "Data8": EntityProperty(value=9223372036854775807, edm_type="Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_raw(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable11")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            #     "Data3": _encode_base64(b"testdata"),
            #     "Data3@odata.type": "Edm.Binary",
            #     "Data3@odata.type@odata.type": "Edm.String",
            #     "Data4": _to_utc_datetime(dt),
            #     "Data4@odata.type": "Edm.DateTime",
            #     "Data4@odata.type@odata.type": "Edm.String",
            #     "Data5": str(guid),
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
            #     "Data8@odata.type@odata.type": "Edm.String",
            #     "Data9": _encode_base64(b"testdata"),
            #     "Data9@odata.type": "Edm.Binary",
            #     "Data9@odata.type@odata.type": "Edm.String",
            #     "Data10": _to_utc_datetime(dt),
            #     "Data10@odata.type": "Edm.DateTime",
            #     "Data10@odata.type@odata.type": "Edm.String",
            #     "Data11": str(guid),
            #     "Data11@odata.type": "Edm.Guid",
            #     "Data11@odata.type@odata.type": "Edm.String",
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
                "Data9": b"testdata",
                "Data10": dt,
                "Data11": guid,
            }
            # _check_backcompat(test_entity, expected_entity) # will fail
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
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
            resp = await client.upsert_entity(
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
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_upsert_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable12")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char, "Data": non_utf8_char}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", non_utf8_char), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", non_utf8_char), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            max_int64 = 9223372036854775807
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int((max_int64 + 1) * 1000)}
            expected_entity = test_entity
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.MERGE)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.REPLACE)
            assert "is too large to be cast to" in str(error.value)

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 + 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 + 1),
                "Data@odata.type": "Edm.Int64",
            }
            with pytest.raises(TypeError) as error:
                _check_backcompat(test_entity, expected_entity)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(HttpResponseError) as error:
                await client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert "An error occurred while processing this request." in str(error.value)
            assert error.value.error_code == "InvalidInput"
            with pytest.raises(HttpResponseError) as error:
                await client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert "An error occurred while processing this request." in str(error.value)
            assert error.value.error_code == "InvalidInput"

            # Valid int64 value with Edm
            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK3", "RK3"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK3", "RK3"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Valid int64 value without Edm
            test_entity = {"PartitionKey": "PK4", "RowKey": "RK4", "Data": max_int64}
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.MERGE)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.REPLACE)
            assert "is too large to be cast to" in str(error.value)

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK5',RowKey='RK5')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK5", "RK5"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK5',RowKey='RK5')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK5", "RK5"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = test_entity
            # _check_backcompat(test_entity, expected_entity) # will fail, TypeError: argument of type 'int' is not iterable
            expected_payload_entity = {"PartitionKey": "PK", "RowKey": "RK", "123": 456}
            verification = json.dumps(expected_payload_entity, sort_keys=True)
            with pytest.raises(HttpResponseError) as error:
                await client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert "The property name is invalid" in str(error.value)
            assert error.value.error_code.value == "PropertyNameInvalid"
            with pytest.raises(HttpResponseError) as error:
                await client.upsert_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
            assert "The property name is invalid" in str(error.value)
            assert error.value.error_code.value == "PropertyNameInvalid"

            # Test enums - it is not supported in old encoder
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "One",
                "Data": "Two",
            }
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='One')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "One"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='One')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "One"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumStrOptions.TWO, "Data": EnumStrOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "Two",
                "Data": "Two",
            }
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='Two')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='Two')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data": EnumIntOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data": 2,
            }
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.upsert_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                verify_response=(lambda: client.get_entity("PK", "RK"), expected_entity),
            )
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable13")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            resp = await client.update_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%", "Data": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK'@*$!%"})
            resp = await client.update_entity(
                test_entity,
                mode="merge",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode="replace",
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": 1}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": True}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "PK", "RowKey": 3.14}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": 3.14,
                "RowKey@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="merge")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode="replace")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable14")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {
                "PartitionKey": self.get_datetime(),
                "RowKey": recorded_uuid,
                "Data": True,
            }
            pk = _to_utc_datetime(test_entity["PartitionKey"])
            rk = str(test_entity["RowKey"])
            expected_entity = {
                "PartitionKey": pk,
                "PartitionKey@odata.type": "Edm.DateTime",
                "RowKey": rk,
                "RowKey@odata.type": "Edm.Guid",
                "Data": True,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": True}
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": pk, "RowKey": rk})
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{quote(rk)}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
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
                "PartitionKey@odata.type": "Edm.Binary",
                "RowKey": rk,
                "Data": 1,
            }
            response_entity = {"PartitionKey": pk, "RowKey": rk, "Data": 1}
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": pk, "RowKey": rk})
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='{quote(pk)}',RowKey='{rk}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity(pk, rk), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable15")
        url = self.account_url(tables_storage_account_name, "table")
        # All automatically detected data types
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable16")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            await client.upsert_entity({"PartitionKey": "PK1", "RowKey": "RK1"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK1',RowKey='RK1')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK1", "RK1"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
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
            response_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data1": 12345,
                "Data2": False,
                "Data4": dt,
                "Data5": guid,
                "Data7": 3.14,
                "Data8": EntityProperty(value=9223372036854775807, edm_type="Edm.Int64"),
            }
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK2", "RowKey": "RK2"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK2", "RK2"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_raw(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable17")
        url = self.account_url(tables_storage_account_name, "table")
        # Raw payload with existing EdmTypes
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
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
            #     "Data3": _encode_base64(b"testdata"),
            #     "Data3@odata.type": "Edm.Binary",
            #     "Data3@odata.type@odata.type": "Edm.String",
            #     "Data4": _to_utc_datetime(dt),
            #     "Data4@odata.type": "Edm.DateTime",
            #     "Data4@odata.type@odata.type": "Edm.String",
            #     "Data5": str(guid),
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
            #     "Data8@odata.type@odata.type": "Edm.String",
            #     "Data9": _encode_base64(b"testdata"),
            #     "Data9@odata.type": "Edm.Binary",
            #     "Data9@odata.type@odata.type": "Edm.String",
            #     "Data10": _to_utc_datetime(dt),
            #     "Data10@odata.type": "Edm.DateTime",
            #     "Data10@odata.type@odata.type": "Edm.String",
            #     "Data11": str(guid),
            #     "Data11@odata.type": "Edm.Guid",
            #     "Data11@odata.type@odata.type": "Edm.String",
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
                "Data9": b"testdata",
                "Data10": dt,
                "Data11": guid,
            }
            # _check_backcompat(test_entity, expected_entity) # will fail
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_update_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable18")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Invalid int32 and int64 values
        # Infinite float values
        # Non-string keys
        # Test enums
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char, "Data": non_utf8_char}
            expected_entity = test_entity
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": non_utf8_char})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", non_utf8_char), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", non_utf8_char), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Invalid int32 and int64 values
            max_int64 = 9223372036854775807
            test_entity = {"PartitionKey": "PK1", "RowKey": "RK1", "Data": int((max_int64 + 1) * 1000)}
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.MERGE)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.upsert_entity(test_entity, mode=UpdateMode.REPLACE)
            assert "is too large to be cast to" in str(error.value)

            test_entity = {"PartitionKey": "PK2", "RowKey": "RK2", "Data": (max_int64 + 1, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK2",
                "RowKey": "RK2",
                "Data": str(max_int64 + 1),
                "Data@odata.type": "Edm.Int64",
            }
            with pytest.raises(TypeError) as error:
                _check_backcompat(test_entity, expected_entity)
            assert "is too large to be cast to" in str(error.value)
            await client.upsert_entity({"PartitionKey": "PK2", "RowKey": "RK2"})
            with pytest.raises(HttpResponseError) as error:
                await client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert "An error occurred while processing this request" in str(error.value)
            assert error.value.error_code == "InvalidInput"
            with pytest.raises(HttpResponseError) as error:
                await client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=json.dumps(expected_entity, sort_keys=True),
                    verify_url=f"/{table_name}(PartitionKey='PK2',RowKey='RK2')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert "An error occurred while processing this request" in str(error.value)
            assert error.value.error_code == "InvalidInput"

            # Valid int64 value with Edm
            test_entity = {"PartitionKey": "PK3", "RowKey": "RK3", "Data": (max_int64, "Edm.Int64")}
            expected_entity = {
                "PartitionKey": "PK3",
                "RowKey": "RK3",
                "Data": str(max_int64),
                "Data@odata.type": "Edm.Int64",
            }
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK3", "RowKey": "RK3"})
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK3", "RK3"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=json.dumps(expected_entity, sort_keys=True),
                verify_url=f"/{table_name}(PartitionKey='PK3',RowKey='RK3')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK3", "RK3"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Valid int64 value without Edm
            test_entity = {"PartitionKey": "PK4", "RowKey": "RK4", "Data": max_int64}
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode=UpdateMode.MERGE)
            assert "is too large to be cast to" in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.update_entity(test_entity, mode=UpdateMode.REPLACE)
            assert "is too large to be cast to" in str(error.value)

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            expected_entity = {
                "PartitionKey": "PK5",
                "RowKey": "RK5",
                "Data1": "NaN",
                "Data1@odata.type": "Edm.Double",
                "Data2": "Infinity",
                "Data2@odata.type": "Edm.Double",
                "Data3": "-Infinity",
                "Data3@odata.type": "Edm.Double",
            }
            _check_backcompat(test_entity, expected_entity)
            await client.upsert_entity({"PartitionKey": "PK5", "RowKey": "RK5"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK5',RowKey='RK5')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK5", "RK5"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK5',RowKey='RK5')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK5", "RK5"), test_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            # Non-string keys
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", 123: 456}
            expected_entity = test_entity
            # _check_backcompat(test_entity, expected_entity) # will fail, TypeError: argument of type 'int' is not iterable
            expected_payload_entity = {"PartitionKey": "PK", "RowKey": "RK", "123": 456}
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_payload_entity, sort_keys=True)
            with pytest.raises(HttpResponseError) as error:
                await client.update_entity(
                    test_entity,
                    mode=UpdateMode.MERGE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert "The property name is invalid" in str(error.value)
            assert error.value.error_code.value == "PropertyNameInvalid"
            with pytest.raises(HttpResponseError) as error:
                await client.update_entity(
                    test_entity,
                    mode=UpdateMode.REPLACE,
                    verify_payload=verification,
                    verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                    verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                )
            assert "The property name is invalid" in str(error.value)
            assert error.value.error_code.value == "PropertyNameInvalid"

            # Test enums - it is not supported in old encoder
            test_entity = {"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE, "Data": EnumBasicOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "One",
                "Data": "Two",
            }
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": EnumBasicOptions.ONE})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='One')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "One"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='One')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "One"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": EnumStrOptions.TWO, "Data": EnumStrOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "Two",
                "Data": "Two",
            }
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "Two"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='Two')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='Two')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "Two"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]

            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data": EnumIntOptions.TWO}
            expected_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data": 2,
            }
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": "RK"})
            verification = json.dumps(expected_entity, sort_keys=True)
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.MERGE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            resp = await client.update_entity(
                test_entity,
                mode=UpdateMode.REPLACE,
                verify_payload=verification,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='RK')",
                verify_headers={"Content-Type": "application/json", "Accept": "application/json", "If-Match": "*"},
                verify_response=(lambda: client.get_entity("PK", "RK"), expected_entity),
            )
            assert list(resp.keys()) == ["date", "etag", "version"]
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_delete_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable19")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "bar"})
            resp = await client.delete_entity(
                "foo",
                "bar",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "bar"})
            resp = await client.delete_entity(
                {"PartitionKey": "foo", "RowKey": "bar"},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "RK'@*$!%"})
            resp = await client.delete_entity(
                "foo",
                "RK'@*$!%",  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "RK'@*$!%"})
            resp = await client.delete_entity(
                {"PartitionKey": "foo", "RowKey": "RK'@*$!%"},  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", 1)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity({"PartitionKey": "foo", "RowKey": 1})
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", True)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity({"PartitionKey": "foo", "RowKey": True})
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", 3.14)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity({"PartitionKey": "foo", "RowKey": 3.14})
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_delete_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable20")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:

            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", self.get_datetime())
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_entity({"PartitionKey": "foo", "RowKey": self.get_datetime()})
            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", recorded_uuid)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_entity({"PartitionKey": "foo", "RowKey": recorded_uuid})
            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", b"binarydata")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_entity({"PartitionKey": "foo", "RowKey": b"binarydata"})
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_delete_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable21")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:

            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", EntityProperty("bar", "Edm.String"))
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_entity({"PartitionKey": "foo", "RowKey": ("bar", EdmType.STRING)})

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_delete_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable22")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Test enums in both keys and properties
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            await client.upsert_entity({"PartitionKey": "PK", "RowKey": non_utf8_char})
            resp = await client.delete_entity(
                "PK",
                non_utf8_char,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            await client.upsert_entity({"PartitionKey": "PK", "RowKey": non_utf8_char})
            resp = await client.delete_entity(
                {"PartitionKey": "PK", "RowKey": non_utf8_char},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", EnumBasicOptions.ONE)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            await client.delete_entity({"PartitionKey": "foo", "RowKey": EnumBasicOptions.ONE})
            with pytest.raises(TypeError) as error:
                await client.delete_entity("foo", EnumIntOptions.ONE)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.delete_entity({"PartitionKey": "foo", "RowKey": EnumIntOptions.ONE})
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "One"})
            resp = await client.delete_entity(
                "foo",
                EnumStrOptions.ONE,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None

            await client.upsert_entity({"PartitionKey": "foo", "RowKey": "One"})
            resp = await client.delete_entity(
                {"PartitionKey": "foo", "RowKey": EnumStrOptions.ONE},
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata", "If-Match": "*"},
            )
            assert resp is None
            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_get_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable23")
        url = self.account_url(tables_storage_account_name, "table")
        # Test basic string, int32 and bool data
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity = {"PartitionKey": "foo", "RowKey": "bar"}
            await client.upsert_entity(test_entity)
            resp = await client.get_entity(
                "foo",
                "bar",
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='bar')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            test_entity = {"PartitionKey": "foo", "RowKey": "RK'@*$!%"}
            await client.upsert_entity(test_entity)
            resp = await client.get_entity(
                "foo",
                "RK'@*$!%",  # cspell:disable-line
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='RK%27%27%40%2A%24%21%25')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", 1)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", True)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", 3.14)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_get_entity_complex_keys(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable24")
        url = self.account_url(tables_storage_account_name, "table")
        # Test complex PartitionKey and RowKey (datetime, GUID and binary)
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:

            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", self.get_datetime())
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", recorded_uuid)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", b"binarydata")
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_get_entity_tuples(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable25")
        url = self.account_url(tables_storage_account_name, "table")
        # Explicit datatypes using Tuple definition
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:

            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", EntityProperty("bar", "Edm.String"))
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_get_entity_atypical_values(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_name = self.get_resource_name("uttable26")
        url = self.account_url(tables_storage_account_name, "table")
        # Non-UTF8 characters in both keys and properties
        # Test enums in both keys and properties
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char}
            await client.upsert_entity(test_entity)
            resp = await client.get_entity(
                "PK",
                non_utf8_char,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='PK',RowKey='{quote(non_utf8_char)}')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity

            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", EnumBasicOptions.ONE)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)
            with pytest.raises(TypeError) as error:
                await client.get_entity("foo", EnumIntOptions.ONE)
            assert "PartitionKey or RowKey must be of type string." in str(error.value)

            test_entity = {"PartitionKey": "foo", "RowKey": "One"}
            await client.upsert_entity(test_entity)
            resp = await client.get_entity(
                "foo",
                EnumStrOptions.ONE,
                verify_payload=None,
                verify_url=f"/{table_name}(PartitionKey='foo',RowKey='One')",
                verify_headers={"Accept": "application/json;odata=minimalmetadata"},
            )
            assert resp == test_entity
            await client.delete_table()

    @pytest.mark.live_test_only
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_encoder_batch(self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable27")
        url = self.account_url(tables_storage_account_name, "table")
        async with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=EncoderVerificationTransport()
        ) as client:
            await client.create_table()
            test_entity1 = {
                "PartitionKey": "PK",
                "RowKey": "RK'@*$!%",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": None,
            }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK'@*$!%",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
            }
            resp = await client.submit_transaction(
                [("create", test_entity1)],
                verify_response=(lambda: client.get_entity("PK", "RK'@*$!%"), response_entity),
            )
            assert list(resp[0].keys()) == ["etag"]

            test_entity2 = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": EntityProperty(recorded_uuid, "Edm.Guid"),
                "Data6": ("Foobar", EdmType.STRING),
                "Data7": (3.14, EdmType.DOUBLE),
                "Data8": (2**60, "Edm.Int64"),
            }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 12345,
                "Data2": False,
                "Data3": b"testdata",
                "Data4": self.get_datetime(),
                "Data5": recorded_uuid,
                "Data6": "Foobar",
                "Data7": 3.14,
                "Data8": (2**60, "Edm.Int64"),
            }
            resp = await client.submit_transaction(
                [("upsert", test_entity2, {"mode": "merge"})],
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp[0].keys()) == ["etag"]
            resp = await client.submit_transaction(
                [("upsert", test_entity2, {"mode": "replace"})],
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp[0].keys()) == ["etag"]

            test_entity3 = {
                "PartitionKey": "PK",
                "PartitionKey@odata.type": "Edm.String",
                "RowKey": "RK",
                "RowKey@odata.type": "Edm.String",
                "Data1": "3.14",
                "Data1@odata.type": "Edm.Double",
                "Data2": "1152921504606846976",
                "Data2@odata.type": "Edm.Int64",
                "Data3": "你好",
                "Data4": float("nan"),
                "Data5": float("inf"),
                "Data6": float("-inf"),
                "Data7": EnumBasicOptions.ONE,
                "Data8": EnumStrOptions.ONE,
            }
            response_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK",
                "Data1": 3.14,
                "Data2": (1152921504606846976, "Edm.Int64"),
                "Data3": "你好",
                "Data4": float("nan"),
                "Data5": float("inf"),
                "Data6": float("-inf"),
                "Data7": "One",
                "Data8": "One",
            }
            resp = await client.submit_transaction(
                [("update", test_entity3, {"mode": "merge"})],
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp[0].keys()) == ["etag"]
            resp = await client.submit_transaction(
                [("update", test_entity3, {"mode": "replace"})],
                verify_response=(lambda: client.get_entity("PK", "RK"), response_entity),
            )
            assert list(resp[0].keys()) == ["etag"]

            await client.submit_transaction([("delete", test_entity1), ("delete", test_entity3)])

            await client.delete_table()
        return recorded_variables
