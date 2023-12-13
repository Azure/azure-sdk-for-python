# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
import os
from unittest.mock import Mock
import pytest
from functools import partial
from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core import MatchConditions
from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.rest._aiohttp import RestAioHttpTransportResponse
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError, HttpResponseError
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.data.tables import (
    TableEntity,
    UpdateMode,
    EntityProperty,
    EdmType,
    TableTransactionError,
    generate_table_sas,
    TableSasPermissions,
    RequestTooLargeError,
    TransactionOperation,
    TableErrorCode,
)
from azure.data.tables._constants import DEFAULT_STORAGE_ENDPOINT_SUFFIX
from azure.identity.aio import DefaultAzureCredential
from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async


class TestTableBatchAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_single_insert(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_insert"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()

            batch = [("create", entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            e = await self.table.get_entity(row_key=entity["RowKey"], partition_key=entity["PartitionKey"])
            assert e["test"] == entity["test"].value
            assert e["test2"] == entity["test2"]
            assert e["test3"] == entity["test3"]
            assert e["test4"] == entity["test4"].value
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_single_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_insert"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()

            resp = await self.table.create_entity(entity)
            assert resp is not None

            entity["test3"] = 5
            entity["test5"] = datetime.utcnow()

            batch = [("update", entity, {"mode": UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            result = await self.table.get_entity(row_key=entity["RowKey"], partition_key=entity["PartitionKey"])
            assert result["PartitionKey"] == "001"
            assert result["RowKey"] == "batch_insert"
            assert result["test3"] == 5
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_update"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()
            await self.table.create_entity(entity)

            entity = await self.table.get_entity("001", "batch_update")
            assert 3 == entity["test3"]
            entity["test2"] = "value1"

            batch = [("update", entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            result = await self.table.get_entity("001", "batch_update")
            assert "value1" == result["test2"]
            assert entity["PartitionKey"] == "001"
            assert entity["RowKey"] == "batch_update"
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_merge(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_merge"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()
            await self.table.create_entity(entity)

            resp_entity = await self.table.get_entity(partition_key="001", row_key="batch_merge")
            assert 3 == entity["test3"]
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_merge"
            entity["test2"] = "value1"

            batch = [("update", entity, {"mode": UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            resp_entity = await self.table.get_entity(partition_key="001", row_key="batch_merge")
            assert entity["test2"] == resp_entity["test2"]
            assert 1234567890 == resp_entity["test4"]
            assert entity["PartitionKey"] == resp_entity["PartitionKey"]
            assert entity["RowKey"] == resp_entity["RowKey"]
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update_if_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            resp = await self.table.create_entity(entity=entity)
            etag = resp["etag"]

            # Act
            sent_entity = self._create_updated_entity_dict(entity["PartitionKey"], entity["RowKey"])
            batch = [
                (
                    "update",
                    sent_entity,
                    {"etag": etag, "match_condition": MatchConditions.IfNotModified, "mode": UpdateMode.REPLACE},
                )
            ]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert transaction_result[0]["etag"] != etag

            entity = await self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
            self._assert_updated_entity(entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_update_if_doesnt_match(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict()
            resp = await self.table.create_entity(entity)
            assert resp is not None

            # Act
            sent_entity1 = self._create_updated_entity_dict(entity["PartitionKey"], entity["RowKey"])

            batch = [
                (
                    "update",
                    sent_entity1,
                    {
                        "etag": "W/\"datetime'2012-06-15T22%3A51%3A44.9662825Z'\"",
                        "match_condition": MatchConditions.IfNotModified,
                    },
                )
            ]
            with pytest.raises(TableTransactionError) as error:
                await self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            # Assert
            received_entity = await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            self._assert_default_entity(received_entity)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_insert_replace(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_insert_replace"
            entity["test"] = True
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()

            batch = [("upsert", entity, {"mode": UpdateMode.REPLACE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = await self.table.get_entity("001", "batch_insert_replace")
            assert entity is not None
            assert "value" == entity["test2"]
            assert 1234567890 == entity["test4"]
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_insert_merge(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_insert_merge"
            entity["test"] = True
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()

            batch = [("upsert", entity, {"mode": UpdateMode.MERGE})]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = await self.table.get_entity("001", "batch_insert_merge")
            assert entity is not None
            assert "value" == entity["test2"]
            assert 1234567890 == entity["test4"]
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_delete(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_delete"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            entity["test5"] = datetime.utcnow()
            await self.table.create_entity(entity)

            entity = await self.table.get_entity(partition_key="001", row_key="batch_delete")
            assert 3 == entity["test3"]

            batch = [("delete", entity)]
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" not in transaction_result[0]

            with pytest.raises(ResourceNotFoundError):
                entity = await self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_inserts(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            entity = TableEntity()
            entity["PartitionKey"] = "batch_inserts"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)
            transaction_count = 0

            batch = []
            for i in range(100):
                entity["RowKey"] = str(i)
                batch.append(("create", entity.copy()))
                transaction_count += 1
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]

            entities = self.table.query_entities("PartitionKey eq 'batch_inserts'")

            length = 0
            async for e in entities:
                length += 1

            # Assert
            assert entities is not None
            assert 100 == length
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_all_operations_together(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
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

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]
            assert "etag" not in transaction_result[1]
            assert "etag" in transaction_result[2]
            assert "etag" in transaction_result[3]
            assert "etag" in transaction_result[4]
            assert "etag" in transaction_result[5]

            entities = self.table.query_entities("PartitionKey eq '003'")
            length = 0
            async for e in entities:
                length += 1
            assert 5 == length
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_same_row_operations_fail(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            await self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict("001", "batch_negative_1")
            batch.append(("update", entity.copy()))

            entity = self._create_random_entity_dict("001", "batch_negative_1")
            batch.append(("update", entity.copy(), {"mode": UpdateMode.REPLACE}))

            # Assert
            with pytest.raises(TableTransactionError):
                await self.table.submit_transaction(batch)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_different_partition_operations_fail(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            await self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict("001", "batch_negative_1")
            batch.append(("update", entity.copy()))

            entity = self._create_random_entity_dict("002", "batch_negative_1")
            batch.append(("update", entity.copy()))

            # Assert
            with pytest.raises(ValueError):
                await self.table.submit_transaction(batch)
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_too_many_ops(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            await self.table.create_entity(entity)

            # Act
            with pytest.raises(TableTransactionError):
                batch = []
                for i in range(0, 101):
                    entity = TableEntity()
                    entity["PartitionKey"] = "large"
                    entity["RowKey"] = "item{0}".format(i)
                    batch.append(("create", entity.copy()))
                await self.table.submit_transaction(batch)

            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_new_non_existent_table(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")

            tc = self.ts.get_table_client("doesntexist")

            batch = [("create", entity)]

            with pytest.raises(TableTransactionError):
                resp = await tc.submit_transaction(batch)
            # Assert
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_new_invalid_key(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        invalid_key = (
            tables_primary_storage_account_key.named_key.key[0:-6] + "=="
        )  # cut off a bit from the end to invalidate
        tables_primary_storage_account_key = AzureNamedKeyCredential(tables_storage_account_name, invalid_key)
        credential = AzureNamedKeyCredential(
            name=tables_storage_account_name, key=tables_primary_storage_account_key.named_key.key
        )
        self.ts = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=credential)
        self.table_name = self.get_resource_name("uttable")
        self.table = self.ts.get_table_client(self.table_name)

        entity = self._create_random_entity_dict("001", "batch_negative_1")

        batch = [("create", entity)]
        with pytest.raises(ClientAuthenticationError):
            resp = await self.table.submit_transaction(batch)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_new_delete_nonexistent_entity(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")

            batch = [("delete", entity)]
            with pytest.raises(TableTransactionError):
                resp = await self.table.submit_transaction(batch)

        finally:
            await self._tear_down()

    @pytest.mark.live_test_only
    @tables_decorator_async
    async def test_batch_sas_auth(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_storage_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True, read=True, update=True, delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )
            token = AzureSasCredential(token)

            # Act
            service = TableServiceClient(
                self.account_url(tables_storage_account_name, "table"),
                credential=token,
            )
            table = service.get_table_client(self.table_name)

            entity = TableEntity()
            entity["PartitionKey"] = "batch_inserts"
            entity["test"] = EntityProperty(True, EdmType.BOOLEAN)
            entity["test2"] = "value"
            entity["test3"] = 3
            entity["test4"] = EntityProperty(1234567890, EdmType.INT32)

            batch = []
            transaction_count = 0
            for i in range(10):
                entity["RowKey"] = str(i)
                batch.append(("create", entity.copy()))
                transaction_count += 1
            transaction_result = await table.submit_transaction(batch)

            assert transaction_result is not None

            total_entities = 0
            async for e in table.list_entities():
                total_entities += 1

            assert total_entities == transaction_count
        finally:
            await self._tear_down()

    @pytest.mark.live_test_only  # Request bodies are very large
    @tables_decorator_async
    async def test_batch_request_too_large(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:

            batch = []
            entity = {
                "PartitionKey": "pk001",
                "Foo": os.urandom(1024 * 64),
                "Bar": os.urandom(1024 * 64),
                "Baz": os.urandom(1024 * 64),
            }
            for i in range(50):
                entity["RowKey"] = str(i)
                batch.append(("create", entity.copy()))

            with pytest.raises(RequestTooLargeError):
                await self.table.submit_transaction(batch)

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_delete_batch_with_bad_kwarg(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            await self.table.create_entity(entity)

            received = await self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            good_etag = received.metadata["etag"]
            received.metadata["etag"] = "W/\"datetime'2012-06-15T22%3A51%3A44.9662825Z'\""

            batch = [("delete", received, {"match_condition": MatchConditions.IfNotModified})]

            with pytest.raises(TableTransactionError) as error:
                await self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            received.metadata["etag"] = good_etag
            batch = [("delete", received, {"match_condition": MatchConditions.IfNotModified})]
            resp = await self.table.submit_transaction(batch)

            assert resp is not None
        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_with_mode(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference("table2")
            table2 = self.ts.get_table_client(table2_name)
            await table2.create_table()

            # Act
            entity1 = {"PartitionKey": "pk001", "RowKey": "rk001", "Value": 1, "day": "Monday", "float": 1.001}
            entity2 = {"PartitionKey": "pk001", "RowKey": "rk002", "Value": 1, "day": "Monday", "float": 1.001}

            batch = [("upsert", entity1, {"mode": "merge"}), ("upsert", entity2, {"mode": "replace"})]

            resp = await self.table.submit_transaction(batch)
            assert len(resp) == 2

            with pytest.raises(ValueError):
                batch = [("upsert", entity1, {"mode": "foo"}), ("upsert", entity2, {"mode": "bar"})]
                await self.table.submit_transaction(batch)

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_batch_with_specialchar_partitionkey(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            table2_name = self._get_table_reference("table2")
            table2 = self.ts.get_table_client(table2_name)
            await table2.create_table()

            # Act
            entity1 = {"PartitionKey": "A'aaa\"_bbbb2", "RowKey": '"A\'aaa"_bbbb2', "test": '"A\'aaa"_bbbb2'}
            await self.table.submit_transaction([("create", entity1)])
            get_entity = await self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            await self.table.submit_transaction([("upsert", entity1, {"mode": "merge"})])
            get_entity = await self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            await self.table.submit_transaction([("upsert", entity1, {"mode": "replace"})])
            get_entity = await self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            await self.table.submit_transaction([("update", entity1, {"mode": "merge"})])
            get_entity = await self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            await self.table.submit_transaction([("update", entity1, {"mode": "replace"})])
            get_entity = await self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            entity_results = self.table.list_entities()
            async for entity in entity_results:
                assert entity == entity1
                get_entity = await self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
                assert get_entity == entity1

            await self.table.submit_transaction([("delete", entity1)])

        finally:
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_async_batch_inserts(self, tables_storage_account_name, tables_primary_storage_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key)
        try:
            # Act
            transaction_count = 10

            async def generate_entities(count):
                for i in range(count):
                    yield ("upsert", {"PartitionKey": "async_inserts", "RowKey": str(i)})

            batch = generate_entities(transaction_count)
            transaction_result = await self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]

            entities = self.table.query_entities("PartitionKey eq 'async_inserts'")
            entities = [e async for e in entities]

            # Assert
            assert len(entities) == transaction_count
        finally:
            await self._tear_down()

    # Playback doesn't work as test proxy issue: https://github.com/Azure/azure-sdk-tools/issues/2900
    @pytest.mark.live_test_only
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_empty_batch(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        async with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            await client.create_table()
            result = await client.submit_transaction([])
            assert result == []
            await client.delete_table()

    # Playback doesn't work as test proxy issue: https://github.com/Azure/azure-sdk-tools/issues/2900
    @pytest.mark.live_test_only
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_client_with_url_ends_with_table_name(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        entity = {"PartitionKey": "test-partition", "RowKey": "test-key", "name": "test-name"}

        valid_tc = TableClient(url, table_name, credential=tables_primary_storage_account_key)
        await valid_tc.create_table()

        tc = TableClient(invalid_url, table_name, credential=tables_primary_storage_account_key)
        with pytest.raises(HttpResponseError) as ex:
            await tc.submit_transaction([("upsert", entity)])
        assert "None of the provided media types are supported" in str(ex.value)
        assert ex.value.error_code == "MediaTypeNotSupported"
        assert ex.value.status_code == 415

        await valid_tc.delete_table()
        await valid_tc.close()
        await tc.close()


class RequestCorrect(Exception):
    pass


class CheckBatchURL(AsyncHTTPPolicy):
    def __init__(self, account_url, table_name):
        if not account_url.startswith("http"):
            account_url = "https://" + account_url
        self.url = account_url
        self.table = table_name
        super().__init__()

    async def send(self, request):
        assert request.http_request.url == self.url + "/$batch"
        payload = request.http_request.body
        for line in payload.split(b"\r\n\r\n"):
            if line.startswith(b"PATCH") or line.startswith(b"POST"):
                assert line[line.index(b" ") + 1 :].decode().startswith(self.url + "/" + self.table)
                raise RequestCorrect()
        raise AssertionError("No matching PATCH/POST requests found in batch:\n{}".format(payload.decode()))


class TestBatchUnitTestsAsync(AsyncTableTestCase):
    tables_storage_account_name = "fake_storage_account"
    tables_sas_credential = "fake_sas_credential"
    tables_primary_storage_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA=="
    credential = AzureSasCredential(tables_sas_credential)
    entity1 = {"PartitionKey": "pk001", "RowKey": "rk001"}
    entity2 = {"PartitionKey": "pk001", "RowKey": "rk002"}
    batch = [("upsert", entity1), ("upsert", entity2)]

    @pytest.mark.asyncio
    async def test_batch_url_http(self):
        url = self.account_url(self.tables_storage_account_name, "table").replace("https", "http")
        table = TableClient(
            url, "batchtablename", credential=self.credential, per_call_policies=[CheckBatchURL(url, "batchtablename")]
        )

        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_https(self):
        table = TableClient(
            self.account_url(self.tables_storage_account_name, "table"),
            "batchtablename",
            credential=self.credential,
            per_call_policies=[
                CheckBatchURL(self.account_url(self.tables_storage_account_name, "table"), "batchtablename")
            ],
        )

        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_connection_string_key(self):
        conn_string = "AccountName={};AccountKey={};".format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key
        )
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[
                CheckBatchURL("https://{}.table.{}".format(self.tables_storage_account_name, endpoint_suffix), "foo")
            ],
        )
        assert table.scheme == "https"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_connection_string_sas(self):
        token = AzureSasCredential(self.generate_sas_token())
        conn_string = "AccountName={};SharedAccessSignature={};".format(
            self.tables_storage_account_name, token.signature
        )
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[
                CheckBatchURL("https://{}.table.{}".format(self.tables_storage_account_name, endpoint_suffix), "foo")
            ],
        )

        assert table.account_name == self.tables_storage_account_name
        assert table.url.startswith("https://" + self.tables_storage_account_name + ".table." + endpoint_suffix)
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_connection_string_custom_domain(self):
        conn_string = "AccountName={};AccountKey={};TableEndpoint=www.mydomain.com;".format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key
        )

        table = TableClient.from_connection_string(
            conn_string, table_name="foo", per_call_policies=[CheckBatchURL("https://www.mydomain.com", "foo")]
        )
        assert table.url.startswith("https://www.mydomain.com")
        assert table.scheme == "https"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

        conn_string = "AccountName={};AccountKey={};TableEndpoint=http://www.mydomain.com;".format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key
        )

        table = TableClient.from_connection_string(
            conn_string, table_name="foo", per_call_policies=[CheckBatchURL("http://www.mydomain.com", "foo")]
        )
        assert table.url.startswith("http://www.mydomain.com")
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_custom_account_endpoint_path(self):
        token = AzureSasCredential(self.generate_sas_token())
        custom_account_url = "http://local-machine:11002/custom/account/path/" + token.signature
        conn_string = "DefaultEndpointsProtocol=http;AccountName={};AccountKey={};TableEndpoint={};".format(
            self.tables_storage_account_name, self.tables_primary_storage_account_key, custom_account_url
        )
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")],
        )
        assert table.account_name == self.tables_storage_account_name
        assert table._primary_hostname == "local-machine:11002/custom/account/path"
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

        table = TableClient(
            endpoint=custom_account_url,
            table_name="foo",
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")],
        )
        assert table.account_name == "custom"
        assert table.table_name == "foo"
        assert table.credential == None
        assert table.url.startswith("http://local-machine:11002/custom/account/path")
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

        table = TableClient.from_table_url(
            "http://local-machine:11002/custom/account/path/foo" + token.signature,
            per_call_policies=[CheckBatchURL("http://local-machine:11002/custom/account/path", "foo")],
        )
        assert table.account_name == "custom"
        assert table.table_name == "foo"
        assert table.credential == None
        assert table.url.startswith("http://local-machine:11002/custom/account/path")
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_complete_table_url(self):
        table_url = self.account_url(self.tables_storage_account_name, "table") + "/foo"
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        table = TableClient(
            table_url,
            table_name="bar",
            credential=self.credential,
            per_call_policies=[
                CheckBatchURL(
                    "https://{}.table.{}/foo".format(self.tables_storage_account_name, endpoint_suffix), "bar"
                )
            ],
        )

        assert table.scheme == "https"
        assert table.table_name == "bar"
        assert table.account_name == self.tables_storage_account_name
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_with_complete_url(self):
        # Arrange
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
        table_url = "https://{}.table.{}:443/foo".format(self.tables_storage_account_name, endpoint_suffix)
        table = TableClient(
            endpoint=table_url,
            table_name="bar",
            credential=self.credential,
            per_call_policies=[
                CheckBatchURL(
                    "https://{}.table.{}:443/foo".format(self.tables_storage_account_name, endpoint_suffix), "bar"
                )
            ],
        )

        # Assert
        assert table.scheme == "https"
        assert table.table_name == "bar"
        assert table.account_name == self.tables_storage_account_name
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_batch_url_for_cosmos_emulator(self):
        emulator_credential = AzureNamedKeyCredential("localhost", self.tables_primary_storage_account_key)
        emulator_connstr = "DefaultEndpointsProtocol=http;AccountName=localhost;AccountKey={};TableEndpoint=http://localhost:8902/;".format(
            self.tables_primary_storage_account_key
        )

        table = TableClient.from_connection_string(
            emulator_connstr, "tablename", per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")]
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table._cosmos_endpoint
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

        table = TableClient(
            "http://localhost:8902/",
            "tablename",
            credential=emulator_credential,
            per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")],
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table._cosmos_endpoint
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

        table = TableClient.from_table_url(
            "http://localhost:8902/Tables('tablename')",
            credential=emulator_credential,
            per_call_policies=[CheckBatchURL("http://localhost:8902", "tablename")],
        )
        assert table.url == "http://localhost:8902"
        assert table.account_name == "localhost"
        assert table.table_name == "tablename"
        assert table._cosmos_endpoint
        assert table.scheme == "http"
        with pytest.raises(RequestCorrect):
            await table.submit_transaction(self.batch)

    @pytest.mark.asyncio
    async def test_decode_string_body(self):
        async def patch_run(request, **kwargs) -> PipelineResponse:
            aiohttp_response = Mock()
            aiohttp_response.status = 405
            aiohttp_response.reason = "Method Not Allowed"
            aiohttp_response.headers = {"x-ms-error-code": "UnsupportedHttpVerb", "content-type": "text/html"}
            core_response = RestAioHttpTransportResponse(
                request=request, internal_response=aiohttp_response, decompress=False
            )
            core_response._content = b"<!DOCTYPE html><html><head><title>UnsupportedHttpVerb</title></head><body><h1>The resource doesn't support specified Http Verb.</h1><p><ul><li>HttpStatusCode: 405</li><li>ErrorCode: UnsupportedHttpVerb</li><li>RequestId : 98adf858-a01e-0071-2580-bfe811000000</li><li>TimeStamp : 2023-07-26T05:19:26.9825582Z</li></ul></p></body></html>"
            return PipelineResponse(
                http_request=request,
                http_response=core_response,
                context={},
            )

        client = TableClient(
            endpoint=self.account_url(self.tables_storage_account_name, "table"),
            credential=DefaultAzureCredential(
                name=self.tables_storage_account_name, key=self.tables_primary_storage_account_key
            ),
            table_name="syncenabled",
        )
        client._client._client._pipeline.run = partial(patch_run)
        with pytest.raises(HttpResponseError) as ex:
            await client.submit_transaction(
                [
                    (
                        "upsert",
                        {
                            "PartitionKey": "test-partition",
                            "RowKey": "test-key",
                            "name": "test-name",
                        },
                    )
                ]
            )
        assert ex.value.status_code == 405
        assert ex.value.error_code == "UnsupportedHttpVerb"
