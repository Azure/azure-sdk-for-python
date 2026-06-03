# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async versions of the encoding round-trip tests. Same checks as
the sync file, but using the async client."""
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

