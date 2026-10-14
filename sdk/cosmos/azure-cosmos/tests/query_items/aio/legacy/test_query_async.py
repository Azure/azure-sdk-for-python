# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied async paging, OFFSET LIMIT, DISTINCT, and COUNT tests against Rust.

Self-contained: builds its own database + container in ``asyncSetUp``
and registers cleanup immediately. Class and method names match
``tests/test_query_async.py``. OFFSET LIMIT helpers are copied from
``tests/test_config.py`` rather than importing the legacy configuration.

Run with::

    pytest --noconftest tests/query_items/aio/legacy/test_query_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, http_constants
from azure.cosmos.aio import CosmosClient
from query_items._legacy_distinct_helpers import DistinctConfig


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


class _QueryConfig(DistinctConfig):
    @classmethod
    async def _validate_distinct_offset_limit(cls, created_collection, query, results):
        # Source helper: tests/test_config.py::TestConfig._validate_distinct_offset_limit
        query_iterable = created_collection.query_items(query=query)
        assert list(map(lambda doc: doc['value'], [item async for item in query_iterable])) == results

    @classmethod
    async def _validate_offset_limit(cls, created_collection, query, results):
        # Source helper: tests/test_config.py::TestConfig._validate_offset_limit
        query_iterable = created_collection.query_items(query=query)
        assert list(map(lambda doc: doc['pk'], [item async for item in query_iterable])) == results


@pytest.mark.cosmosEmulator
class TestQueryAsync(unittest.IsolatedAsyncioTestCase):
    config = _QueryConfig

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self._db_id = "legacy_query_paging_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.addAsyncCleanup(self._delete_owned_database)
        print(f"\nOwned async query database: {self._db_id}")
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def _delete_owned_database(self):
        await self.client.delete_database(self._db_id)
        print(f"\nDeleted owned async query database: {self._db_id}")

    async def test_offset_limit_async(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_offset_limit_async
        container_id = self._container_id
        created_collection = self.container
        values = []
        for i in range(10):
            document_definition = {'pk': i, 'id': 'myId' + str(uuid.uuid4()), 'value': i // 3}
            current_document = await created_collection.create_item(body=document_definition)
            values.append(current_document['pk'])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 0 LIMIT 2',
            results=[0, 1])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 2 LIMIT 2',
            results=[2, 3])

        await self.config._validate_distinct_offset_limit(
            created_collection=created_collection,
            query='SELECT DISTINCT c["value"] from c ORDER BY c.pk OFFSET 4 LIMIT 3',
            results=[])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 0 LIMIT 5',
                                                 results=values[:5])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 5 LIMIT 10',
                                                 results=values[5:])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 10 LIMIT 5',
                                                 results=[])

        await self.config._validate_offset_limit(created_collection=created_collection,
                                                 query='SELECT * from c ORDER BY c.pk OFFSET 100 LIMIT 1',
                                                 results=[])

        await self.database.delete_container(container_id)

    async def test_distinct_async(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_distinct_async
        distinct_field = 'distinct_field'
        pk_field = "pk"
        different_field = "different_field"

        container_id = 'collection with composite index ' + str(uuid.uuid4())
        created_collection = await self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            indexing_policy={
                "compositeIndexes": [
                    [{"path": "/" + pk_field, "order": "ascending"},
                     {"path": "/" + distinct_field, "order": "ascending"}],
                    [{"path": "/" + distinct_field, "order": "ascending"},
                     {"path": "/" + pk_field, "order": "ascending"}]
                ]
            }
        )
        documents = []
        for i in range(5):
            j = i
            while j > i - 5:
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(await created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4()), distinct_field: j}
                documents.append(await created_collection.create_item(body=document_definition))
                document_definition = {pk_field: i, 'id': str(uuid.uuid4())}
                documents.append(await created_collection.create_item(body=document_definition))
                j -= 1

        padded_docs = self.config._pad_with_none(documents, distinct_field)

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s from c' % distinct_field,  # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None, False),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s, c.%s from c' % (distinct_field, pk_field),
                                             # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, pk_field, False),
                                             is_select=True,
                                             fields=[distinct_field, pk_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct value c.%s from c' % distinct_field,  # nosec
                                             results=self.config._get_distinct_docs(padded_docs, distinct_field, None, True),
                                             is_select=True,
                                             fields=[distinct_field])

        await self.config._validate_distinct(created_collection=created_collection,
                                             query='SELECT distinct c.%s from c' % different_field,  # nosec
                                             results=['None'],
                                             is_select=True,
                                             fields=[different_field])

        await self.database.delete_container(container_id)

    async def test_partition_scoped_count_is_index_only_async(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_partition_scoped_count_is_index_only_async
        created_collection = self.container
        partition_key = "PowerCut-" + str(uuid.uuid4())
        other_partition_key = "Other-" + str(uuid.uuid4())
        created_items = []
        try:
            for i in range(25):
                item = await created_collection.create_item({
                    "id": f"power-cut-{i}-{uuid.uuid4()}",
                    "pk": partition_key,
                    "value": i,
                })
                created_items.append((item["id"], item["pk"]))
            item = await created_collection.create_item({
                "id": "other-document-type-" + str(uuid.uuid4()),
                "pk": other_partition_key,
            })
            created_items.append((item["id"], item["pk"]))

            query_iterable = created_collection.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key=partition_key,
                populate_query_metrics=True,
            )
            pager = query_iterable.by_page()
            pages = []
            async for page in pager:
                pages.append([item async for item in page])

            assert pages == [[25]]
            assert pager.continuation_token is None

            response_headers = query_iterable.get_response_headers()
            metrics_header = response_headers[http_constants.HttpHeaders.QueryMetrics]
            metrics = dict(
                entry.split("=", 1)
                for entry in metrics_header.split(";")
                if entry
            )
            assert int(metrics["retrievedDocumentCount"]) == 0
            assert int(metrics["retrievedDocumentSize"]) == 0
            assert float(metrics["indexUtilizationRatio"]) == 1.0
            assert float(response_headers[http_constants.HttpHeaders.RequestCharge]) < 20.0
        finally:
            for item_id, item_partition_key in created_items:
                await created_collection.delete_item(item_id, item_partition_key)

    async def test_paging_with_continuation_token_async(self):
        """A continuation token replays the page that follows it.

        Two items are queried one page at a time. After taking the first page,
        the token is saved and the second page is read normally. A fresh page
        iterator resumed from that token must then return the same second page.

        This is the promise behind every saved token: a customer who stores one
        and comes back later gets the next page, not a repeat of what they
        already have and not a gap. Run against a real account so the token is
        a genuine one from the service rather than a fake.
        """
        # Source: tests/test_query_async.py::TestQueryAsync.test_paging_with_continuation_token_async
        await self.container.upsert_item({"pk": "pk", "id": "1"})
        await self.container.upsert_item({"pk": "pk", "id": "2"})

        query_iterable = self.container.query_items(
            query="SELECT * from c",
            partition_key="pk",
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        replay_pager = query_iterable.by_page(token)
        replay_second_page = [item async for item in await replay_pager.__anext__()][0]
        assert second_page["id"] == replay_second_page["id"]

    async def test_cross_partition_query_with_continuation_token_async(self):
        """Original async cross-partition replay, without an explicit enable flag."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_cross_partition_query_with_continuation_token_async
        created_collection = self.container
        await created_collection.create_item(body={"pk": "pk1", "id": str(uuid.uuid4())})
        await created_collection.create_item(body={"pk": "pk2", "id": str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query="SELECT * from c",
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]
        assert second_page["id"] == second_page_fetched_with_continuation_token["id"]
