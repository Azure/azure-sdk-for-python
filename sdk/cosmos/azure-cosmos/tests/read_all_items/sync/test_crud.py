# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_query_iterable_functionality`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source (apart from the method's ``_rust`` suffix) at ``tests/test_crud.py`` so test IDs
differ by path and method suffix.

Run with::

    pytest --noconftest tests/read_all_items/sync/test_crud.py -v
"""
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(unittest.TestCase):

    def setUp(self) -> None:
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original.
        self.key_client = create_setup_client(_backend="rust", timeout=30)
        self.client = create_data_client(_backend="rust", timeout=30)
        self._db_id = "rust_read_all_crud_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = self.key_client.create_database(self._db_id)
        key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(
            self._db_id
        ).get_container_client(self._container_id)

    def tearDown(self) -> None:
        try:
            self.key_client.delete_database(self._db_id)
        finally:
            self.client.close()
            self.key_client.close()

    def test_query_iterable_functionality_rust(self):
        """Enumerating a whole container works item by item and page by page.

        Three items are created, then read back three ways with a page size of
        two: as a flat iterator, as a manually counted loop, and page by page.

        All three must see the same three items in the same order. Paging must
        split them 2 then 1 and then stop cleanly, which proves the page size
        is honoured and the end of the feed is signalled properly rather than
        looping or repeating the last page.

        This runs against a real account because read_all_items takes no
        partition key, so it is a whole-container read served through a live
        Rust read-many cursor. No continuation token is required between pages.
        """
        # Source: tests/test_crud.py::TestCRUDOperations.test_query_iterable_functionality
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
