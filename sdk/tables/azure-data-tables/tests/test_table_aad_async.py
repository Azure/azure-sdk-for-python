# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime
import sys

from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from azure.data.tables.aio import TableServiceClient, TableClient

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.data.tables import (
    TableAnalyticsLogging,
    TableMetrics,
    TableRetentionPolicy,
    EntityProperty,
    EdmType,
    TableEntity,
    TransactionOperation,
    UpdateMode,
)

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async


class TestTableAADAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_create_table(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            await ts.create_table(table_name)

            if table_name not in [t.name async for t in ts.list_tables()]:
                raise AssertionError("Table could not be found")

            await ts.delete_table(table_name)
            if table_name in [t.name async for t in ts.list_tables()]:
                raise AssertionError("Table was not deleted")

        finally:
            await ts.delete_table(table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_query_list_tables(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name1 = self._get_table_reference(prefix="table1")
            table_name2 = self._get_table_reference(prefix="table2")
            table_name3 = self._get_table_reference(prefix="table3")
            table_name4 = self._get_table_reference(prefix="table4")
            await ts.create_table(table_name1)
            await ts.create_table(table_name2)
            await ts.create_table(table_name3)
            await ts.create_table(table_name4)

            count = 0
            async for table in ts.list_tables():
                count += 1

            assert count == 4

            query_filter = "TableName eq '{}'".format(table_name2)
            count = 0
            async for table in ts.query_tables(query_filter):
                count += 1
                assert table.name == table_name2
            assert count == 1

        finally:
            async for table in ts.list_tables():
                await ts.delete_table(table.name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_create_table_tc(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            table_client = TableClient(
                credential=self.get_token_credential(), endpoint=account_url, table_name=table_name
            )
            await table_client.create_table()

            if table_name not in [t.name async for t in ts.list_tables()]:
                raise AssertionError("Table could not be found")

            await table_client.delete_table()
            if table_name in [t.name async for t in ts.list_tables()]:
                raise AssertionError("Table was not deleted")

        finally:
            await ts.delete_table(table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_service_properties(self, tables_storage_account_name):
        try:
            account_url = self.account_url(tables_storage_account_name, "table")
            ts = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)
            table_name = self._get_table_reference()
            created = await ts.create_table(table_name)

            assert created.table_name == table_name

            properties = await ts.get_service_properties()
            await ts.set_service_properties(analytics_logging=TableAnalyticsLogging(write=True))
            # have to wait async for return to service
            p = await ts.get_service_properties()
            # have to wait async for return to service
            await ts.set_service_properties(
                minute_metrics=TableMetrics(
                    enabled=True, include_apis=True, retention_policy=TableRetentionPolicy(enabled=True, days=5)
                )
            )

            ps = await ts.get_service_properties()
        finally:
            await ts.delete_table(table_name)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_table_service_stats(self, tables_storage_account_name):
        tsc = TableServiceClient(
            self.account_url(tables_storage_account_name, "table"), credential=self.get_token_credential()
        )
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        self._assert_stats_default(stats)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_insert_entity_dictionary(self, tables_storage_account_name):

        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity = self._create_random_entity_dict()
            resp = await self.table.create_entity(entity=entity)

            self._assert_valid_metadata(resp)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_query_user_filter(self, tables_storage_account_name):

        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity, _ = await self._insert_two_opposite_entities()

            entities = self.table.query_entities("married eq @my_param", parameters={"my_param": entity["married"]})

            assert entities is not None
            length = 0
            async for e in entities:
                self._assert_default_entity(e)
                length += 1

            assert length == 1
        finally:
            await self._tear_down()

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires Python3")
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_batch_all_operations_together(self, tables_storage_account_name):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:

            entity = TableEntity()
            entity["PartitionKey"] = "003"
            entity["RowKey"] = "batch_all_operations_together-1"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()

            await self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-2"
            await self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-3"
            await self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-4"
            await self.table.create_entity(entity)
            transaction_count = 0

            batch = []
            entity["RowKey"] = "batch_all_operations_together"
            batch.append((TransactionOperation.CREATE, entity.copy()))
            transaction_count += 1

            entity["RowKey"] = "batch_all_operations_together-1"
            batch.append((TransactionOperation.DELETE, entity.copy()))
            transaction_count += 1

            entity["RowKey"] = "batch_all_operations_together-2"
            entity["test3"] = 10
            batch.append((TransactionOperation.UPDATE, entity.copy()))
            transaction_count += 1

            entity["RowKey"] = "batch_all_operations_together-3"
            entity["test3"] = 100
            batch.append((TransactionOperation.UPDATE, entity.copy(), {"mode": UpdateMode.REPLACE}))
            transaction_count += 1

            entity["RowKey"] = "batch_all_operations_together-4"
            entity["test3"] = 10
            batch.append((TransactionOperation.UPSERT, entity.copy()))
            transaction_count += 1

            entity["RowKey"] = "batch_all_operations_together-5"
            batch.append((TransactionOperation.UPSERT, entity.copy(), {"mode": UpdateMode.REPLACE}))
            transaction_count += 1

            transaction_result = await self.table.submit_transaction(batch)

            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]
            assert "etag" not in transaction_result[1]
            assert "etag" in transaction_result[2]
            assert "etag" in transaction_result[3]
            assert "etag" in transaction_result[4]
            assert "etag" in transaction_result[5]

            entity_count = 0
            async for e in self.table.query_entities("PartitionKey eq '003'"):
                entity_count += 1
            assert 5 == entity_count
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_access_policy_error(self, tables_storage_account_name):
        account_url = self.account_url(tables_storage_account_name, "table")
        table_name = self._get_table_reference()
        table_client = TableClient(credential=self.get_token_credential(), endpoint=account_url, table_name=table_name)

        with pytest.raises(HttpResponseError):
            await table_client.get_table_access_policy()

        with pytest.raises(HttpResponseError):
            await table_client.set_table_access_policy(signed_identifiers={})

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_delete_entities(self, tables_storage_account_name):
        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity, _ = await self._insert_random_entity()
            await self.table.delete_entity(entity)

            with pytest.raises(ResourceNotFoundError):
                await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_aad_query_user_filter(self, tables_storage_account_name):

        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity, _ = await self._insert_two_opposite_entities()

            entities = self.table.query_entities("married eq @my_param", parameters={"my_param": entity["married"]})

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
    async def test_aad_list_entities(self, tables_storage_account_name):
        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            table = await self._create_query_table(2)

            entities = table.list_entities()

            count = 0
            async for entity in entities:
                self._assert_default_entity(entity)
                count += 1
            assert count == 2
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_merge_entity(self, tables_storage_account_name):
        await self._set_up(tables_storage_account_name, self.get_token_credential())
        try:
            entity, _ = await self._insert_random_entity()

            sent_entity = self._create_updated_entity_dict(entity["PartitionKey"], entity["RowKey"])
            resp = await self.table.update_entity(mode=UpdateMode.MERGE, entity=sent_entity)

            self._assert_valid_metadata(resp)
            received_entity = await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            self._assert_merged_entity(received_entity)
        finally:
            await self._tear_down()
