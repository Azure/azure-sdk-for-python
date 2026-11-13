# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original read-all assertions on isolated Rust-backed resources."""

import unittest
import uuid

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.http_constants import StatusCodes
from config.settings import TestSettings


class _OwnedReadAllTests(unittest.TestCase):
    no_response_on_write = False

    def setUp(self):
        self.client = CosmosClient(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            no_response_on_write=self.no_response_on_write,
        )
        self.addCleanup(self.client.close)
        self.database = self.client.create_database(
            "read-all-original-" + uuid.uuid4().hex
        )
        self.addCleanup(self.client.delete_database, self.database.id)
        self.key_databaseForTest = self.database

    def _create_container_for_test(self, container_id, partition_key):
        return self.database.create_container(container_id, partition_key=partition_key)

    def _delete_container_for_test(self, container_id):
        self.database.delete_container(container_id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeaders(_OwnedReadAllTests):

    def test_read_all_items_response_headers_rust(self):
        """read_all_items pagers expose the same headers contract as queries."""
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_read_all_items_response_headers
        container_id = "test_headers_readall_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id, PartitionKey(path="/pk")
        )
        try:
            for i in range(8):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            paged = created_collection.read_all_items(max_item_count=3)
            items = list(paged)
            self.assertEqual(len(items), 8)

            self.assertTrue(
                hasattr(paged, "get_response_headers"),
                "read_all_items pager must expose get_response_headers",
            )
            headers = paged.get_response_headers()
            self.assertIsInstance(headers, CaseInsensitiveDict)
            self.assertIn("x-ms-request-charge", headers)
        finally:
            self._delete_container_for_test(container_id)


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(_OwnedReadAllTests):
    no_response_on_write = True

    def test_query_iterable_functionality_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_query_iterable_functionality
        collection = self.key_databaseForTest.create_container(
            "query-iterable-container", partition_key=PartitionKey("/pk")
        )

        doc1 = collection.create_item(
            body={"id": "doc1", "prop1": "value1", "pk": "pk"}, no_response=False
        )
        doc2 = collection.create_item(
            body={"id": "doc2", "prop1": "value2", "pk": "pk"}, no_response=False
        )
        doc3 = collection.create_item(
            body={"id": "doc3", "prop1": "value3", "pk": "pk"}, no_response=False
        )
        resources = {"coll": collection, "doc1": doc1, "doc2": doc2, "doc3": doc3}

        results = resources["coll"].read_all_items(max_item_count=2)
        docs = list(iter(results))
        self.assertEqual(
            3,
            len(docs),
            "QueryIterable should return all documents" + " using continuation",
        )
        self.assertEqual(resources["doc1"]["id"], docs[0]["id"])
        self.assertEqual(resources["doc2"]["id"], docs[1]["id"])
        self.assertEqual(resources["doc3"]["id"], docs[2]["id"])

        # Validate QueryIterable iterator with 'for'.
        results = resources["coll"].read_all_items(max_item_count=2)
        counter = 0
        # test QueryIterable with 'for'.
        for doc in iter(results):
            counter += 1
            if counter == 1:
                self.assertEqual(
                    resources["doc1"]["id"], doc["id"], "first document should be doc1"
                )
            elif counter == 2:
                self.assertEqual(
                    resources["doc2"]["id"], doc["id"], "second document should be doc2"
                )
            elif counter == 3:
                self.assertEqual(
                    resources["doc3"]["id"], doc["id"], "third document should be doc3"
                )
        self.assertEqual(counter, 3)

        # Get query results page by page.
        results = resources["coll"].read_all_items(max_item_count=2)

        page_iter = results.by_page()
        first_block = list(next(page_iter))
        self.assertEqual(2, len(first_block), "First block should have 2 entries.")
        self.assertEqual(resources["doc1"]["id"], first_block[0]["id"])
        self.assertEqual(resources["doc2"]["id"], first_block[1]["id"])
        self.assertEqual(
            1, len(list(next(page_iter))), "Second block should have 1 entry."
        )
        with self.assertRaises(StopIteration):
            next(page_iter)

        self.key_databaseForTest.delete_container(collection.id)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestTransactionalBatch(_OwnedReadAllTests):

    def test_batch_delete_rust(self):
        # Source: tests/test_transactional_batch.py::TestTransactionalBatch.test_batch_delete
        container = self._create_container_for_test(
            "batch_delete" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/company"),
        )
        create_batch = []
        delete_batch = []
        for i in range(10):
            item_id = str(uuid.uuid4())
            create_batch.append(("create", ({"id": item_id, "company": "Microsoft"},)))
            delete_batch.append(("delete", (item_id,)))

        batch_response = container.execute_item_batch(
            batch_operations=create_batch, partition_key="Microsoft"
        )
        assert len(batch_response) == 10
        assert len(list(container.read_all_items())) == 10

        batch_response = container.execute_item_batch(
            batch_operations=delete_batch, partition_key="Microsoft"
        )
        assert len(batch_response) == 10
        assert len(list(container.read_all_items())) == 0

        # delete non-existent item
        batch = [("delete", ("new-item",)), ("delete", ("new-item",))]

        try:
            container.execute_item_batch(
                batch_operations=batch, partition_key="Microsoft"
            )
            self.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.NOT_FOUND
            assert e.error_index == 0
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.NOT_FOUND
            assert (
                operation_results[1].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            )

        self._delete_container_for_test(container.id)
