# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, ContainerProxy


@pytest.mark.cosmosEmulator
class TestEncoding(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    client: cosmos_client.CosmosClient = None
    key_client: cosmos_client.CosmosClient = None
    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    key_container: ContainerProxy = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        # Key-auth client for control-plane operations (e.g. stored procedures)
        cls.key_client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.key_db = cls.key_client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        cls.key_container = cls.key_db.get_container_client(
            test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)

        # AAD (or key, depending on env var) client for data-plane operations
        cls.client = test_config.TestConfig.create_data_client()
        cls.created_db = cls.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        cls.created_container = cls.created_db.get_container_client(
            test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)

    def test_unicode_characters_in_partition_key(self):
        test_string = u'€€ کلید پارتیشن विभाजन कुंजी \t123'  # cspell:disable-line
        document_definition = {'pk': test_string, 'id': 'myid' + str(uuid.uuid4())}
        created_doc = self.created_container.create_item(body=document_definition)

        read_doc = self.created_container.read_item(item=created_doc['id'], partition_key=test_string)
        self.assertEqual(read_doc['pk'], test_string)

    def test_create_document_with_line_separator_para_seperator_next_line_unicodes(self):
        test_string = u'Line Separator (\u2028) & Paragraph Separator (\u2029) & Next Line (\x85) & نیم\u200cفاصله'  # cspell:disable-line
        document_definition = {'pk': 'pk', 'id': 'myid' + str(uuid.uuid4()), 'unicode_content': test_string}
        created_doc = self.created_container.create_item(body=document_definition)

        read_doc = self.created_container.read_item(item=created_doc['id'], partition_key='pk')
        self.assertEqual(read_doc['unicode_content'], test_string)

    def test_create_stored_procedure_with_line_separator_para_seperator_next_line_unicodes(self):
        # scripts.create_stored_procedure and scripts.get_stored_procedure are control-plane.
        # operations that will return 403 under AAD Data Contributor role. This test uses key_container
        # (key-auth) for these operations.
        test_string = 'Line Separator (\u2028) & Paragraph Separator (\u2029) & Next Line (\x85) & نیم\u200cفاصله'  # cspell:disable-line

        test_string_unicode = u'Line Separator (\u2028) & Paragraph Separator (\u2029) & Next Line (\x85) & نیم\u200cفاصله'  # cspell:disable-line

        stored_proc_definition = {'id': 'myid' + str(uuid.uuid4()), 'body': test_string}
        created_sp = self.key_container.scripts.create_stored_procedure(body=stored_proc_definition)

        read_sp = self.key_container.scripts.get_stored_procedure(created_sp['id'])
        self.assertEqual(read_sp['body'], test_string_unicode)

    # Round-trip tests for documents that contain 4-byte UTF-8
    # characters (emoji). These exercise both writing and reading
    # of multi-byte content.

    def test_round_trip_emoji_document_through_full_sdk_stack(self):
        """Writes a document containing emoji, reads it back, and
        checks the read content matches the written content exactly."""
        # Mixes 2-byte (é), 3-byte (日), and 4-byte (emoji) characters.
        emoji_payload = u'celebration 🎉🎊 — café 日本 🌍'  # cspell:disable-line
        doc_id = 'emoji-rt-' + str(uuid.uuid4())
        document = {
            'pk': 'pk',
            'id': doc_id,
            'multibyte_content': emoji_payload,
        }

        created = self.created_container.create_item(body=document)
        # Sanity check on the write response itself.
        self.assertEqual(created['multibyte_content'], emoji_payload)

        read = self.created_container.read_item(item=doc_id, partition_key='pk')
        self.assertEqual(read['multibyte_content'], emoji_payload)
        # Also compare the raw UTF-8 bytes to be sure nothing changed.
        self.assertEqual(
            read['multibyte_content'].encode('utf-8'),
            emoji_payload.encode('utf-8'),
        )

    def test_round_trip_emoji_document_via_query(self):
        """Same content as the test above, but pulled back via a SQL
        query instead of a point read."""
        emoji_payload = u'query 🎉 — café 日本'  # cspell:disable-line
        doc_id = 'emoji-q-' + str(uuid.uuid4())
        document = {
            'pk': 'pk',
            'id': doc_id,
            'multibyte_content': emoji_payload,
        }
        self.created_container.create_item(body=document)

        results = list(self.created_container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": doc_id}],
            partition_key='pk',
        ))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['multibyte_content'], emoji_payload)


if __name__ == "__main__":
    unittest.main()
