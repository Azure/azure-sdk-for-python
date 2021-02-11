# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from datetime import datetime

from azure.data.tables import (
    TableServiceClient,
    TableClient,
    EdmType,
    EntityProperty
)
from azure.core.exceptions import ResourceExistsError

from _shared.testcase import TableTestCase, SLEEP_DELAY
from preparers import TablesPreparer, CosmosPreparer


class MyEntity(object):
    def __init__(self, entry_element):
        self.properties = {}
        self.partition_key = entry_element.pop("PartitionKey")
        self.row_key = entry_element.pop("RowKey")
        self.timestamp = entry_element.pop("Timestamp")

        properties = {}
        edmtypes = {}
        odata = {}

        for name, value in entry_element.items():
            if name.startswith("odata."):
                odata[name[6:]] = value
            elif name.endswith("@odata.type"):
                edmtypes[name[:-11]] = value
            else:
                properties[name] = value

        for name, value in properties.items():
            mtype = edmtypes.get(name)

            # Use Simple Ints
            if type(value) is int and mtype in [EdmType.INT32, EdmType.INT64]:
                self.properties[name] = int(value)
                continue

            # Add type for String
            try:
                if type(value) is unicode and mtype is None:
                    self.properties[name] = unicode(value)
                    continue
            except NameError:
                if type(value) is str and mtype is None:  # pylint:disable=C0123
                    self.properties[name] = str(value)
                    continue

            self.properties[name] = value

        self.convert_birthdays()

    def convert_birthdays(self):
        if "birthday" in self.properties.keys():
            (
                self.properties["birthday"],
                self.properties["milliseconds"],
            ) = self._convert_date(self.properties["birthday"])
        if "Birthday" in self.properties.keys():
            (
                self.properties["Birthday"],
                self.properties["milliseconds"],
            ) = self._convert_date(self.properties["Birthday"])

    def _convert_date(self, bday):
        if "Z" in bday:
            # Has milliseconds, we'll handle this separately
            # Python library only handles 6 decimal places of precision
            ms = bday.split(".")[-1]
            ms = "." + ms[:-1]
            ms = float(ms)
            date = bday.split(".")[0]
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            return date, ms
        else:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"), 0.0

    def keys(self):
        return self.properties.keys()


def modify_returned_class(entity):
    if "birthday" in entity.keys():
        bday = entity["birthday"]
        if "Z" in bday:
            ms = bday.split(":")[-1]
            ms = "." + ms
            ms = float(ms)
            date = bday.replace(str(ms), "")
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
            entity["birthday"] = date
            entity["birthday_ms"] = ms
    if "Birthday" in entity.keys():
        bday = entity["birthday"]
        if "Z" in bday:
            ms = bday.split(":")[-1]
            ms = "." + ms
            ms = float(ms)
            date = bday.replace(str(ms), "")
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
            entity["Birthday"] = date
            entity["Birthday_ms"] = ms

    return entity


class StorageTableEntityTest(TableTestCase):
    def _set_up(
        self,
        tables_storage_account_name,
        tables_primary_storage_account_key,
        url="table",
    ):
        table_name = self.get_resource_name("uttable")
        ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            table_name=table_name,
        )
        table = ts.get_table_client(table_name)
        if self.is_live:
            try:
                ts.create_table(table_name)
            except ResourceExistsError:
                pass
        return table

    def _tear_down(
        self,
        tables_storage_account_name,
        tables_primary_storage_account_key,
        url="table",
    ):
        table_name = self.get_resource_name("uttable")
        ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            table_name=table_name,
        )
        if self.is_live:
            try:
                ts.delete_table(table_name)
            except:
                pass

    @TablesPreparer()
    def test_custom_entity(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_client = self._set_up(
            tables_storage_account_name, tables_primary_storage_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                entity = tc.get_entity(
                    partition_key=entity[u"PartitionKey"],
                    row_key=entity[u"RowKey"],
                    entity_hook=MyEntity,
                )

                assert isinstance(entity.properties["Birthday"], datetime)
                assert "milliseconds" in entity.keys()
                assert entity.properties["milliseconds"] == 0.0123456
                assert entity.properties["Birthday"] == datetime(2020, 1, 1, 12, 59, 59)

        finally:
            self._tear_down(
                tables_storage_account_name, tables_primary_storage_account_key
            )

    @TablesPreparer()
    def test_custom_entity_edmtype(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_client = self._set_up(
            tables_storage_account_name, tables_primary_storage_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": EntityProperty(
                type=EdmType.DATETIME,
                value=u"2020-01-01T12:59:59.0123456Z"
            )
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                entity = tc.get_entity(
                    partition_key=entity[u"PartitionKey"],
                    row_key=entity[u"RowKey"],
                    entity_hook=MyEntity,
                )

                assert isinstance(entity.properties["Birthday"], datetime)
                assert "milliseconds" in entity.keys()
                assert entity.properties["milliseconds"] == 0.0123456
                assert entity.properties["Birthday"] == datetime(2020, 1, 1, 12, 59, 59)

        finally:
            self._tear_down(
                tables_storage_account_name, tables_primary_storage_account_key
            )

    @TablesPreparer()
    def test_custom_entity_list(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_client = self._set_up(
            tables_storage_account_name, tables_primary_storage_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
        }
        entity2 = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk1",
            u"Birthday": u"2021-02-02T12:59:59.0123456Z",
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                tc.create_entity(entity2)
                entities = tc.list_entities(entity_hook=MyEntity)

                length = 0
                for entity in entities:
                    assert isinstance(entity.properties["Birthday"], datetime)
                    assert "milliseconds" in entity.keys()
                    assert entity.properties["milliseconds"] == 0.0123456
                    length += 1
                assert length == 2

        finally:
            self._tear_down(
                tables_storage_account_name, tables_primary_storage_account_key
            )

    @TablesPreparer()
    def test_custom_entity_query(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        table_client = self._set_up(
            tables_storage_account_name, tables_primary_storage_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
            u"Value": 20,
        }
        entity2 = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk1",
            u"Birthday": u"2021-02-02T12:59:59.0123456Z",
            u"Value": 30,
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                tc.create_entity(entity2)

                f = "Value lt @value"
                params = {"value": 25}
                entities = tc.query_entities(
                    filter=f, parameters=params, entity_hook=MyEntity
                )

                length = 0
                for entity in entities:
                    assert isinstance(entity.properties["Birthday"], datetime)
                    assert "milliseconds" in entity.keys()
                    assert entity.properties["milliseconds"] == 0.0123456
                    length += 1
                assert length == 1

        finally:
            self._tear_down(
                tables_storage_account_name, tables_primary_storage_account_key
            )


class CosmosTableEntityTest(TableTestCase):
    def _set_up(
        self,
        tables_storage_account_name,
        tables_primary_storage_account_key,
        url="cosmos",
    ):
        table_name = self.get_resource_name("uttable")
        ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            table_name=table_name,
        )
        table = ts.get_table_client(table_name)
        if self.is_live:
            try:
                ts.create_table(table_name)
            except ResourceExistsError:
                pass
        return table

    def _tear_down(
        self,
        tables_storage_account_name,
        tables_primary_storage_account_key,
        url="cosmos",
    ):
        table_name = self.get_resource_name("uttable")
        ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            table_name=table_name,
        )
        if self.is_live:
            try:
                ts.delete_table(table_name)
            except:
                pass
        self.sleep(SLEEP_DELAY)

    @CosmosPreparer()
    def test_custom_entity_cosmos(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        table_client = self._set_up(
            tables_cosmos_account_name, tables_primary_cosmos_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                entity = tc.get_entity(
                    partition_key=entity[u"PartitionKey"],
                    row_key=entity[u"RowKey"],
                    entity_hook=MyEntity,
                )

                assert isinstance(entity.properties["Birthday"], datetime)
                assert "milliseconds" in entity.keys()
                assert entity.properties["milliseconds"] == 0.0123456
                assert entity.properties["Birthday"] == datetime(2020, 1, 1, 12, 59, 59)

        finally:
            self._tear_down(
                tables_cosmos_account_name, tables_primary_cosmos_account_key
            )

    @CosmosPreparer()
    def test_custom_entity_list_cosmos(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        table_client = self._set_up(
            tables_cosmos_account_name, tables_primary_cosmos_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
        }
        entity2 = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk1",
            u"Birthday": u"2021-02-02T12:59:59.0123456Z",
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                tc.create_entity(entity2)
                entities = tc.list_entities(entity_hook=MyEntity)

                length = 0
                for entity in entities:
                    assert isinstance(entity.properties["Birthday"], datetime)
                    assert "milliseconds" in entity.keys()
                    assert entity.properties["milliseconds"] == 0.0123456
                    length += 1
                assert length == 2

        finally:
            self._tear_down(
                tables_cosmos_account_name, tables_primary_cosmos_account_key
            )

    @CosmosPreparer()
    def test_custom_entity_query_cosmos(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        table_client = self._set_up(
            tables_cosmos_account_name, tables_primary_cosmos_account_key
        )

        entity = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk",
            u"Birthday": u"2020-01-01T12:59:59.0123456Z",
            u"Value": 20,
        }
        entity2 = {
            u"PartitionKey": u"pk",
            u"RowKey": u"rk1",
            u"Birthday": u"2021-02-02T12:59:59.0123456Z",
            u"Value": 30,
        }
        try:
            with table_client as tc:
                tc.create_entity(entity)
                tc.create_entity(entity2)

                f = "Value lt @value"
                params = {"value": 25}
                entities = tc.query_entities(
                    filter=f, parameters=params, entity_hook=MyEntity
                )

                length = 0
                for entity in entities:
                    assert isinstance(entity.properties["Birthday"], datetime)
                    assert "milliseconds" in entity.keys()
                    assert entity.properties["milliseconds"] == 0.0123456
                    length += 1
                assert length == 1

        finally:
            self._tear_down(
                tables_cosmos_account_name, tables_primary_cosmos_account_key
            )
