# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
from datetime import datetime, timezone

from azure.data.tables import TableClient, EdmType, EntityProperty
from azure.data.tables._common_conversion import _to_utc_datetime

from _shared.testcase import TableTestCase

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import cosmos_decorator
from test_decoder import MyDecoder, _clean


class TestTableDecoderCosmos(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_decode_entity_basic(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        table_name = self.get_resource_name("uttable01")
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        # Test basic string, int32 and bool data
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
            test_entity = {"PartitionKey": "PK", "RowKey": "RK", "Data1": 1, "Data2": True}
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK")
            old_result = client.get_entity("PK", "RK", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            test_entity = {"PartitionKey": "PK", "RowKey": "RK'@*$!%"}
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK'@*$!%")
            old_result = client.get_entity("PK", "RK'@*$!%", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = client.query_entities("PartitionKey eq 'PK'")
            old_result = client.query_entities("PartitionKey eq 'PK'", decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = client.list_entities()
            old_result = client.list_entities(decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            client.delete_table()

    @cosmos_decorator
    @recorded_by_proxy
    def test_decode_entity_type_conversion(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key, **kwargs
    ):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable03")
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        # All automatically detected data types
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
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
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK")
            old_result = client.get_entity("PK", "RK", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = client.query_entities("PartitionKey eq 'PK'")
            old_result = client.query_entities("PartitionKey eq 'PK'", decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = client.list_entities()
            old_result = client.list_entities(decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            client.delete_table()
        return recorded_variables

    @cosmos_decorator
    @recorded_by_proxy
    def test_decode_entity_tuples(self, tables_cosmos_account_name, tables_primary_cosmos_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable04")
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        # Explicit datatypes using Tuple definition
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
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
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK1")
            old_result = client.get_entity("PK", "RK1", decoder=MyDecoder())
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
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK2")
            old_result = client.get_entity("PK", "RK2", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = client.query_entities("PartitionKey eq 'PK'")
            old_result = client.query_entities("PartitionKey eq 'PK'", decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = client.list_entities()
            old_result = client.list_entities(decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            client.delete_table()
        return recorded_variables

    @cosmos_decorator
    @recorded_by_proxy
    def test_decode_entity_raw(self, tables_cosmos_account_name, tables_primary_cosmos_account_key, **kwargs):
        recorded_variables = kwargs.pop("variables", {})
        recorded_uuid = self.set_uuid_variable(recorded_variables, "uuid", uuid.uuid4())
        table_name = self.get_resource_name("uttable05")
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        # Raw payload with existing EdmTypes
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
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

            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK")
            old_result = client.get_entity("PK", "RK", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = client.query_entities("PartitionKey eq 'PK'")
            old_result = client.query_entities("PartitionKey eq 'PK'", decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = client.list_entities()
            old_result = client.list_entities(decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert new == old, f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            client.delete_table()
        return recorded_variables

    @cosmos_decorator
    @recorded_by_proxy
    def test_decode_entity_atypical_values(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        table_name = self.get_resource_name("uttable06")
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            client.create_table()
            # Non-UTF8 characters in both keys and properties
            non_utf8_char = "你好"
            test_entity = {"PartitionKey": "PK", "RowKey": non_utf8_char, "Data": non_utf8_char}
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", non_utf8_char)
            old_result = client.get_entity("PK", non_utf8_char, decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            # Valid int64 value with Edm
            max_int64 = 9223372036854775807
            test_entity = {"PartitionKey": "PK", "RowKey": "RK2", "Data": (max_int64, "Edm.Int64")}
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK2")
            old_result = client.get_entity("PK", "RK2", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            # Valid int64 value without Edm
            test_entity = {"PartitionKey": "PK", "RowKey": "RK3", "Data": max_int64}
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK3")
            old_result = client.get_entity("PK", "RK3", decoder=MyDecoder())
            assert result == old_result, f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            # Infinite float values
            test_entity = {
                "PartitionKey": "PK",
                "RowKey": "RK4",
                "Data1": float("nan"),
                "Data2": float("inf"),
                "Data3": float("-inf"),
            }
            created = client.create_entity(test_entity)
            result = client.get_entity("PK", "RK4")
            old_result = client.get_entity("PK", "RK4", decoder=MyDecoder())
            assert _clean(result) == _clean(old_result), f"Old:\n'{old_result}'\ndoes not match new:\n'{result}'."

            result = client.query_entities("PartitionKey eq 'PK'")
            old_result = client.query_entities("PartitionKey eq 'PK'", decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert _clean(new) == _clean(old), f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            result = client.list_entities()
            old_result = client.list_entities(decoder=MyDecoder())
            assert len(list(result)) == len(list(old_result))
            for new, old in zip(result, old_result):
                assert _clean(new) == _clean(old), f"Old:\n'{old}'\ndoes not match new:\n'{new}'."

            client.delete_table()
