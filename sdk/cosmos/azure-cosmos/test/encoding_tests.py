# -*- coding: utf-8 -*-

import unittest
import uuid
import pytest
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class EncodingTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.created_collection = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(cls.client)


    def test_unicode_characters_in_partition_key (self):
        test_string = u'€€ کلید پارتیشن विभाजन कुंजी 	123'
        document_definition = {'pk': test_string, 'id':'myid' + str(uuid.uuid4())}
        created_doc = self.client.CreateItem(self.created_collection['_self'], document_definition)

        read_options = {'partitionKey': test_string }
        read_doc = self.client.ReadItem(created_doc['_self'], read_options)
        self.assertEqual(read_doc['pk'], test_string)

    def test_create_document_with_line_separator_para_seperator_next_line_unicodes (self):

        test_string = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'
        document_definition = {'pk': 'pk', 'id':'myid' + str(uuid.uuid4()), 'unicode_content':test_string }
        created_doc = self.client.CreateItem(self.created_collection['_self'], document_definition)

        read_options = {'partitionKey': 'pk' }
        read_doc = self.client.ReadItem(created_doc['_self'], read_options)
        self.assertEqual(read_doc['unicode_content'], test_string)

    def test_create_stored_procedure_with_line_separator_para_seperator_next_line_unicodes (self):

        test_string = 'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'

        test_string_unicode = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'

        stored_proc_definition = {'id':'myid' + str(uuid.uuid4()), 'body': test_string}
        created_sp = self.client.CreateStoredProcedure(self.created_collection['_self'], stored_proc_definition)

        read_sp = self.client.ReadStoredProcedure(created_sp['_self'], dict())
        self.assertEqual(read_sp['body'], test_string_unicode)
if __name__ == '__main__':
    unittest.main()
