# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_paging_with_continuation_token`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source at ``tests/test_query.py`` so test IDs differ only by path.

Run with::

    pytest --noconftest tests/query_items/sync/legacy/test_query.py -v
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
class TestQuery(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_query_paging_" + uuid.uuid4().hex[:8]
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

    def test_paging_with_continuation_token(self):
        # Source: tests/test_query.py::TestQuery.test_paging_with_continuation_token
        self.container.create_item({"pk": "pk", "id": "1"})
        self.container.create_item({"pk": "pk", "id": "2"})

        query_iterable = self.container.query_items(
            query="SELECT * from c",
            partition_key="pk",
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        pager.next()
        token = pager.continuation_token
        second_page = list(pager.next())[0]

        replay_pager = query_iterable.by_page(token)
        replay_second_page = list(replay_pager.next())[0]
        self.assertEqual(second_page["id"], replay_second_page["id"])

