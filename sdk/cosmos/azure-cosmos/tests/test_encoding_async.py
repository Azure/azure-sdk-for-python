# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async data-plane versions of the encoding round-trip tests.

This mirrors the sync document/partition-key checks and emoji round-trips
using the async client. The stored-procedure control-plane check remains in
the sync file because it relies on key-auth script operations.
"""
import json
import unittest
import uuid

import pytest

import test_config
from azure.cosmos import exceptions


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestEncodingAsync(unittest.IsolatedAsyncioTestCase):
    """Async round-trips for non-ASCII document content.

    Marked for the emulator lane and both live lanes so the compact UTF-8
    item-write coverage runs against a real account as well.
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    @staticmethod
    def _large_cjk_document(id_prefix):
        return {
            'id': id_prefix + str(uuid.uuid4()),
            'pk': 'pk',
            'content': '日' * 400000,
        }

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]'
                or cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' (ACCOUNT_KEY env var) and 'host' (ACCOUNT_HOST "
                "env var) to run the tests."
            )

    async def asyncSetUp(self):
        # Open the async client and keep a handle to the test container.
        # The client is closed in asyncTearDown so we don't leak sockets.
        self.client = test_config.TestConfig.create_data_client_async()
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(
            test_config.TestConfig.TEST_DATABASE_ID
        )
        self.created_container = self.created_db.get_container_client(
            test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_unicode_characters_in_partition_key_async(self):
        test_string = u'€€ کلید پارتیشن विभाजन कुंजी \t123'  # cspell:disable-line
        document_definition = {
            'pk': test_string,
            'id': 'myid' + str(uuid.uuid4()),
        }
        created_doc = await self.created_container.create_item(body=document_definition)

        read_doc = await self.created_container.read_item(
            item=created_doc['id'],
            partition_key=test_string,
        )
        self.assertEqual(read_doc['pk'], test_string)

    async def test_create_document_with_line_separator_para_seperator_next_line_unicodes_async(self):
        test_string = u'Line Separator (\u2028) & Paragraph Separator (\u2029) & Next Line (\x85) & نیم\u200cفاصله'  # cspell:disable-line
        document_definition = {
            'pk': 'pk',
            'id': 'myid' + str(uuid.uuid4()),
            'unicode_content': test_string,
        }
        created_doc = await self.created_container.create_item(body=document_definition)

        read_doc = await self.created_container.read_item(
            item=created_doc['id'],
            partition_key='pk',
        )
        self.assertEqual(read_doc['unicode_content'], test_string)

    async def test_round_trip_emoji_document_through_full_sdk_stack_async(self):
        """Writes a document containing emoji, reads it back, and checks
        the read content matches the written content exactly."""
        emoji_payload = u'celebration 🎉🎊 — café 日本 🌍'  # cspell:disable-line
        doc_id = 'emoji-rt-async-' + str(uuid.uuid4())
        document = {
            'pk': 'pk',
            'id': doc_id,
            'multibyte_content': emoji_payload,
        }

        created = await self.created_container.create_item(body=document)
        self.assertEqual(created['multibyte_content'], emoji_payload)

        read = await self.created_container.read_item(
            item=doc_id, partition_key='pk'
        )
        self.assertEqual(read['multibyte_content'], emoji_payload)
        self.assertEqual(
            read['multibyte_content'].encode('utf-8'),
            emoji_payload.encode('utf-8'),
        )

    async def test_round_trip_emoji_document_via_query_async(self):
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

    async def test_compact_utf8_item_writes_through_full_sdk_stack_async(self):
        """Exercise every item-write operation covered by the client option."""
        captured = {}

        def capture_body(request):
            captured['body'] = request.http_request.body

        async with test_config.TestConfig.create_data_client_async(
            enable_compact_utf8_item_writes=True
        ) as client:
            container = client.get_database_client(
                test_config.TestConfig.TEST_DATABASE_ID
            ).get_container_client(
                test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            doc_id = 'utf8-writes-async-' + str(uuid.uuid4())

            # Keep the non-ASCII partition key: these operations must send an
            # escaped partition-key header alongside a raw UTF-8 item body.
            created = await container.create_item({
                'id': doc_id,
                'pk': '日本',
                'content': 'create café 日本 🎉',
            }, raw_request_hook=capture_body)
            self.assertEqual(created['content'], 'create café 日本 🎉')

            # Round-tripping alone cannot detect a regression to escaped
            # output, since escaped JSON round-trips identically. Assert on
            # the bytes actually put on the wire.
            self.assertIsInstance(captured['body'], str)
            self.assertIn('日本', captured['body'])
            self.assertNotIn('\\u65e5', captured['body'])

            created['content'] = 'upsert مرحبا 日本 🚀'  # cspell:disable-line
            upserted = await container.upsert_item(created)
            self.assertEqual(upserted['content'], created['content'])

            upserted['content'] = 'replace नमस्ते 日本 🌍'  # cspell:disable-line
            replaced = await container.replace_item(doc_id, upserted)
            self.assertEqual(replaced['content'], upserted['content'])

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
            self.assertEqual(patched['content'], 'patch שלום 日本 🎊')  # cspell:disable-line

            batch_id = 'utf8-batch-async-' + str(uuid.uuid4())
            batch_result = await container.execute_item_batch(
                [(
                    'create',
                    ({'id': batch_id, 'pk': '日本', 'content': 'batch ไทย 日本 🎉'},),  # cspell:disable-line
                )],
                partition_key='日本',
            )
            self.assertEqual(batch_result[0]['statusCode'], 201)

            queried = []
            async for item in container.query_items(
                    query="SELECT * FROM c WHERE c.id = @id",
                    parameters=[{'name': '@id', 'value': doc_id}],
                    partition_key='日本'):
                queried.append(item)
            self.assertEqual(len(queried), 1)
            self.assertEqual(queried[0]['content'], patched['content'])

    async def test_default_ascii_escaping_rejects_large_cjk_item_async(self):
        """Verify the backend rejects the escaped async request body because it exceeds 2 MiB."""
        document = self._large_cjk_document('utf8-large-default-async-')
        escaped_body = json.dumps(document, separators=(",", ":")).encode("utf-8")
        self.assertGreater(len(escaped_body), 2 * 1024 * 1024)

        with self.assertRaises(exceptions.CosmosHttpResponseError) as context:
            await self.created_container.create_item(document)

        self.assertEqual(context.exception.status_code, 413)

    async def test_compact_utf8_large_cjk_item_stays_under_wire_limit_async(self):
        """Write an item that exceeds 2 MiB when escaped but not as compact UTF-8."""
        document = self._large_cjk_document('utf8-large-compact-async-')
        escaped_body = json.dumps(document, separators=(",", ":")).encode("utf-8")
        compact_body = json.dumps(
            document,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        self.assertGreater(len(escaped_body), 2 * 1024 * 1024)
        self.assertLess(len(compact_body), 2 * 1024 * 1024)

        async with test_config.TestConfig.create_data_client_async(
            enable_compact_utf8_item_writes=True
        ) as client:
            container = client.get_database_client(
                test_config.TestConfig.TEST_DATABASE_ID
            ).get_container_client(
                test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            created = await container.create_item(document)

            self.assertEqual(created['content'], document['content'])


if __name__ == "__main__":
    unittest.main()
