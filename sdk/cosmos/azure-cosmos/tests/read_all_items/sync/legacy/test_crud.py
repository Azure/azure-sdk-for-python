# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_query_iterable_functionality`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source at ``tests/test_crud.py`` so test IDs differ only by path.

Run with::

    pytest --noconftest tests/read_all_items/sync/legacy/test_crud.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_read_all_crud_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.container = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def test_query_iterable_functionality(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_query_iterable_functionality
        # End-to-end on the real Rust driver: read_all_items takes no partition key,
        # so this is a whole-container read served through the Rust query fast path.
        # If it were routed to a native read-feed the driver would reject it and this
        # would error -- which is why running it against a real account matters.
        doc1 = self.container.create_item(body={"id": "doc1", "prop1": "value1", "pk": "pk"})
        doc2 = self.container.create_item(body={"id": "doc2", "prop1": "value2", "pk": "pk"})
        doc3 = self.container.create_item(body={"id": "doc3", "prop1": "value3", "pk": "pk"})
        resources = {
            "coll": self.container,
            "doc1": doc1,
            "doc2": doc2,
            "doc3": doc3,
        }

        results = resources["coll"].read_all_items(max_item_count=2)
        docs = list(iter(results))
        self.assertEqual(3, len(docs))
        self.assertEqual(resources["doc1"]["id"], docs[0]["id"])
        self.assertEqual(resources["doc2"]["id"], docs[1]["id"])
        self.assertEqual(resources["doc3"]["id"], docs[2]["id"])

        results = resources["coll"].read_all_items(max_item_count=2)
        counter = 0
        for doc in iter(results):
            counter += 1
            if counter == 1:
                self.assertEqual(resources["doc1"]["id"], doc["id"])
            elif counter == 2:
                self.assertEqual(resources["doc2"]["id"], doc["id"])
            elif counter == 3:
                self.assertEqual(resources["doc3"]["id"], doc["id"])
        self.assertEqual(counter, 3)

        results = resources["coll"].read_all_items(max_item_count=2)
        page_iter = results.by_page()
        first_block = list(next(page_iter))
        self.assertEqual(2, len(first_block))
        self.assertEqual(resources["doc1"]["id"], first_block[0]["id"])
        self.assertEqual(resources["doc2"]["id"], first_block[1]["id"])
        self.assertEqual(1, len(list(next(page_iter))))
        with self.assertRaises(StopIteration):
            next(page_iter)

