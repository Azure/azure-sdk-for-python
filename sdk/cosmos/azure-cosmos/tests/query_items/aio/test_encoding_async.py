# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async non-ASCII encoding tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_encoding_async.py::TestEncodingAsync``. Each method keeps
the original steps, query inputs and assertions; only setup and request
observation changed. Clients use ``_backend="rust"``; each test owns a
uniquely named database with the ``/pk`` single-partition container the
original shared setup provided, deleted afterwards.
"""
import unittest
import uuid
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from azure.cosmos import PartitionKey, _rust
from azure.cosmos.aio import CosmosClient
from config import clients
from config.settings import TestSettings, unique_database_id

_ITEM_BINDING_FUNCTIONS = (
    "create_item_async", "upsert_item_async", "replace_item_async", "patch_item_async", "execute_item_batch_async",
)


@contextmanager
def capture_requests(container, resource_type="docs"):
    """Original async non-ASCII encoding tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_encoding_async.py::TestEncodingAsync``. Each method keeps
the original steps, query inputs and assertions; only setup and request
observation changed. Clients use ``_backend="rust"``; each test owns a
uniquely named database with the ``/pk`` single-partition container the
original shared setup provided, deleted afterwards.
"""
    requests = []

    def wrap(original):
        def call(driver_handle, prepared, *args, **kwargs):
            body = prepared.body_bytes
            requests.append(SimpleNamespace(body=body.decode("ascii") if body.isascii() else body))
            return original(driver_handle, prepared, *args, **kwargs)
        return call

    patches = [patch.object(_rust, name, wrap(getattr(_rust, name))) for name in _ITEM_BINDING_FUNCTIONS]
    for p in patches:
        p.start()
    try:
        yield requests
    finally:
        for p in reversed(patches):
            p.stop()
    assert requests, "The operation did not send a matching request"


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestEncodingAsync(unittest.IsolatedAsyncioTestCase):
    """Original async non-ASCII encoding tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_encoding_async.py::TestEncodingAsync``. Each method keeps
the original steps, query inputs and assertions; only setup and request
observation changed. Clients use ``_backend="rust"``; each test owns a
uniquely named database with the ``/pk`` single-partition container the
original shared setup provided, deleted afterwards.
"""

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = unique_database_id("qi_encoding_async")
        self.TEST_SINGLE_PARTITION_CONTAINER_ID = "single_partition_" + uuid.uuid4().hex[:8]
        self.setup_client = CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust")
        await self.setup_client.__aenter__()
        self.client = None
        self.setup_db = None
        try:
            self.setup_db = await self.setup_client.create_database(self.TEST_DATABASE_ID)
            await self.setup_db.create_container(
                id=self.TEST_SINGLE_PARTITION_CONTAINER_ID,
                partition_key=PartitionKey(path="/" + TestSettings.TEST_CONTAINER_PARTITION_KEY),
                offer_throughput=TestSettings.THROUGHPUT_FOR_1_PARTITION,
            )
            # Open the async client and keep a handle to the test container.
            # The client is closed in asyncTearDown so we don't leak sockets.
            self.client = clients.create_data_client_async(_backend="rust")
            await self.client.__aenter__()
            self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
            self.created_container = self.created_db.get_container_client(self.TEST_SINGLE_PARTITION_CONTAINER_ID)
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            if self.setup_db is not None:
                await self.setup_client.delete_database(self.TEST_DATABASE_ID)
        finally:
            try:
                if self.client is not None:
                    await self.client.close()
            finally:
                await self.setup_client.close()

    async def test_round_trip_emoji_document_via_query_async_rust(self):
        # Source: tests/test_encoding_async.py::TestEncodingAsync.test_round_trip_emoji_document_via_query_async
        """Same content as the test above, but pulled back via a SQL
        query instead of a point read."""
        emoji_payload = u'query 🎉 — café 日本'  # cspell:disable-line
        doc_id = 'emoji-q-async-' + str(uuid.uuid4())
        document = {
            'pk': 'pk',
            'id': doc_id,
            'multibyte_content': emoji_payload,
        }
        await self.created_container.create_item(body=document)

        results = []
        async for item in self.created_container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{"name": "@id", "value": doc_id}],
                partition_key='pk'):
            results.append(item)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['multibyte_content'], emoji_payload)

    async def test_compact_utf8_item_writes_through_full_sdk_stack_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_encoding_async.py::TestEncodingAsync.test_compact_utf8_item_writes_through_full_sdk_stack_async
        """Exercise every item-write operation covered by the client option."""
        captured = {}

        def capture_body(request):
            captured['body'] = request.body

        def assert_compact_body(expected_content):
            # Compact bodies are handed to the transport as UTF-8 bytes, not str,
            # so that no transport layer can re-encode them (urllib3 1.x would
            # otherwise Latin-1 encode a str body via http.client).
            body = captured['body']
            self.assertIsInstance(body, bytes)
            decoded = body.decode('utf-8')
            self.assertIn(expected_content, decoded)
            self.assertNotIn('\\u65e5', decoded)

        async with clients.create_data_client_async(
            _backend="rust",
            enable_compact_utf8_item_writes=True
        ) as client:
            container = client.get_database_client(
                self.TEST_DATABASE_ID
            ).get_container_client(
                self.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            doc_id = 'utf8-writes-async-' + str(uuid.uuid4())

            # Keep the non-ASCII partition key: these operations must send an
            # escaped partition-key header alongside a raw UTF-8 item body.
            with capture_requests(container, resource_type='docs') as requests:
                created = await container.create_item({
                    'id': doc_id,
                    'pk': '日本',
                    'content': 'create café 日本 🎉',
                })
            for request in requests:
                capture_body(request)
            self.assertEqual(created['content'], 'create café 日本 🎉')

            # Round-tripping alone cannot detect a regression to escaped
            # output, since escaped JSON round-trips identically. Assert on
            # the bytes actually put on the wire.
            assert_compact_body(created['content'])

            created['content'] = 'upsert مرحبا 日本 🚀'  # cspell:disable-line
            with capture_requests(container, resource_type='docs') as requests:
                upserted = await container.upsert_item(
                    created,
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(upserted['content'], created['content'])
            assert_compact_body(upserted['content'])

            upserted['content'] = 'replace नमस्ते 日本 🌍'  # cspell:disable-line
            with capture_requests(container, resource_type='docs') as requests:
                replaced = await container.replace_item(
                    doc_id,
                    upserted,
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(replaced['content'], upserted['content'])
            assert_compact_body(replaced['content'])

            with capture_requests(container, resource_type='docs') as requests:
                patched = await container.patch_item(
                    doc_id,
                    partition_key='日本',
                    patch_operations=[
                        {
                            'op': 'set',
                            'path': '/content',
                            'value': 'patch שלום 日本 🎊',  # cspell:disable-line
                        },
                    ],
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(patched['content'], 'patch שלום 日本 🎊')  # cspell:disable-line
            assert_compact_body(patched['content'])

            # A patch filter predicate travels in the same request body as the
            # patch operations, so a non-ASCII predicate is affected by the
            # option too and must be sent compact and accepted by the service.
            with capture_requests(container, resource_type='docs') as requests:
                conditional = await container.patch_item(
                    doc_id,
                    partition_key='日本',
                    patch_operations=[
                        {
                            'op': 'set',
                            'path': '/content',
                            'value': 'conditional patch 日本 ✅',
                        },
                    ],
                    filter_predicate="FROM c WHERE c.pk = '日本'",
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(conditional['content'], 'conditional patch 日本 ✅')
            assert_compact_body("FROM c WHERE c.pk = '日本'")

            batch_id = 'utf8-batch-async-日本-' + str(uuid.uuid4())
            with capture_requests(container, resource_type='docs') as requests:
                batch_result = await container.execute_item_batch(
                    [(
                        'create',
                        ({'id': batch_id, 'pk': '日本', 'content': 'batch ไทย 日本 🎉'},),  # cspell:disable-line
                    )],
                    partition_key='日本',
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(batch_result[0]['statusCode'], 201)
            assert_compact_body('batch ไทย 日本 🎉')  # cspell:disable-line

            with capture_requests(container, resource_type='docs') as requests:
                read_batch_result = await container.execute_item_batch(
                    [('read', (batch_id,))],
                    partition_key='日本',
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(read_batch_result[0]['statusCode'], 200)
            self.assertEqual(read_batch_result[0]['resourceBody']['content'], 'batch ไทย 日本 🎉')  # cspell:disable-line
            self.assertNotIn('日本', captured['body'])
            self.assertIn('\\u65e5', captured['body'])

            # A delete-only batch is the other body-free shape: like read, the
            # operation carries just an id, so the item-write option must leave
            # it escaped. The service must still accept that escaped form.
            with capture_requests(container, resource_type='docs') as requests:
                delete_batch_result = await container.execute_item_batch(
                    [('delete', (batch_id,))],
                    partition_key='日本',
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(delete_batch_result[0]['statusCode'], 204)
            self.assertNotIn('日本', captured['body'])
            self.assertIn('\\u65e5', captured['body'])

            queried = []
            async for item in container.query_items(
                    query="SELECT * FROM c WHERE c.id = @id",
                    parameters=[{'name': '@id', 'value': doc_id}],
                    partition_key='日本'):
                queried.append(item)
            self.assertEqual(len(queried), 1)
            # The conditional patch is the last write to touch this item.
            self.assertEqual(queried[0]['content'], conditional['content'])
