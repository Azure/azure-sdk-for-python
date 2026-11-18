# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async callback/result comparisons, with Rust clients and owned resources."""

import unittest
import uuid
from collections.abc import Mapping

import pytest

from config import clients, settings
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeadersAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config = settings.TestSettings
        self.key_client = CosmosClient(config.host, config.masterKey, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        database_id = "response_hooks_async_" + uuid.uuid4().hex
        self.key_db = await self.key_client.create_database(database_id)
        self.addAsyncCleanup(self.key_client.delete_database, database_id)
        self.client = clients.create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(database_id)

    async def _create_container_for_test(self, container_id, partition_key):
        await self.key_db.create_container(container_id, partition_key)
        return self.created_db.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id):
        await self.key_db.delete_container(container_id)

    async def test_query_response_headers_match_last_response_hook_invocation_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_query_response_headers_match_last_response_hook_invocation_async
        cid = "test_headers_hookparity_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(12):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})
            captured_pages = []

            def hook(headers, _result):
                captured_pages.append(dict(headers))

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test", max_item_count=4, response_hook=hook,
            )
            items = [item async for item in query_iterable]
            assert len(items) == 12
            assert len(captured_pages) > 0
            final_headers = query_iterable.get_response_headers()
            assert final_headers["x-ms-request-charge"] == captured_pages[-1]["x-ms-request-charge"]
            assert final_headers["x-ms-activity-id"] == captured_pages[-1]["x-ms-activity-id"]
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_query_items_change_feed_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_query_items_change_feed_async
        cid = "test_hookparity_cf_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})
            captured = []

            def hook(headers, _result):
                captured.append(dict(headers))

            paged = created_collection.query_items_change_feed(
                start_time="Beginning", max_item_count=2, response_hook=hook,
            )
            items = [item async for item in paged]
            assert len(items) >= 6
            assert len(captured) > 0, "response_hook must fire at least once"
            assert "x-ms-request-charge" in captured[-1]
            if hasattr(paged, "get_response_headers"):
                final_headers = paged.get_response_headers()
                assert "x-ms-request-charge" in final_headers
                assert final_headers["x-ms-request-charge"] == captured[-1]["x-ms-request-charge"]
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_point_ops_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_point_ops_async
        cid = "test_hookparity_point_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            captured.clear()
            created = await created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1}, response_hook=hook,
            )
            assert len(captured) == 1
            assert created.get_response_headers()["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            captured.clear()
            read = await created_collection.read_item(item="doc1", partition_key="p", response_hook=hook)
            assert len(captured) == 1
            assert read.get_response_headers()["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            captured.clear()
            replaced = await created_collection.replace_item(
                item="doc1", body={"pk": "p", "id": "doc1", "value": 2}, response_hook=hook,
            )
            assert len(captured) == 1
            assert replaced.get_response_headers()["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            captured.clear()
            upserted = await created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3}, response_hook=hook,
            )
            assert len(captured) == 1
            assert upserted.get_response_headers()["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            captured.clear()
            await created_collection.delete_item(item="doc1", partition_key="p", response_hook=hook)
            assert len(captured) == 1
            assert "x-ms-request-charge" in captured[0]
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_query_databases_and_query_containers_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_query_databases_and_query_containers_async
        captured_db = []

        def hook_db(*args):
            captured_db.append(args[0])

        db_pager = self.client.query_databases(query="SELECT * FROM root r", response_hook=hook_db)
        _ = [item async for item in db_pager]
        assert len(captured_db) == 1, "query_databases hook must fire exactly once"
        assert isinstance(captured_db[0], Mapping)
        captured_c = []

        def hook_c(*args):
            captured_c.append(args[0])

        c_pager = self.created_db.query_containers(query="SELECT * FROM root r", response_hook=hook_c)
        _ = [item async for item in c_pager]
        assert len(captured_c) == 1, "query_containers hook must fire exactly once"
        assert isinstance(captured_c[0], Mapping)

    async def test_response_hook_fires_at_least_once_for_every_paged_surface_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_fires_at_least_once_for_every_paged_surface_async
        cid = "test_hookfires_paged_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                await created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            async def _run(surface_name, build_pager):
                captured = []

                def hook(headers, _result):
                    captured.append(dict(headers))

                pager = build_pager(hook)
                _ = [item async for item in pager]
                assert len(captured) > 0, f"{surface_name} response_hook never fired"
                for payload in captured:
                    assert isinstance(payload, Mapping), f"{surface_name} hook received non-Mapping payload"

            await _run("query_items", lambda h: created_collection.query_items(
                query="SELECT * FROM c", partition_key="test", response_hook=h,
            ))
            await _run("query_items_change_feed", lambda h: created_collection.query_items_change_feed(
                start_time="Beginning", max_item_count=2, response_hook=h,
            ))
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_patch_item_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_patch_item_async
        cid = "test_hookparity_patch_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            await created_collection.create_item(body={"pk": "p", "id": "doc-patch", "value": 1})
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            patched = await created_collection.patch_item(
                item="doc-patch", partition_key="p",
                patch_operations=[{"op": "replace", "path": "/value", "value": 99}],
                response_hook=hook,
            )
            assert len(captured) == 1
            patched_headers = patched.get_response_headers()
            assert patched_headers["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            assert patched_headers["x-ms-activity-id"] == captured[0]["x-ms-activity-id"]
            assert patched["value"] == 99
        finally:
            await self._delete_container_for_test(cid)

    async def test_response_hook_parity_execute_item_batch_async_rust(self):
        # Source: tests/test_query_response_headers_async.py::TestQueryResponseHeadersAsync.test_response_hook_parity_execute_item_batch_async
        cid = "test_hookparity_batch_async_" + str(uuid.uuid4())
        created_collection = await self._create_container_for_test(cid, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            batch_ops = [
                ("create", ({"pk": "p", "id": "batch-doc-1", "value": 1},)),
                ("upsert", ({"pk": "p", "id": "batch-doc-2", "value": 2},)),
            ]
            result = await created_collection.execute_item_batch(
                batch_operations=batch_ops, partition_key="p", response_hook=hook,
            )
            assert len(captured) == 1
            result_headers = result.get_response_headers()
            assert result_headers["x-ms-request-charge"] == captured[0]["x-ms-request-charge"]
            assert result_headers["x-ms-activity-id"] == captured[0]["x-ms-activity-id"]
            assert len(result) == 2
        finally:
            await self._delete_container_for_test(cid)
