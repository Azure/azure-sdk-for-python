# -*- coding: utf-8 -*-

import unittest
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey, ContainerProxy


class EncodingTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy
    TEST_DATABASE_ID = "Python SDK Test Database " + str(uuid.uuid4())
    TEST_CONTAINER_ID = "Multi Partition Test Collection With Custom PK " + str(uuid.uuid4())
    client: cosmos_client.CosmosClient = None
    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, connection_policy=cls.connectionPolicy)
        cls.created_db = cls.client.create_database(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_db.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey("/pk"),
            offer_throughput=test_config._test_config.THROUGHPUT_FOR_5_PARTITIONS)

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_database(cls.TEST_DATABASE_ID)

    def test_unicode_characters_in_partition_key(self):
        test_string = u'€€ کلید پارتیشن विभाजन कुंजी 	123'  # cspell:disable-line
        document_definition = {'pk': test_string, 'id': 'myid' + str(uuid.uuid4())}
        created_doc = self.created_container.create_item(body=document_definition)

        read_doc = self.created_container.read_item(item=created_doc['id'], partition_key=test_string)
        self.assertEqual(read_doc['pk'], test_string)

    def test_create_document_with_line_separator_para_seperator_next_line_unicodes(self):
        test_string = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'  # cspell:disable-line
        document_definition = {'pk': 'pk', 'id': 'myid' + str(uuid.uuid4()), 'unicode_content': test_string}
        created_doc = self.created_container.create_item(body=document_definition)

        read_doc = self.created_container.read_item(item=created_doc['id'], partition_key='pk')
        self.assertEqual(read_doc['unicode_content'], test_string)

    def test_create_stored_procedure_with_line_separator_para_seperator_next_line_unicodes(self):
        test_string = 'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'  # cspell:disable-line

        test_string_unicode = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'  # cspell:disable-line

        stored_proc_definition = {'id': 'myid' + str(uuid.uuid4()), 'body': test_string}
        created_sp = self.created_container.scripts.create_stored_procedure(body=stored_proc_definition)

        read_sp = self.created_container.scripts.get_stored_procedure(created_sp['id'])
        self.assertEqual(read_sp['body'], test_string_unicode)


if __name__ == "__main__":
    unittest.main()
