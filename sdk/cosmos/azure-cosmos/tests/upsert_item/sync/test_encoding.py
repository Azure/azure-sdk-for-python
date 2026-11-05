# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync compact UTF-8 item-write test, which upserts an item, re-run on the Rust path.

Source: ``tests/test_encoding.py::TestEncoding``. The method keeps the original
steps and assertions; only setup and request observation changed. Clients use
``_backend="rust"``; the class owns a uniquely named database with the ``/pk``
single-partition container the original shared setup provided, deleted
afterwards.
"""

import unittest
import uuid
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import DatabaseProxy, ContainerProxy, PartitionKey, _rust
from config import clients
from config.settings import TestSettings, unique_database_id

_ITEM_BINDING_FUNCTIONS = ("create_item", "upsert_item", "replace_item", "patch_item", "execute_item_batch")


@contextmanager
def capture_requests(container, resource_type="docs"):
    """Stand-in for test_config.capture_requests, which patches the Python pipeline transport.

    The Rust backend does not send through that transport, so this records the
    request body the Python wrapper hands to the Rust binding for each item
    operation instead. Like the legacy transport, a compact (non-ASCII) body is
    exposed as UTF-8 bytes and an escaped ASCII body as ``str``.
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
class TestEncoding(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key.

    Marked for the emulator lane and both live lanes: the compact UTF-8
    item-write coverage below asserts on service behavior (2 MiB request
    limit, non-ASCII round trips) that the emulator only approximates, so
    these must also run against a live account.
    """

    client: cosmos_client.CosmosClient = None
    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("upsert_item_encoding")
        cls.TEST_SINGLE_PARTITION_CONTAINER_ID = "single_partition_" + uuid.uuid4().hex[:8]
        cls.setup_client = clients.create_setup_client(_backend="rust")
        cls.client = None
        try:
            setup_db = cls.setup_client.create_database(cls.TEST_DATABASE_ID)
            setup_db.create_container(
                id=cls.TEST_SINGLE_PARTITION_CONTAINER_ID,
                partition_key=PartitionKey(path="/" + TestSettings.TEST_CONTAINER_PARTITION_KEY),
                offer_throughput=TestSettings.THROUGHPUT_FOR_1_PARTITION,
            )
            cls.client = clients.create_data_client(_backend="rust")
            cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
            cls.created_container = cls.created_db.get_container_client(cls.TEST_SINGLE_PARTITION_CONTAINER_ID)
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            try:
                cls.setup_client.delete_database(cls.TEST_DATABASE_ID)
            except Exception:  # pylint: disable=broad-except
                pass
        finally:
            if cls.client is not None:
                cls.client.close()
            cls.setup_client.close()

    def test_compact_utf8_item_writes_through_full_sdk_stack_rust(self):
        # Source: tests/test_encoding.py::TestEncoding.test_compact_utf8_item_writes_through_full_sdk_stack
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

        with clients.create_data_client(
            _backend="rust",
            enable_compact_utf8_item_writes=True
        ) as client:
            container = client.get_database_client(
                self.TEST_DATABASE_ID
            ).get_container_client(
                self.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            doc_id = 'utf8-writes-' + str(uuid.uuid4())

            # Keep the non-ASCII partition key: these operations must send an
            # escaped partition-key header alongside a raw UTF-8 item body.
            with capture_requests(container, resource_type='docs') as requests:
                created = container.create_item({
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
                upserted = container.upsert_item(
                    created,
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(upserted['content'], created['content'])
            assert_compact_body(upserted['content'])

            upserted['content'] = 'replace नमस्ते 日本 🌍'  # cspell:disable-line
            with capture_requests(container, resource_type='docs') as requests:
                replaced = container.replace_item(
                    doc_id,
                    upserted,
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(replaced['content'], upserted['content'])
            assert_compact_body(replaced['content'])

            with capture_requests(container, resource_type='docs') as requests:
                patched = container.patch_item(
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
                conditional = container.patch_item(
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

            batch_id = 'utf8-batch-日本-' + str(uuid.uuid4())
            with capture_requests(container, resource_type='docs') as requests:
                batch_result = container.execute_item_batch(
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
                read_batch_result = container.execute_item_batch(
                    [('read', (batch_id,))],
                    partition_key='日本',
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(read_batch_result[0]['statusCode'], 200)
            self.assertEqual(read_batch_result[0]['resourceBody']['content'], 'batch ไทย 日本 🎉')  # cspell:disable-line
            # Rust path today: prepare_batch compacts read/delete-only batches, while legacy keeps them escaped
            # (_synchronized_request._should_escape_non_ascii_in_request_body), so this check and the delete-batch one fail.
            self.assertNotIn('日本', captured['body'])
            self.assertIn('\\u65e5', captured['body'])

            # A delete-only batch is the other body-free shape: like read, the
            # operation carries just an id, so the item-write option must leave
            # it escaped. The service must still accept that escaped form.
            with capture_requests(container, resource_type='docs') as requests:
                delete_batch_result = container.execute_item_batch(
                    [('delete', (batch_id,))],
                    partition_key='日本',
                )
            for request in requests:
                capture_body(request)
            self.assertEqual(delete_batch_result[0]['statusCode'], 204)
            self.assertNotIn('日本', captured['body'])
            self.assertIn('\\u65e5', captured['body'])

            queried = list(container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{'name': '@id', 'value': doc_id}],
                partition_key='日本',
            ))
            self.assertEqual(len(queried), 1)
            # The conditional patch is the last write to touch this item.
            self.assertEqual(queried[0]['content'], conditional['content'])


if __name__ == '__main__':
    unittest.main()
