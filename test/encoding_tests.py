# -*- coding: utf-8 -*-

import unittest
import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import test.test_config as test_config

class EncodingTest(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    testDbName = 'testDatabase'
    testCollectionName = 'testCollection'

    @classmethod
    def cleanUpTestDatabase(cls):
        global client
        client = document_client.DocumentClient(cls.host,
                                                {'masterKey': cls.masterKey})
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.testDbName + '\'')
        it = iter(query_iterable)

        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    @classmethod
    def tearDownClass(cls):
        EncodingTest.cleanUpTestDatabase()

    def setUp(self):
        global created_collection

        EncodingTest.cleanUpTestDatabase()
        created_db = client.CreateDatabase({ 'id': self.testDbName })

        collection_definition = { 'id': self.testCollectionName, 'partitionKey': {'paths': ['/pk'],'kind': 'Hash'} }
        collection_options = { 'offerThroughput': 10100 }
        created_collection = client.CreateCollection(created_db['_self'], collection_definition, collection_options)

    def test_unicode_characters_in_partition_key (self):
        test_string = u'€€ کلید پارتیشن विभाजन कुंजी 	123'
        document_definition = {'pk': test_string, 'id':'myid'}
        created_doc = client.CreateDocument(created_collection['_self'], document_definition)

        read_options = {'partitionKey': test_string }
        read_doc = client.ReadDocument(created_doc['_self'], read_options)
        self.assertEqual(read_doc['pk'], test_string)

    def test_create_document_with_line_separator_para_seperator_next_line_unicodes (self):

        test_string = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'
        document_definition = {'pk': 'pk', 'id':'myid', 'unicode_content':test_string }
        created_doc = client.CreateDocument(created_collection['_self'], document_definition)

        read_options = {'partitionKey': 'pk' }
        read_doc = client.ReadDocument(created_doc['_self'], read_options)
        self.assertEqual(read_doc['unicode_content'], test_string)

    def test_create_stored_procedure_with_line_separator_para_seperator_next_line_unicodes (self):

        test_string = 'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'

        test_string_unicode = u'Line Separator ( ) & Paragraph Separator ( ) & Next Line () & نیم‌فاصله'

        stored_proc_definition = {'id':'myid', 'body': test_string}
        created_sp = client.CreateStoredProcedure(created_collection['_self'], stored_proc_definition)

        read_sp = client.ReadStoredProcedure(created_sp['_self'], dict())
        self.assertEqual(read_sp['body'], test_string_unicode)
if __name__ == '__main__':
    unittest.main()
