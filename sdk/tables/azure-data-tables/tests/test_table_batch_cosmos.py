# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
import os
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, set_custom_default_matcher

from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.data.tables import (
    EdmType,
    EntityProperty,
    TableTransactionError,
    TableEntity,
    UpdateMode,
    TransactionOperation,
    RequestTooLargeError,
    TableSasPermissions,
    TableServiceClient,
    generate_table_sas,
    TableErrorCode,
    TableClient,
)
from azure.data.tables._constants import DEFAULT_COSMOS_ENDPOINT_SUFFIX

from test_table_batch import CheckBatchURL, RequestCorrect
from _shared.testcase import TableTestCase
from preparers import cosmos_decorator


class TestTableBatchCosmos(AzureRecordedTestCase, TableTestCase):
    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_insert(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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

            batch = [("upsert", entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = self.table.get_entity("001", "batch_insert_replace")
            assert entity is not None
            assert "value" == entity["test2"]
            assert 1234567890 == entity["test4"]
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_update(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            self.table.create_entity(entity)

            entity = self.table.get_entity("001", "batch_update")
            assert 3 == entity["test3"]
            entity["test2"] = "value1"

            batch = [("update", entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            result = self.table.get_entity("001", "batch_update")
            assert "value1" == result["test2"]
            assert entity["PartitionKey"] == "001"
            assert entity["RowKey"] == "batch_update"
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_merge(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            self.table.create_entity(entity)

            resp_entity = self.table.get_entity(partition_key="001", row_key="batch_merge")
            assert 3 == entity["test3"]
            entity = TableEntity()
            entity["PartitionKey"] = "001"
            entity["RowKey"] = "batch_merge"
            entity["test2"] = "value1"

            batch = [("update", entity, {"mode": UpdateMode.MERGE})]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            resp_entity = self.table.get_entity(partition_key="001", row_key="batch_merge")
            assert entity["test2"] == resp_entity["test2"]
            assert 1234567890 == resp_entity["test4"]
            assert entity["PartitionKey"] == resp_entity["PartitionKey"]
            assert entity["RowKey"] == resp_entity["RowKey"]
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_update_if_match(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict()
            resp = self.table.create_entity(entity=entity)
            etag = resp["etag"]

            # Act
            sent_entity = self._create_updated_entity_dict(entity["PartitionKey"], entity["RowKey"])
            batch = [
                (
                    "update",
                    sent_entity,
                    {
                        "mode": UpdateMode.REPLACE,
                        "etag": etag,
                        "match_condition": MatchConditions.IfNotModified,
                        "mode": UpdateMode.REPLACE,
                    },
                )
            ]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
            self._assert_updated_entity(entity)
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_update_if_doesnt_match(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict()
            self.table.create_entity(entity)

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
                self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            # Assert
            received_entity = self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            self._assert_default_entity(received_entity)
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_insert_replace(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = self.table.get_entity("001", "batch_insert_replace")
            assert entity is not None
            assert "value" == entity["test2"]
            assert 1234567890 == entity["test4"]
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_insert_merge(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" in transaction_result[0]

            entity = self.table.get_entity("001", "batch_insert_merge")
            assert entity is not None
            assert "value" == entity["test2"]
            assert 1234567890 == entity["test4"]
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_delete(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            self.table.create_entity(entity)

            entity = self.table.get_entity(partition_key="001", row_key="batch_delete")
            assert 3 == entity["test3"]

            batch = [("delete", entity)]
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, 1)
            assert "etag" not in transaction_result[0]

            with pytest.raises(ResourceNotFoundError):
                entity = self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_inserts(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]

            entities = list(self.table.query_entities("PartitionKey eq 'batch_inserts'"))

            # Assert
            assert entities is not None
            assert transaction_count == len(entities)
            e = self.table.get_entity("batch_inserts", "1")
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_all_operations_together(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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

            self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-2"
            self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-3"
            self.table.create_entity(entity)
            entity["RowKey"] = "batch_all_operations_together-4"
            self.table.create_entity(entity)
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

            transaction_result = self.table.submit_transaction(batch)

            # Assert
            self._assert_valid_batch_transaction(transaction_result, transaction_count)
            assert "etag" in transaction_result[0]
            assert "etag" not in transaction_result[1]
            assert "etag" in transaction_result[2]
            assert "etag" in transaction_result[3]
            assert "etag" in transaction_result[4]
            assert "etag" in transaction_result[5]

            # Assert
            entities = list(self.table.query_entities("PartitionKey eq '003'"))
            assert 5 == len(entities)
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_different_partition_operations_fail(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            self.table.create_entity(entity)

            # Act
            batch = []

            entity = self._create_updated_entity_dict("001", "batch_negative_1")
            batch.append(("update", entity.copy()))

            entity = self._create_random_entity_dict("002", "batch_negative_1")
            batch.append(("update", entity.copy()))

            with pytest.raises(ValueError):
                self.table.submit_transaction(batch)
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_new_non_existent_table(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")

            tc = self.ts.get_table_client("doesntexist")

            batch = [("create", entity)]

            with pytest.raises(TableTransactionError):
                resp = tc.submit_transaction(batch)
            # Assert
        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_new_delete_nonexistent_entity(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")

            batch = [("delete", entity)]
            with pytest.raises(TableTransactionError):
                resp = self.table.submit_transaction(batch)

        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_delete_batch_with_bad_kwarg(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            entity = self._create_random_entity_dict("001", "batch_negative_1")
            self.table.create_entity(entity)

            received = self.table.get_entity(entity["PartitionKey"], entity["RowKey"])
            good_etag = received.metadata["etag"]
            received.metadata["etag"] = "W/\"datetime'2012-06-15T22%3A51%3A44.9662825Z'\""

            batch = [("delete", received, {"match_condition": MatchConditions.IfNotModified})]

            with pytest.raises(TableTransactionError) as error:
                self.table.submit_transaction(batch)
            assert error.value.status_code == 412
            assert error.value.error_code == TableErrorCode.update_condition_not_satisfied

            received.metadata["etag"] = good_etag
            batch = [("delete", received, {"match_condition": MatchConditions.IfNotModified})]
            resp = self.table.submit_transaction(batch)

            assert resp is not None
        finally:
            self._tear_down()

    @pytest.mark.live_test_only
    @cosmos_decorator
    def test_batch_sas_auth(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            token = self.generate_sas(
                generate_table_sas,
                tables_primary_cosmos_account_key,
                self.table_name,
                permission=TableSasPermissions(add=True, read=True, update=True, delete=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )
            token = AzureSasCredential(token)

            # Act
            service = TableServiceClient(
                self.account_url(tables_cosmos_account_name, "cosmos"),
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
            transaction_result = table.submit_transaction(batch)

            assert transaction_result

            total_entities = 0
            for e in table.list_entities():
                total_entities += 1

            assert total_entities == transaction_count
        finally:
            self._tear_down()

    @pytest.mark.live_test_only  # Request bodies are very large
    @cosmos_decorator
    def test_batch_request_too_large(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
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
                self.table.submit_transaction(batch)

        finally:
            self._tear_down()

    @cosmos_decorator
    @recorded_by_proxy
    def test_batch_with_specialchar_partitionkey(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )

        # Arrange
        self._set_up(tables_cosmos_account_name, tables_primary_cosmos_account_key, url="cosmos")
        try:
            table2_name = self._get_table_reference("table2")
            table2 = self.ts.get_table_client(table2_name)
            table2.create_table()

            # Act
            entity1 = {"PartitionKey": "A'aaa\"_bbbb2", "RowKey": '"A\'aaa"_bbbb2', "test": '"A\'aaa"_bbbb2'}
            self.table.submit_transaction([("create", entity1)])
            get_entity = self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            self.table.submit_transaction([("upsert", entity1, {"mode": "merge"})])
            get_entity = self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            self.table.submit_transaction([("upsert", entity1, {"mode": "replace"})])
            get_entity = self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            self.table.submit_transaction([("update", entity1, {"mode": "merge"})])
            get_entity = self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            self.table.submit_transaction([("update", entity1, {"mode": "replace"})])
            get_entity = self.table.get_entity(partition_key=entity1["PartitionKey"], row_key=entity1["RowKey"])
            assert get_entity == entity1

            entity_results = list(self.table.list_entities())
            assert entity_results[0] == entity1
            for entity in entity_results:
                get_entity = self.table.get_entity(partition_key=entity["PartitionKey"], row_key=entity["RowKey"])
                assert get_entity == entity1

            self.table.submit_transaction([("delete", entity1)])

        finally:
            self._tear_down()

    # Playback doesn't work as test proxy issue: https://github.com/Azure/azure-sdk-tools/issues/2900
    @pytest.mark.live_test_only
    @cosmos_decorator
    @recorded_by_proxy
    def test_empty_batch(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        with TableClient(url, table_name, credential=tables_primary_cosmos_account_key) as client:
            # client.create_table()
            result = client.submit_transaction([])
            assert result == []
            client.delete_table()

    # Playback doesn't work as test proxy issue: https://github.com/Azure/azure-sdk-tools/issues/2900
    @pytest.mark.live_test_only
    @cosmos_decorator
    @recorded_by_proxy
    def test_client_with_url_ends_with_table_name(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        url = self.account_url(tables_cosmos_account_name, "cosmos")
        table_name = self.get_resource_name("mytable")
        invalid_url = url + "/" + table_name
        entity = {"PartitionKey": "test-partition", "RowKey": "test-key", "name": "test-name"}

        valid_tc = TableClient(url, table_name, credential=tables_primary_cosmos_account_key)
        valid_tc.create_table()

        tc = TableClient(invalid_url, table_name, credential=tables_primary_cosmos_account_key)
        with pytest.raises(HttpResponseError) as ex:
            tc.submit_transaction([("upsert", entity)])
        assert "Request url is invalid" in str(ex.value)
        assert ex.value.error_code == "InvalidInput"
        assert ex.value.status_code == 400

        valid_tc.delete_table()


class TestBatchCosmosUnitTests(TableTestCase):
    tables_cosmos_account_name = "fake_cosmos_account"
    tables_primary_cosmos_account_key = "fakeXMZjnGsZGvd4bVr3Il5SeHA=="
    entity1 = {"PartitionKey": "pk001", "RowKey": "rk001"}
    entity2 = {"PartitionKey": "pk001", "RowKey": "rk002"}
    batch = [("upsert", entity1), ("upsert", entity2)]

    def test_batch_url_with_connection_string(self):
        endpoint_suffix = os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
        conn_string = "DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};TableEndpoint=https://{0}.table.{2}:443/;".format(
            self.tables_cosmos_account_name, self.tables_primary_cosmos_account_key, endpoint_suffix
        )
        table = TableClient.from_connection_string(
            conn_string,
            table_name="foo",
            endpoint_type="cosmos",
            per_call_policies=[
                CheckBatchURL("https://{}.table.{}:443".format(self.tables_cosmos_account_name, endpoint_suffix), "foo")
            ],
        )
        assert table.account_name == self.tables_cosmos_account_name
        assert table.url.startswith("https://" + self.tables_cosmos_account_name + ".table." + endpoint_suffix)
        assert table.scheme == "https"
        with pytest.raises(RequestCorrect):
            table.submit_transaction(self.batch)
