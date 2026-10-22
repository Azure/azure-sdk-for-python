# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
from datetime import datetime, timezone

from azure.data.tables import EdmType, EntityProperty
from azure.data.tables.aio import TableClient
from azure.data.tables._common_conversion import _to_utc_datetime

from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import _convert_to_entity

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import tables_decorator_async
from test_decoder import _clean


class TestTableDecoderAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_decode_entity_basic(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable011")
        url = self.account_url(tables_storage_account_name, "table")
        responses = {}

        def callback(response):
            responses["response_body"] = response.http_response.json()

        # Test basic string, int32 and bool data
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK'@*$!%", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = await self._convert_to_list(
                client.query_entities("PartitionKey eq 'PK'", raw_response_hook=callback)
            )
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = await self._convert_to_list(client.list_entities(raw_response_hook=callback))
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            await client.delete_table()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_decode_entity_type_conversion(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable02")
        url = self.account_url(tables_storage_account_name, "table")
        responses = {}

        def callback(response):
            responses["response_body"] = response.http_response.json()

        # All automatically detected data types
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
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
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = await self._convert_to_list(
                client.query_entities("PartitionKey eq 'PK'", raw_response_hook=callback)
            )
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = await self._convert_to_list(client.list_entities(raw_response_hook=callback))
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_decode_entity_tuples(
        self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable03")
        url = self.account_url(tables_storage_account_name, "table")
        responses = {}

        def callback(response):
            responses["response_body"] = response.http_response.json()

        # Explicit datatypes using Tuple definition
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.create_table()
            test_entity = {
                "PartitionKey": "PK",
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
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK1", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            test_entity = {
                "PartitionKey": "PK",
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
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK2", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = await self._convert_to_list(
                client.query_entities("PartitionKey eq 'PK'", raw_response_hook=callback)
            )
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = await self._convert_to_list(client.list_entities(raw_response_hook=callback))
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_decode_entity_raw(self, tables_storage_account_name, tables_primary_storage_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable04")
        url = self.account_url(tables_storage_account_name, "table")
        responses = {}

        def callback(response):
            responses["response_body"] = response.http_response.json()

        # Raw payload with existing EdmTypes
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
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
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = await self._convert_to_list(
                client.query_entities("PartitionKey eq 'PK'", raw_response_hook=callback)
            )
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = await self._convert_to_list(client.list_entities(raw_response_hook=callback))
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            await client.delete_table()
        return recorded_variables

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_decode_entity_atypical_values(self, tables_storage_account_name, tables_primary_storage_account_key):
        table_name = self.get_resource_name("uttable05")
        url = self.account_url(tables_storage_account_name, "table")
        responses = {}

        def callback(response):
            responses["response_body"] = response.http_response.json()

        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char, "Data": non_utf8_char}
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", non_utf8_char, raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            max_int64 = 9223372036854775807
            # Valid int64 value with Edm
            test_entity = {"PartitionKey": "PK", "RowKey": "RK2", "Data": (max_int64, "Edm.Int64")}
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK2", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK4",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            created = await client.create_entity(test_entity)
            result = await client.get_entity("PK", "RK4", raw_response_hook=callback)
            old_result = _convert_to_entity(responses["response_body"])
            assert _clean(result) == _clean(old_result), f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = await self._convert_to_list(
                client.query_entities("PartitionKey eq 'PK'", raw_response_hook=callback)
            )
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert str(new) == str(old), f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = await self._convert_to_list(client.list_entities(raw_response_hook=callback))
            old_result = [_convert_to_entity(t) for t in responses["response_body"]["value"]]
            assert len(result) == len(old_result)
            for new, old in zip(result, old_result):
                assert str(new) == str(old), f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            await client.delete_table()
