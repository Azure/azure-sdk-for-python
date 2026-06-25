# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async data-plane versions of the encoding round-trip tests.

This mirrors the sync document/partition-key checks and emoji round-trips
using the async client. The stored-procedure control-plane check remains in
the sync file because it relies on key-auth script operations.
"""
import unittest
import uuid

import pytest

import test_config


@pytest.mark.cosmosEmulator
class TestEncodingAsync(unittest.IsolatedAsyncioTestCase):
    """Async round-trips for non-ASCII document content."""

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

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


if __name__ == "__main__":
    unittest.main()
