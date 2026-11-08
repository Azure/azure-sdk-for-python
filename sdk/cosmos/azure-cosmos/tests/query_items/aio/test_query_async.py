# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied async paging, OFFSET LIMIT, DISTINCT, COUNT, MAX, and query/index-metrics tests against Rust.

Self-contained: builds its own database + container in ``asyncSetUp``
and registers cleanup immediately. Class and method names match
``tests/test_query_async.py``. OFFSET LIMIT helpers are copied from
``tests/test_config.py`` rather than importing the legacy configuration.
Query advice retains the original unconditional emulator-related skip.

Later copies (slashes, unsupported queries, partition-key continuation,
pagination, ``parameters=None``, timeouts and AVG) create containers in this
test's own database. The shared multi-partition container becomes an owned
``/pk`` container with 11000 RU.

Run with::

    pytest --noconftest tests/query_items/aio/test_query_async.py -v
"""
import asyncio
import os
import unittest
import uuid
from asyncio import gather
from unittest.mock import patch

import pytest

import azure.cosmos.aio._asynchronous_request as _asynchronous_request
import azure.cosmos.aio._retry_utility_async as retry_utility
import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey, http_constants, _endpoint_discovery_retry_policy
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos.aio import CosmosClient
from query_items._legacy_distinct_helpers import DistinctConfig, distinct_query_diagnostics
from query_items._legacy_feed_range_helpers import create_feed_range_in_dict, create_range


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


class _QueryConfig(DistinctConfig):
    @classmethod
    async def _validate_distinct(cls, created_collection, query, results, is_select, fields):
        """Put the actual query error first so CI cannot hide it behind wrapper frames."""
        with distinct_query_diagnostics(query):
            await super()._validate_distinct(created_collection, query, results, is_select, fields)

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

    @pytest.mark.cosmosEmulator
    @pytest.mark.asyncio
    async def test_populate_query_metrics_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_populate_query_metrics_async
        container_id = self._container_id
        created_collection = self.container
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_query_metrics=True
        )

        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in created_collection.client_connection.last_response_headers
        metrics_header = created_collection.client_connection.last_response_headers[metrics_header_name]
        # Validate header is well-formed: "key1=value1;key2=value2;etc"
        metrics = metrics_header.split(';')
        assert len(metrics) > 1
        assert all(['=' in x for x in metrics])

        await self.database.delete_container(container_id)

    @pytest.mark.cosmosEmulator
    async def test_populate_index_metrics_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_populate_index_metrics_async
        container_id = self._container_id
        created_collection = self.container
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            populate_index_metrics=True
        )

        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_index_metrics over Gateway V2, so the "
                    "index-utilization header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The query ran.")
        index_header_name = http_constants.HttpHeaders.IndexUtilization
        assert index_header_name in created_collection.client_connection.last_response_headers
        index_metrics = created_collection.client_connection.last_response_headers[index_header_name]
        assert index_metrics != {}
        assert 'UtilizedSingleIndexes' in index_metrics
        assert 'PotentialSingleIndexes' in index_metrics
        assert 'UtilizedCompositeIndexes' in index_metrics
        assert 'PotentialCompositeIndexes' in index_metrics

        # Backend index diagnostics can vary by region/build; validate stable signal instead of exact payload.
        candidate_indexes = list(index_metrics.get('UtilizedSingleIndexes', []))
        candidate_indexes.extend(index_metrics.get('PotentialSingleIndexes', []))
        assert any(
            idx.get('FilterExpression') == ''
            and idx.get('IndexImpactScore') == 'High'
            and idx.get('IndexSpec') in ('/pk/?', '/_epk/?')
            for idx in candidate_indexes
        )

        await self.database.delete_container(container_id)

    @pytest.mark.cosmosEmulator
    @pytest.mark.skip(reason="environment-gap: Emulator does not support query advisor yet")
    async def test_populate_query_advice_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_populate_query_advice_async
        container_id = self._container_id
        created_collection = self.container
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {
            'pk': 'pk', 'id': doc_id, 'name': 'test document',
            'tags': [{'name': 'python'}, {'name': 'cosmos'}],
            'timestamp': '2099-01-01T00:00:00Z', 'ticks': 0, 'ts': 0
        }
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        QUERY_ADVICE_HEADER = http_constants.HttpHeaders.QueryAdvice

        # QA1000 - PartialArrayContains: ARRAY_CONTAINS with partial match
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, {"name": "python"}, true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1000" in query_advice

        # QA1002 - Contains: CONTAINS usage
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE CONTAINS(c.name, "test")',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1002" in query_advice

        # QA1003 - CaseInsensitiveStartsWithOrStringEquals: case-insensitive STARTSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE STARTSWITH(c.name, "test", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1003" in query_advice

        # QA1004 - CaseInsensitiveEndsWith: case-insensitive ENDSWITH
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE ENDSWITH(c.name, "document", true)',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1004" in query_advice

        # QA1007 - GetCurrentDateTime: usage of GetCurrentDateTime
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.timestamp < GetCurrentDateTime()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1007" in query_advice

        # QA1008 - GetCurrentTicks: usage of GetCurrentTicks
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ticks < GetCurrentTicks()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1008" in query_advice

        # QA1009 - GetCurrentTimestamp: usage of GetCurrentTimestamp
        query_iterable = created_collection.query_items(
            query='SELECT * FROM c WHERE c.ts < GetCurrentTimestamp()',
            partition_key='pk', populate_query_advice=True
        )
        [item async for item in query_iterable]
        query_advice = created_collection.client_connection.last_response_headers.get(QUERY_ADVICE_HEADER)
        assert query_advice is not None
        assert "QA1009" in query_advice

        await self.database.delete_container(container_id)

    @pytest.mark.cosmosEmulator
    @pytest.mark.skip(
        reason="driver-gap: Gap 30 - Rust rejects MAX queries without a partition key "
        "(HTTP 400/1004). Re-enable when the driver supports this aggregate query."
    )
    async def test_value_max_query_results_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_value_max_query_results_async
        container = self.container
        await container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 3, "lookupVersion": "console_version"})
        await container.create_item(
            {"id": str(uuid.uuid4()), "isComplete": True, "version": 2, "lookupVersion": "console_version"})
        query = "Select value max(c.version) FROM c where c.isComplete = true and c.lookupVersion = @lookupVersion"
        query_results = container.query_items(query, parameters=[
            {"name": "@lookupVersion", "value": "console_version"}
        ])
        item_list = [item async for item in query_results]
        assert len(item_list) == 1
        assert item_list[0] == 3

    @pytest.mark.cosmosEmulator
    @pytest.mark.skip(
        reason="driver-gap: Gap 30 - For SELECT DISTINCT c[\"value\"] with ORDER BY and "
        "OFFSET LIMIT, Rust returns rows with a '$1' field instead of the requested "
        "'value' field, so the unchanged test raises KeyError. Re-enable when the "
        "driver preserves the selected property name."
    )
    async def test_offset_limit_async_rust(self):
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

    @pytest.mark.cosmosEmulator
    async def test_distinct_async_rust(self):
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

        # Known gap 30: query_items() remaining query, paging, and continuation-token gaps, item 2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30).
        pytest.skip("driver-gap: Rust rejects cross-partition unordered DISTINCT without TOP or LIMIT "
                    "(400/20125 ClientBufferedQueryRequiresFiniteWindow) (known gap 30 item 2, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30). The documents were created.")
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

    @pytest.mark.cosmosEmulator
    async def test_partition_scoped_count_is_index_only_async_rust(self):
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

            # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
            pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                        "metrics header is missing (known gap 36, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). The COUNT query ran.")
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

    @pytest.mark.cosmosEmulator
    async def test_paging_with_continuation_token_async_rust(self):
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
        created_collection = self.container

        document_definition = {'pk': 'pk', 'id': '1'}
        await created_collection.upsert_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        await created_collection.upsert_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    @pytest.mark.cosmosEmulator
    async def test_continuation_token_size_limit_query_async_rust(self):
        """Preserve the original async one-kilobyte token assertions on owned data."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_continuation_token_size_limit_query_async
        container = self.container
        for i in range(1, 1000):
            await container.create_item(body=dict(pk='123', id=str(uuid.uuid4()), some_value=str(i % 3)))
        query = "Select * from c where c.some_value='2'"
        response_query = container.query_items(query, partition_key='123', max_item_count=100,
                                               continuation_token_limit=1)
        pager = response_query.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        assert len(token.encode('utf-8')) <= 1024
        await pager.__anext__()
        token = pager.continuation_token
        assert len(token.encode('utf-8')) <= 1024

    @pytest.mark.cosmosEmulator
    async def test_continuation_token_limit_preserves_broad_scope_and_resume_async_rust(
        self,
    ):
        """Forward the service limit without imposing a size cap on the SDK token."""
        container = await self._create_multi_partition_container()
        ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        self.assertGreater(len(ranges), 1)
        expected = {f"token-limit-{i}" for i in range(7)}
        for i in range(7):
            await container.create_item(
                {"id": f"token-limit-{i}", "pk": f"customer-{i % 3}"}
            )
        full_range = {
            "Range": {
                "min": "",
                "max": "FF",
                "isMinInclusive": True,
                "isMaxInclusive": False,
            }
        }
        for scope in ({}, {"feed_range": full_range}):
            with self.subTest(scope=scope):
                options = dict(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    continuation_token_limit=1,
                    enable_cross_partition_query=True,
                    **scope,
                )
                pages = container.query_items(**options).by_page()
                first = [row async for row in await pages.__anext__()]
                token = pages.continuation_token
                self.assertTrue(first)
                self.assertTrue(token)
                resumed = container.query_items(**options).by_page(
                    continuation_token=token
                )
                rows = first + [row async for page in resumed async for row in page]
                self.assertEqual(len(rows), len(expected))
                self.assertEqual({row["id"] for row in rows}, expected)

    @pytest.mark.cosmosEmulator
    async def test_cross_partition_query_with_continuation_token_async_rust(self):
        """Original async cross-partition replay, without an explicit enable flag."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_cross_partition_query_with_continuation_token_async
        created_collection = self.container
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]
        assert second_page['id'] == second_page_fetched_with_continuation_token['id']

    # Copies below use owned containers in this test's database. The shared
    # TEST_MULTI_PARTITION_CONTAINER_ID (``/pk``) becomes an owned ``/pk``
    # container with 11000 RU so it still spans more than one physical partition.
    # The original's sync key-auth setup client is replaced by awaited calls on
    # this test's Rust-backed async client.

    async def _create_container_for_test(self, container_id, partition_key, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._create_container_for_test
        return await self.database.create_container(id=container_id, partition_key=partition_key, **kwargs)

    async def _create_container_if_not_exists_for_test(self, container_id, partition_key, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._create_container_if_not_exists_for_test
        return await self.database.create_container_if_not_exists(
            id=container_id, partition_key=partition_key, **kwargs)

    async def _delete_container_for_test(self, container_id):
        # Source helper: tests/test_query_async.py::TestQueryAsync._delete_container_for_test
        await self.database.delete_container(container_id)

    async def _create_multi_partition_container(self):
        return await self.database.create_container(
            id="multi_partition_" + uuid.uuid4().hex[:8], partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_first_and_last_slashes_trimmed_for_query_string_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_async.py::TestQueryAsync.test_first_and_last_slashes_trimmed_for_query_string_async
        container_id = str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        doc_id = 'myId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await created_collection.create_item(body=document_definition)
        await asyncio.sleep(1)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key='pk'
        )
        iter_list = [item async for item in query_iterable]
        assert iter_list[0]['id'] == doc_id

        await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    @pytest.mark.skip(reason="internals-only: the original is unconditionally skipped and counts requests by "
                             "patching legacy _retry_utility_async.ExecuteFunctionAsync, which Rust never calls.")
    async def test_max_item_count_honored_in_order_by_query_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_max_item_count_honored_in_order_by_query_async
        container_id = str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        docs = []
        for i in range(10):
            document_definition = {'pk': 'pk', 'id': 'myId' + str(uuid.uuid4())}
            docs.append(await created_collection.create_item(body=document_definition))

        query = 'SELECT * from c ORDER BY c._ts'
        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=1
        )
        await self.validate_query_requests_count(query_iterable, 25)

        query_iterable = created_collection.query_items(
            query=query,
            max_item_count=100
        )

        await self.validate_query_requests_count(query_iterable, 5)

        await self._delete_container_for_test(container_id)

    async def validate_query_requests_count(self, query_iterable, expected_count):
        # Source helper: tests/test_query_async.py::TestQueryAsync.validate_query_requests_count
        self.count = 0
        self.OriginalExecuteFunction = retry_utility.ExecuteFunctionAsync
        retry_utility.ExecuteFunctionAsync = self._mock_execute_function
        item_pages = query_iterable.by_page()
        while True:
            try:
                page = await item_pages.__anext__()
                assert len([item async for item in page]) > 0
            except StopAsyncIteration:
                break
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        assert self.count == expected_count
        self.count = 0

    async def _mock_execute_function(self, function, *args, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._mock_execute_function
        self.count += 1
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_unsupported_queries_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_unsupported_queries_async
        # Known gap 30 item 9: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust returns raw per-partition rows for the cross-partition non-VALUE aggregate "
            "'SELECT COUNT(1) FROM c' instead of the legacy 400 rejection (known gap 30 item 9, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-non-value-aggregate)."
        )
        created_collection = await self._create_multi_partition_container()
        queries = ['SELECT COUNT(1) FROM c', 'SELECT COUNT(1) + 5 FROM c', 'SELECT COUNT(1) + SUM(c) FROM c']
        for query in queries:
            query_iterable = created_collection.query_items(query=query)
            try:
                results = [item async for item in query_iterable]
                self.fail("query '{}' should have failed".format(query))
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_with_non_overlapping_pk_ranges_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_with_non_overlapping_pk_ranges_async
        created_collection = await self._create_multi_partition_container()
        query_iterable = created_collection.query_items("select * from c where c.pk='1' or c.pk='2'")
        assert [item async for item in query_iterable] == []

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_full_pk_continuation_emits_legacy_by_default_async_rust(self):
        """Full partition-key queries return legacy continuation tokens by default."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_full_pk_continuation_emits_legacy_by_default_async
        created_collection = await self._create_multi_partition_container()
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        assert token is not None
        assert _decode_token(token) is None

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_full_pk_legacy_replay_resumes_same_page_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_full_pk_legacy_replay_resumes_same_page_async
        created_collection = await self._create_multi_partition_container()
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        assert token is not None
        assert _decode_token(token) is None

        replay_pager = query_iterable.by_page(token)
        replay_second_page = [item async for item in await replay_pager.__anext__()][0]
        assert second_page['id'] == replay_second_page['id']

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_cross_partition_query_with_none_partition_key_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_cross_partition_query_with_none_partition_key_async
        created_collection = await self._create_multi_partition_container()
        document_definition = {'pk': 'pk1', 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)
        document_definition = {'pk': 'pk2' , 'id': str(uuid.uuid4())}
        await created_collection.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key=None)

        assert len([item async for item in query_iterable]) >= 2

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_cosmos_query_retryable_error_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_cosmos_query_retryable_error_async
        async def query_items(database):
            # Tests to make sure 429 exception is surfaced when retries run out in the first page of a query.
            try:
                await self._create_container_for_test(
                    "query_retryable_error_test", PartitionKey(path="/pk"), offer_throughput=400
                )
                container = database.get_container_client("query_retryable_error_test")
            except exceptions.CosmosResourceExistsError:
                container = database.get_container_client("query_retryable_error_test")
            query = "SELECT * FROM c"
            try:
                query_iterable = [d async for d in container.query_items(query, max_item_count=10)]
                if len(query_iterable) == 0:
                    # Query should not return empty if it has items to query on a retryable exception is raised
                    pytest.fail("Expected 429 Exception.")
            except exceptions.CosmosHttpResponseError as ex:
                # A retryable exception should be surfaced when retries run out
                assert ex.status_code == 429

        await self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        created_collection = self.database.get_container_client("query_retryable_error_test")
        # Created items to query
        for _ in range(150):
            partition_key = 'pk' + str(uuid.uuid4())
            item = {
                'id': 'item' + str(uuid.uuid4()),
                'partitionKey': partition_key,
                'content': 'This is some random content',
            }

            try:
                await created_collection.upsert_item(item)
            except exceptions.CosmosHttpResponseError as e:
                pytest.fail(e)
        # Known gap 11: Closed: driver-owned throttle retry waiting (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). Throttle retries are owned by the Rust driver.
        pytest.skip("internals-only: the 429 is forced by replacing the legacy "
                    "client_connection.connection_policy.RetryOptions object, which the Rust driver does not "
                    "read; it owns throttle retries (known gap 11). The items were upserted.")
        # Set retry options to fail much more easily to avoid too much concurrency
        retry_options = RetryOptions(max_retry_attempt_count=1,
                                     fixed_retry_interval_in_milliseconds=1, max_wait_time_in_seconds=1)
        old_retry = self.client.client_connection.connection_policy.RetryOptions
        self.client.client_connection.connection_policy.RetryOptions = retry_options
        await self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        # Force a 429 exception by having multiple concurrent queries.
        num_queries = 4
        await gather(*[query_items(self.database) for _ in range(num_queries)])

        self.client.client_connection.connection_policy.RetryOptions = old_retry
        await self._delete_container_for_test("query_retryable_error_test")

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_request_params_none_retry_policy_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_request_params_none_retry_policy_async
        container_id = "query_request_params_none_retry_policy_" + str(uuid.uuid4())
        created_collection = await self._create_container_if_not_exists_for_test(
            container_id, PartitionKey(path="/pk"))
        items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5}
        ]

        for item in items:
            await created_collection.create_item(body=item)

        # Known gap 11: Closed: driver-owned throttle retry waiting (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). Retry policies are owned by the Rust driver.
        pytest.skip("internals-only: the errors are injected by patching legacy "
                    "_retry_utility_async.ExecuteFunctionAsync and the legacy endpoint-discovery retry policy; "
                    "Rust never calls them and owns its retries (known gap 11). The items were created.")
        self.OriginalExecuteFunction = retry_utility.ExecuteFunctionAsync
        # Test session retry will properly push the exception when retries run out
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionSessionRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 404.1002 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.NOT_FOUND
            assert e.sub_status == http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE

        # Test endpoint discovery retry
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionEndPointRetry
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 3
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 10
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 403.3 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.FORBIDDEN
            assert e.sub_status == http_constants.SubStatusCodes.WRITE_FORBIDDEN
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Max_retry_attempt_count = 120
        _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds = 1000

        # Finally lets test timeout failover retry
        retry_utility.ExecuteFunctionAsync = self._MockExecuteFunctionTimeoutFailoverRetry
        try:
            query = "SELECT * FROM c"
            items = created_collection.query_items(
                query=query,
            )
            fetch_results = [item async for item in items]
            pytest.fail("Expected 408 Exception.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == http_constants.StatusCodes.REQUEST_TIMEOUT
        retry_utility.ExecuteFunctionAsync = self.OriginalExecuteFunction
        await self._delete_container_for_test(container_id)

    async def _MockExecuteFunctionSessionRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._MockExecuteFunctionSessionRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.NOT_FOUND,
                                                                 message="Read Session is Not Available")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.READ_SESSION_NOTAVAILABLE
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def _MockExecuteFunctionEndPointRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._MockExecuteFunctionEndPointRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.FORBIDDEN,
                                                                 message="End Point Discovery")
                ex_to_raise.sub_status = http_constants.SubStatusCodes.WRITE_FORBIDDEN
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    async def _MockExecuteFunctionTimeoutFailoverRetry(self, function, *args, **kwargs):
        # Source helper: tests/test_query_async.py::TestQueryAsync._MockExecuteFunctionTimeoutFailoverRetry
        if args:
            if args[1].operation_type == 'SqlQuery':
                ex_to_raise = exceptions.CosmosHttpResponseError(status_code=http_constants.StatusCodes.REQUEST_TIMEOUT,
                                                                 message="Timeout Failover")
                raise ex_to_raise
        return await self.OriginalExecuteFunction(function, *args, **kwargs)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_partitioned_query_response_hook_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_partitioned_query_response_hook_async
        container_id = "query_response_hook_test" + str(uuid.uuid4())
        created_collection = await self._create_container_if_not_exists_for_test(
            container_id, PartitionKey(path="/pk"))
        items = [
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10},
            {'id': str(uuid.uuid4()), 'pk': '0', 'val': 5},
            {'id': str(uuid.uuid4()), 'pk': '1', 'val': 10}
        ]

        for item in items:
            await created_collection.create_item(body=item)

        response_hook = ResponseHookCaller()
        item_list = [item async for item in created_collection.query_items("select * from c", partition_key="0", response_hook=response_hook)]
        assert len(item_list) == 3
        assert response_hook.count == 1
        await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_pagination_with_max_item_count_async_rust(self):
        """Test pagination showing per-page limits and total results counting."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_pagination_with_max_item_count_async
        container_id = "pagination_test_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))

        total_items = 20
        partition_key_value = "test_pk"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            await created_collection.create_item(body=document_definition)

        max_items_per_page = 7
        query = "SELECT * FROM c WHERE c.pk = @pk ORDER BY c['value']"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value,
            max_item_count=max_items_per_page
        )

        all_fetched_results = []
        page_count = 0
        item_pages = query_iterable.by_page()

        async for page in item_pages:
            page_count += 1
            items_in_page = [item async for item in page]
            all_fetched_results.extend(items_in_page)
            assert len(items_in_page) <= max_items_per_page

        assert len(all_fetched_results) == total_items
        assert page_count == 3

        for i, item in enumerate(all_fetched_results):
            assert item['value'] == i

        await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_pagination_without_max_item_count_async_rust(self):
        """Test pagination behavior without specifying max_item_count."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_pagination_without_max_item_count_async
        container_id = "pagination_no_max_test_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))

        total_items = 15
        partition_key_value = "test_pk_2"
        for i in range(total_items):
            document_definition = {
                'pk': partition_key_value,
                'id': f'item_{i}',
                'value': i
            }
            await created_collection.create_item(body=document_definition)

        query = "SELECT * FROM c WHERE c.pk = @pk"
        query_iterable = created_collection.query_items(
            query=query,
            parameters=[{"name": "@pk", "value": partition_key_value}],
            partition_key=partition_key_value
        )

        all_results = [item async for item in query_iterable]
        assert len(all_results) == total_items

        await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_items_with_parameters_none_async_rust(self):
        """Test that query_items handles parameters=None correctly (issue #43662)."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_items_with_parameters_none_async
        container_id = "test_params_none_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))

        # Create test documents
        doc1_id = 'doc1_' + str(uuid.uuid4())
        doc2_id = 'doc2_' + str(uuid.uuid4())
        await created_collection.create_item(body={'pk': 'pk1', 'id': doc1_id, 'value1': 1})
        await created_collection.create_item(body={'pk': 'pk2', 'id': doc2_id, 'value1': 2})

        # Test 1: Explicitly passing parameters=None should not cause TypeError
        query = 'SELECT * FROM c'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None
        )
        results = [item async for item in query_iterable]
        assert len(results) == 2

        # Test 2: parameters=None with partition_key should work
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='pk1'
        )
        results = [item async for item in query_iterable]
        assert len(results) == 1
        assert results[0]['id'] == doc1_id

        # Test 3: Verify parameterized query still works with actual parameters
        query_with_params = 'SELECT * FROM c WHERE c.value1 = @value'
        query_iterable = created_collection.query_items(
            query=query_with_params,
            parameters=[{'name': '@value', 'value': 2}]
        )
        results = [item async for item in query_iterable]
        assert len(results) == 1
        assert results[0]['id'] == doc2_id

        # Test 4: Query without parameters argument should work (default behavior)
        query_iterable = created_collection.query_items(
            query=query
        )
        results = [item async for item in query_iterable]
        assert len(results) == 2

        await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_query_items_parameters_none_with_options_async_rust(self):
        """Test parameters=None works with various query options."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_query_items_parameters_none_with_options_async
        container_id = "test_params_none_opts_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(container_id, PartitionKey(path="/pk"))

        # Create multiple test documents
        for i in range(5):
            doc_id = f'doc_{i}_' + str(uuid.uuid4())
            await created_collection.create_item(body={'pk': 'test', 'id': doc_id, 'index': i})

        # Test with parameters=None and max_item_count
        query = 'SELECT * FROM c ORDER BY c.index'
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            max_item_count=2
        )

        # Verify pagination works
        page_count = 0
        total_items = 0
        async for page in query_iterable.by_page():
            page_count += 1
            items = [item async for item in page]
            total_items += len(items)
            assert len(items) <= 2

        assert total_items == 5
        assert page_count >= 2  # Should have multiple pages

        # Test with parameters=None and populate_query_metrics
        query_iterable = created_collection.query_items(
            query=query,
            parameters=None,
            partition_key='test',
            populate_query_metrics=True
        )
        results = [item async for item in query_iterable]
        assert len(results) == 5

        # Known gap 36: Query diagnostics and other request options are not sent over Gateway V2 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).
        pytest.skip("driver-gap: Rust does not send populate_query_metrics over Gateway V2, so the "
                    "metrics header is missing (known gap 36, "
                    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36). Paging and the query ran.")
        # Verify query metrics were populated
        metrics_header_name = 'x-ms-documentdb-query-metrics'
        assert metrics_header_name in created_collection.client_connection.last_response_headers

        await self._delete_container_for_test(container_id)

    def _capture_pipeline_kwarg_async(self, kwarg_name):
        # Source helper: tests/test_query_async.py::TestQueryAsync._capture_pipeline_kwarg_async
        captured = []
        original = _asynchronous_request._PipelineRunFunction

        async def _wrapper(pipeline_client, request, **kwargs):
            captured.append((str(request.url), kwargs.get(kwarg_name)))
            return await original(pipeline_client, request, **kwargs)

        return captured, patch.object(
            _asynchronous_request, "_PipelineRunFunction", side_effect=_wrapper,
        )

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_outer_timeout_propagates_through_by_page_paging_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_async.py::TestQueryAsync.test_outer_timeout_propagates_through_by_page_paging_async
        container_id = "by_page_outer_timeout_async_" + str(uuid.uuid4())
        container = await self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            outer_timeout = 15
            captured, ctx = self._capture_pipeline_kwarg_async("timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    timeout=outer_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            # Known gap 5: Closed: runtime and operation timeout scopes (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). The driver applies the operation budget; Rust never calls legacy _asynchronous_request.
            pytest.skip("internals-only: per-request timeout values were captured by patching legacy "
                        "_asynchronous_request._PipelineRunFunction, which Rust never calls; the driver owns "
                        "the operation budget (known gap 5). The paged query with timeout ran.")
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            non_none = [t for t in doc_values if t is not None]
            self.assertGreater(len(non_none), 0)
            for t in non_none:
                self.assertLessEqual(t, outer_timeout)
        finally:
            await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_connection_timeout_propagates_through_by_page_paging_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_async.py::TestQueryAsync.test_connection_timeout_propagates_through_by_page_paging_async
        container_id = "by_page_conn_timeout_async_" + str(uuid.uuid4())
        container = await self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(6):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": i % 2, "data": i}
                )

            connection_timeout = 27
            # Known gap 5: Closed: runtime and operation timeout scopes (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). Rust-served operations reject per-call connection_timeout.
            pytest.skip("accepted-vnext-change: Rust query_items rejects per-call connection_timeout with "
                        "NotImplementedError; connection limits belong to the runtime (known gap 5, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5). The items were created.")
            captured, ctx = self._capture_pipeline_kwarg_async("connection_timeout")
            with ctx:
                pages = container.query_items(
                    query="SELECT * FROM c",
                    max_item_count=1,
                    connection_timeout=connection_timeout,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            doc_values = [t for (url, t) in captured if "/docs" in url]
            self.assertGreater(len(doc_values), 0)
            self.assertTrue(all(t == connection_timeout for t in doc_values))
        finally:
            await self._delete_container_for_test(container_id)

    @pytest.mark.cosmosCircuitBreaker
    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADQuery
    async def test_avg_aggregate_by_page_raises_value_error_cross_partition_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_async.py::TestQueryAsync.test_avg_aggregate_by_page_raises_value_error_cross_partition_async
        container_id = "by_page_avg_cross_async_" + str(uuid.uuid4())
        container = await self._create_container_for_test(
            container_id, PartitionKey(path="/pk"), offer_throughput=11000,
        )
        try:
            for i in range(20):
                await container.create_item(
                    {"id": f"item_{i}_{uuid.uuid4()}", "pk": f"pk_{i}", "amount": i + 10}
                )

            # A feed range that covers the full hash space forces the
            # query to fan out across every physical partition.
            full_range = create_range(
                range_min="",
                range_max="FF",
                is_min_inclusive=True,
                is_max_inclusive=False,
            )
            feed_range = create_feed_range_in_dict(full_range)

            # Known gap 30: query_items remaining query, paging, and continuation-token gaps, item 1 aggregates (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum).
            pytest.skip("driver-gap: Rust rejects full-range aggregates with 400/20113 "
                        "(ClientUnsupportedQueryFeature) instead of the legacy AVG ValueError (known gap 30 item 1, "
                        "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum). The items were created.")
            with self.assertRaises(ValueError) as cm:
                pages = container.query_items(
                    query="SELECT VALUE AVG(c.amount) FROM c",
                    feed_range=feed_range,
                    max_item_count=1,
                ).by_page()
                async for page in pages:
                    [item async for item in page]
            self.assertIn("AVG", str(cm.exception).upper())

            # Control: a single-partition AVG must still succeed.
            single_pages = container.query_items(
                query="SELECT VALUE AVG(c.amount) FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "pk_0"}],
                partition_key="pk_0",
                max_item_count=1,
            ).by_page()
            single_result = []
            async for page in single_pages:
                async for item in page:
                    single_result.append(item)
            self.assertEqual(len(single_result), 1)
        finally:
            await self._delete_container_for_test(container_id)


class ResponseHookCaller:
    # Source helper: tests/_test_helpers.py::ResponseHookCaller
    def __init__(self):
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
