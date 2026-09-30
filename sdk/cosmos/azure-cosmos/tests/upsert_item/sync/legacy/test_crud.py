# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preserve test_document_upsert with an owned Rust fixture and stored-data checks."""

import os
from types import SimpleNamespace
import unittest
import uuid

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey, exceptions


class TestCRUDOperations(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_upsert_crud_" + uuid.uuid4().hex
        self.databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)
        self.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="orders")
        self.databaseForTest.create_container(id="orders", partition_key=PartitionKey(path="/pk"))

    def test_document_upsert(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_document_upsert
        created_db = self.databaseForTest
        created_collection = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        documents = list(created_collection.read_all_items())
        before_create_documents_count = len(documents)
        document_definition = {'id': 'doc',
                               'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'pk',
                               'key': 'value'}
        created_document = created_collection.upsert_item(body=document_definition)
        self.assertEqual(created_document['id'], document_definition['id'])
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            created_collection.upsert_item(body=document_definition)
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')
        stored_document = created_collection.read_item(item='doc', partition_key='pk')
        self.assertEqual(
            {key: stored_document[key] for key in ('id', 'name', 'spam', 'pk', 'key')},
            {'id': 'doc', 'name': 'sample document', 'spam': 'eggs', 'pk': 'pk', 'key': 'value'})
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        upserted_document = created_collection.upsert_item(body=created_document)
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document name property should change')
        self.assertEqual(upserted_document['spam'],
                         created_document['spam'],
                         'property should have changed')
        self.assertEqual(upserted_document['id'],
                         created_document['id'],
                         'document id should stay the same')
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')
        stored_document = created_collection.read_item(item='doc', partition_key='pk')
        self.assertEqual(
            {key: stored_document[key] for key in ('id', 'name', 'spam', 'pk', 'key')},
            {'id': 'doc', 'name': 'replaced document', 'spam': 'not eggs', 'pk': 'pk', 'key': 'value'})
        created_document['id'] = 'new id'
        new_document = created_collection.upsert_item(body=created_document)
        created_document['spam'] = 'more eggs'
        created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        created_collection.delete_item(item=new_document, partition_key=new_document['pk'])
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')
