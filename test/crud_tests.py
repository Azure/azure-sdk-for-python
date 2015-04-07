# Copyright (c) Microsoft Corporation.  All rights reserved.

"""End to end test.
"""

import logging
import unittest

import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants


# localhost
masterKey = '[YOUR_KEY_HERE]'
host = '[YOUR_ENDPOINT_HERE]'


class CRUDTests(unittest.TestCase):
    """Python CRUD Tests.
    """

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except errors.HTTPFailure as inst:
            self.assertEqual(inst.status_code, status_code)

    def setUp(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        databases = list(client.ReadDatabases())
        if not databases:
            return
        for database in databases:
            client.DeleteDatabase(database['_self'])

    def test_database_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # read databases.
        databases = list(client.ReadDatabases())
        # create a database.
        before_create_databases_count = len(databases)
        database_definition = { 'id': 'sample database' }
        created_db = client.CreateDatabase(database_definition)
        self.assertEqual(created_db['id'], database_definition['id'])
        # Read databases after creation.
        databases = list(client.ReadDatabases())
        self.assertEqual(len(databases),
                         before_create_databases_count + 1,
                         'create should increase the number of databases')
        # query databases.
        databases = list(client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                { 'name':'@id', 'value': database_definition['id'] }
            ]
        }))
        self.assert_(databases,
                     'number of results for the query should be > 0')

		# read database.
        one_db_from_read = client.ReadDatabase(created_db['_self'])

        # delete database.
        client.DeleteDatabase(created_db['_self'])
        # read database after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadDatabase,
                                           created_db['_self'])

    def test_sql_query_crud(self):
        client = document_client.DocumentClient(host, {'masterKey': masterKey})
        # create two databases.
        client.CreateDatabase({ 'id': 'database 1' })
        client.CreateDatabase({ 'id': 'database 2' })
        # query with parameters.
        databases = list(client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                { 'name':'@id', 'value': 'database 1' }
            ]
        }))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

        # query without parameters.
        databases = list(client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id="database non-existing"'
        }))
        self.assertEqual(0, len(databases), 'Unexpected number of query results.')

        # query with a string.
        databases = list(client.QueryDatabases('SELECT * FROM root r WHERE r.id="database 2"'))
        self.assertEqual(1, len(databases), 'Unexpected number of query results.')

    def test_collection_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        created_db = client.CreateDatabase({ 'id': 'sample database' })
        collections = list(client.ReadCollections(created_db['_self']))
        # create a collection
        before_create_collections_count = len(collections)
        collection_definition = { 'id': 'sample collection' }
        created_collection = client.CreateCollection(created_db['_self'],
                                                     collection_definition)
        self.assertEqual(created_collection['id'],
                         collection_definition['id'])
        # read collections after creation
        collections = list(client.ReadCollections(created_db['_self']))
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')
        # query collections
        collections = list(client.QueryCollections(
            created_db['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value': collection_definition['id'] }
                ]
            }))
        self.assert_(collections)
        # delete collection
        client.DeleteCollection(created_collection['_self'])
        # read collection after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadCollection,
                                           created_collection['_self'])

    def test_document_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        created_db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        created_collection = client.CreateCollection(
            created_db['_self'],
            { 'id': 'sample collection' })
        # read documents
        documents = list(client.ReadDocuments(
            created_collection['_self']))
        # create a document
        before_create_documents_count = len(documents)
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value'}
        # Should throw an error because automatic id generation is disabled.
        self.__AssertHTTPFailureWithStatus(
            400,
            client.CreateDocument,
            created_collection['_self'],
            document_definition,
            {'disableAutomaticIdGeneration': True})

        created_document = client.CreateDocument(
            created_collection['_self'],
            document_definition)
        self.assertEqual(created_document['name'],
                         document_definition['name'])
        self.assertTrue(created_document['id'] != None)
        # duplicated documents are allowed when 'id' is not provided.
        duplicated_document = client.CreateDocument(
            created_collection['_self'],
            document_definition)
        self.assertEqual(duplicated_document['name'],
                         document_definition['name'])
        self.assert_(duplicated_document['id'])
        self.assertNotEqual(duplicated_document['id'],
                            created_document['id'])
        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        duplicated_definition_with_id['id'] = created_document['id']
        self.__AssertHTTPFailureWithStatus(409,
                                           client.CreateDocument,
                                           created_collection['_self'],
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(client.ReadDocuments(
            created_collection['_self']))
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'create should increase the number of documents')
        # query documents
        documents = list(client.QueryDocuments(
            created_collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    { 'name':'@name', 'value':document_definition['name'] }
                ]
            }))
        self.assert_(documents)
        documents = list(client.QueryDocuments(
            created_collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    { 'name':'@name', 'value':document_definition['name'] }
                ]
            },
            { 'enableScanInQuery': True}))
        self.assert_(documents)
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        replaced_document = client.ReplaceDocument(
            created_document['_self'],
            created_document)
        self.assertEqual(replaced_document['name'],
                         'replaced document',
                         'document id property should change')
        self.assertEqual(replaced_document['spam'],
                         'not eggs',
                         'property should have changed')
        self.assertEqual(created_document['id'],
                         replaced_document['id'],
                         'document id should stay the same')
        # read document
        one_document_from_read = client.ReadDocument(
            replaced_document['_self'])
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        client.DeleteDocument(replaced_document['_self'])
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadDocument,
                                           replaced_document['_self'])

    def test_attachment_crud(self):
        class ReadableStream(object):
            """Customized file-like stream.
            """

            def __init__(self, chunks = ['first chunk ', 'second chunk']):
                """Initialization.

                :Parameters:
                    - `chunks`: list

                """
                self._chunks = list(chunks)

            def read(self, n=-1):
                """Simulates the read method in a file stream.

                :Parameters:
                    - `n`: int

                :Returns:
                    str

                """
                if self._chunks:
                    return self._chunks.pop(0)
                else:
                    return ''

            def __len__(self):
                """To make len(ReadableStream) work.
                """
                return sum([len(chunk) for chunk in self._chunks])


        # Should do attachment CRUD operations successfully
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'],
            { 'id': 'sample collection' })
        # create document
        document = client.CreateDocument(collection['_self'],
                                         { 'id': 'sample document',
                                           'spam': 'eggs',
                                           'key': 'value' })
        # list all attachments
        attachments = list(client.ReadAttachments(document['_self']))
        initial_count = len(attachments)
        valid_media_options = { 'slug': 'attachment name',
                                'contentType': 'application/text' }
        invalid_media_options = { 'slug': 'attachment name',
                                  'contentType': 'junt/test' }
        # create attachment with invalid content-type
        content_stream = ReadableStream()
        self.__AssertHTTPFailureWithStatus(
            400,
            client.CreateAttachmentAndUploadMedia,
            document['_self'],
            content_stream,
            invalid_media_options)
        content_stream = ReadableStream()
        # create streamed attachment with valid content-type
        valid_attachment = client.CreateAttachmentAndUploadMedia(
            document['_self'], content_stream, valid_media_options)
        self.assertEqual(valid_attachment['id'],
                         'attachment name',
                         'id of created attachment should be the'
                         ' same as the one in the request')
        content_stream = ReadableStream()
        # create colliding attachment
        self.__AssertHTTPFailureWithStatus(
            409,
            client.CreateAttachmentAndUploadMedia,
            document['_self'],
            content_stream,
            valid_media_options)

        content_stream = ReadableStream()
        # create attachment with media link
        dynamic_attachment = {
            'id': 'dynamic attachment',
            'media': 'http://xstore.',
            'MediaType': 'Book',
            'Author':'My Book Author',
            'Title':'My Book Title',
            'contentType':'application/text'
        }
        attachment = client.CreateAttachment(document['_self'],
                                             dynamic_attachment)
        self.assertEqual(attachment['MediaType'],
                         'Book',
                         'invalid media type')
        self.assertEqual(attachment['Author'],
                         'My Book Author',
                         'invalid property value')
        # list all attachments
        attachments = list(client.ReadAttachments(document['_self']))
        self.assertEqual(len(attachments),
                         initial_count + 2,
                         'number of attachments should\'ve increased by 2')
        attachment['Author'] = 'new author'
        # replace the attachment
        client.ReplaceAttachment(attachment['_self'], attachment)
        self.assertEqual(attachment['MediaType'],
                         'Book',
                         'invalid media type')
        self.assertEqual(attachment['Author'],
                         'new author',
                         'invalid property value')
        # read attachment media
        media_response = client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response,
                         'first chunk second chunk')
        content_stream = ReadableStream(['modified first chunk ',
                                         'modified second chunk'])
        # update attachment media
        client.UpdateMedia(valid_attachment['media'],
                           content_stream,
                           valid_media_options)
        # read attachment media after update
        # read media buffered
        media_response = client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response,
                         'modified first chunk modified second chunk')
        # read media streamed
        client.connection_policy.MediaReadMode = (
            documents.MediaReadMode.Streamed)
        media_response = client.ReadMedia(valid_attachment['media'])
        self.assertEqual(media_response.read(),
                         'modified first chunk modified second chunk')
        # share attachment with a second document
        document = client.CreateDocument(collection['_self'],
                                         {'id': 'document 2'})
        second_attachment = {
            'id': valid_attachment['id'],
            'contentType': valid_attachment['contentType'],
            'media': valid_attachment['media'] }
        attachment = client.CreateAttachment(document['_self'],
                                             second_attachment)
        self.assertEqual(valid_attachment['id'],
                         attachment['id'],
                         'id mismatch')
        self.assertEqual(valid_attachment['media'],
                         attachment['media'],
                         'media mismatch')
        self.assertEqual(valid_attachment['contentType'],
                         attachment['contentType'],
                         'contentType mismatch')
        # deleting attachment
        client.DeleteAttachment(attachment['_self'])
        # read attachments after deletion
        attachments = list(client.ReadAttachments(document['_self']))
        self.assertEqual(len(attachments), 0)

    def test_user_crud(self):
        # Should do User CRUD operations successfully.
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # list users
        users = list(client.ReadUsers(db['_self']))
        before_create_count = len(users)
        # create user
        user = client.CreateUser(db['_self'], { 'id': 'new user' })
        self.assertEqual(user['id'], 'new user', 'user id error')
        # list users after creation
        users = list(client.ReadUsers(db['_self']))
        self.assertEqual(len(users), before_create_count + 1)
        # query users
        results = list(client.QueryUsers(
            db['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value':'new user' }
                ]
            }))
        self.assert_(results)

        # replace user
        user['id'] = 'replaced user'
        replaced_user = client.ReplaceUser(user['_self'], user)
        self.assertEqual(replaced_user['id'],
                         'replaced user',
                         'user id should change')
        self.assertEqual(user['id'],
                         replaced_user['id'],
                         'user id should stay the same')
        # read user
        user = client.ReadUser(replaced_user['_self'])
        self.assertEqual(replaced_user['id'], user['id'])
        # delete user
        client.DeleteUser(user['_self'])
        # read user after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadUser,
                                           user['_self'])

    def test_permission_crud(self):
        # Should do Permission CRUD operations successfully
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create user
        user = client.CreateUser(db['_self'], { 'id': 'new user' })
        # list permissions
        permissions = list(client.ReadPermissions(user['_self']))
        before_create_count = len(permissions)
        permission = {
            'id': 'new permission',
            'permissionMode': documents.PermissionMode.Read,
            'resource': 'dbs/AQAAAA==/colls/AQAAAJ0fgTc='  # A random one.
        }
        # create permission
        permission = client.CreatePermission(user['_self'], permission)
        self.assertEqual(permission['id'],
                         'new permission',
                         'permission id error')
        # list permissions after creation
        permissions = list(client.ReadPermissions(user['_self']))
        self.assertEqual(len(permissions), before_create_count + 1)
        # query permissions
        results = list(client.QueryPermissions(
            user['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value':permission['id'] }
                ]
            }))
        self.assert_(results)

        # replace permission 
        permission['id'] = 'replaced permission'
        replaced_permission = client.ReplacePermission(permission['_self'],
                                                       permission)
        self.assertEqual(replaced_permission['id'],
                         'replaced permission',
                         'permission id should change')
        self.assertEqual(permission['id'],
                         replaced_permission['id'],
                         'permission id should stay the same')
        # read permission
        permission = client.ReadPermission(replaced_permission['_self'])
        self.assertEqual(replaced_permission['id'], permission['id'])
        # delete permission
        client.DeletePermission(replaced_permission['_self'])
        # read permission after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadPermission,
                                           permission['_self'])

    def test_authorization(self):
        def __SetupEntities(client):
            """Sets up entities for this test.

            :Parameters:
                - `client`: document_client.DocumentClient

            :Returns:
                dict

            """
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection1
            collection1 = client.CreateCollection(
                db['_self'], { 'id': 'sample collection' })
            # create document1
            document1 = client.CreateDocument(collection1['_self'],
                                              { 'id': 'coll1doc1',
                                                'spam': 'eggs',
                                                'key': 'value' })
            # create document 2
            document2 = client.CreateDocument(
                collection1['_self'],
                { 'id': 'coll1doc2', 'spam': 'eggs2', 'key': 'value2' })
            # create attachment
            dynamic_attachment = {
                'id': 'dynamic attachment',
                'media': 'http://xstore.',
                'MediaType': 'Book',
                'Author': 'My Book Author',
                'Title': 'My Book Title',
                'contentType': 'application/text'
            }
            attachment = client.CreateAttachment(document1['_self'],
                                                 dynamic_attachment)
            # create collection 2
            collection2 = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection2' })
            # create user1
            user1 = client.CreateUser(db['_self'], { 'id': 'user1' })
            permission = {
                'id': 'permission On Coll1',
                'permissionMode': documents.PermissionMode.Read,
                'resource': collection1['_self']
            }
            # create permission for collection1 
            permission_on_coll1 = client.CreatePermission(user1['_self'],
                                                          permission)
            self.assertTrue(permission_on_coll1['_token'] != None,
                            'permission token is invalid')
            permission = {
                'id': 'permission On Doc1',
                'permissionMode': documents.PermissionMode.All,
                'resource': document2['_self']
            }
            # create permission for document 2
            permission_on_doc2 = client.CreatePermission(user1['_self'],
                                                         permission)
            self.assertTrue(permission_on_doc2['_token'] != None,
                            'permission token is invalid')
            # create user 2
            user2 = client.CreateUser(db['_self'], { 'id': 'user2' })
            permission = {
                'id': 'permission On coll2',
                'permissionMode': documents.PermissionMode.All,
                'resource': collection2['_self']
            }
            # create permission on collection 2
            permission_on_coll2 = client.CreatePermission(
                user2['_self'], permission)
            entities = {
                'db': db,
                'coll1': collection1,
                'coll2': collection2,
                'doc1': document1,
                'doc2': document2,
                'user1': user1,
                'user2': user2,
                'attachment': attachment,
                'permissionOnColl1': permission_on_coll1,
                'permissionOnDoc2': permission_on_doc2,
                'permissionOnColl2': permission_on_coll2
            }
            return entities

        # Client without any authorization will fail.
        client = document_client.DocumentClient(host, {})
        self.__AssertHTTPFailureWithStatus(401,
                                           list,
                                           client.ReadDatabases())
        # Client with master key.
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # setup entities
        entities = __SetupEntities(client)
        resource_tokens = {}
        resource_tokens[entities['coll1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        resource_tokens[entities['doc1']['_rid']] = (
            entities['permissionOnColl1']['_token'])
        col1_client = document_client.DocumentClient(
            host, {'resourceTokens': resource_tokens})
        # 1. Success-- Use Col1 Permission to Read
        success_coll1 = col1_client.ReadCollection(
            entities['coll1']['_self'])
        # 2. Failure-- Use Col1 Permission to delete
        self.__AssertHTTPFailureWithStatus(403,
                                           col1_client.DeleteCollection,
                                           success_coll1['_self'])
        # 3. Success-- Use Col1 Permission to Read All Docs
        success_documents = list(col1_client.ReadDocuments(
            success_coll1['_self']))
        self.assertTrue(success_documents != None,
                        'error reading documents')
        self.assertEqual(len(success_documents),
                         2,
                         'Expected 2 Documents to be succesfully read')
        # 4. Success-- Use Col1 Permission to Read Col1Doc1
        success_doc = col1_client.ReadDocument(entities['doc1']['_self'])
        self.assertTrue(success_doc != None, 'error reading document')
        self.assertEqual(
            success_doc['id'],
            entities['doc1']['id'],
            'Expected to read children using parent permissions')
        col2_client = document_client.DocumentClient(
            host,
            { 'permissionFeed': [ entities['permissionOnColl2'] ] })
        doc = {
            'id': 'new doc',
            'CustomProperty1': 'BBBBBB',
            'customProperty2': 1000,
            'id': entities['doc2']['id']
        }
        success_doc = col2_client.CreateDocument(
            entities['coll2']['_self'], doc)
        self.assertTrue(success_doc != None, 'error creating document')
        self.assertEqual(success_doc['CustomProperty1'],
                         doc['CustomProperty1'],
                         'document should have been created successfully')

    def test_trigger_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'],
            { 'id': 'sample collection' })
        # read triggers
        triggers = list(client.ReadTriggers(collection['_self']))
        # create a trigger
        before_create_triggers_count = len(triggers)
        trigger_definition = {
            'id': 'sample trigger',
            'serverScript': 'function() {var x = 10;}',
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }
        trigger = client.CreateTrigger(collection['_self'],
                                       trigger_definition)
        for property in trigger_definition:
            if property != "serverScript":
                self.assertEqual(
                    trigger[property],
                    trigger_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                    self.assertEqual(trigger['body'],
                                     'function() {var x = 10;}')

        # read triggers after creation
        triggers = list(client.ReadTriggers(collection['_self']))
        self.assertEqual(len(triggers),
                         before_create_triggers_count + 1,
                         'create should increase the number of triggers')
        # query triggers
        triggers = list(client.QueryTriggers(
            collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name': '@id', 'value': trigger_definition['id']}
                ]
            }))
        self.assert_(triggers)

        results = list(client.QueryTriggers(
            collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name': '@id', 'value':trigger_definition['id'] }
                ]
            }))
        self.assert_(results)

        # replace trigger
        trigger['body'] = 'function() {var x = 20;}'
        replaced_trigger = client.ReplaceTrigger(trigger['_self'], trigger)
        for property in trigger_definition:
            if property != "serverScript":
                self.assertEqual(
                    replaced_trigger[property],
                    trigger[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(replaced_trigger['body'],
                                 'function() {var x = 20;}')

        # read trigger
        trigger = client.ReadTrigger(replaced_trigger['_self'])
        self.assertEqual(replaced_trigger['id'], trigger['id'])
        # delete trigger
        res = client.DeleteTrigger(replaced_trigger['_self'])
        # read triggers after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadTrigger,
                                           replaced_trigger['_self'])

    def test_udf_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'],
            { 'id': 'sample collection' })
        # read udfs
        udfs = list(client.ReadUserDefinedFunctions(collection['_self']))
        # create a udf
        before_create_udfs_count = len(udfs)
        udf_definition = {
            'id': 'sample udf',
            'body': 'function() {var x = 10;}'
        }
        udf = client.CreateUserDefinedFunction(collection['_self'],
                                               udf_definition)
        for property in udf_definition:
                self.assertEqual(
                    udf[property],
                    udf_definition[property],
                    'property {property} should match'.format(property=property))
                            
        # read udfs after creation
        udfs = list(client.ReadUserDefinedFunctions(collection['_self']))
        self.assertEqual(len(udfs),
                         before_create_udfs_count + 1,
                         'create should increase the number of udfs')
        # query udfs
        results = list(client.QueryUserDefinedFunctions(
            collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name':'@id', 'value':udf_definition['id']}
                ]
            }))
        self.assert_(results)
        # replace udf
        udf['body'] = 'function() {var x = 20;}'
        replaced_udf = client.ReplaceUserDefinedFunction(udf['_self'], udf)
        for property in udf_definition:
                self.assertEqual(
                    replaced_udf[property],
                    udf[property],
                    'property {property} should match'.format(property=property))
        # read udf
        udf = client.ReadUserDefinedFunction(replaced_udf['_self'])
        self.assertEqual(replaced_udf['id'], udf['id'])
        # delete udf
        res = client.DeleteUserDefinedFunction(replaced_udf['_self'])
        # read udfs after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadUserDefinedFunction,
                                           replaced_udf['_self'])

    def test_sproc_crud(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'],
            { 'id': 'sample collection' })
        # read sprocs
        sprocs = list(client.ReadStoredProcedures(collection['_self']))
        # create a sproc
        before_create_sprocs_count = len(sprocs)
        sproc_definition = {
            'id': 'sample sproc',
            'serverScript': 'function() {var x = 10;}'
        }
        sproc = client.CreateStoredProcedure(collection['_self'],
                                             sproc_definition)
        for property in sproc_definition:
            if property != "serverScript":
                self.assertEqual(
                    sproc[property],
                    sproc_definition[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(sproc['body'], 'function() {var x = 10;}')
                            
        # read sprocs after creation
        sprocs = list(client.ReadStoredProcedures(collection['_self']))
        self.assertEqual(len(sprocs),
                         before_create_sprocs_count + 1,
                         'create should increase the number of sprocs')
        # query sprocs
        sprocs = list(client.QueryStoredProcedures(
            collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters':[
                    { 'name':'@id', 'value':sproc_definition['id'] }
                ]
            }))
        self.assert_(sprocs)
        # replace sproc
        sproc['body'] = 'function() {var x = 20;}'
        replaced_sproc = client.ReplaceStoredProcedure(sproc['_self'],
                                                       sproc)
        for property in sproc_definition:
            if property != 'serverScript':
                self.assertEqual(
                    replaced_sproc[property],
                    sproc[property],
                    'property {property} should match'.format(property=property))
            else:
                self.assertEqual(replaced_sproc['body'],
                                 "function() {var x = 20;}")
        # read sproc
        sproc = client.ReadStoredProcedure(replaced_sproc['_self'])
        self.assertEqual(replaced_sproc['id'], sproc['id'])
        # delete sproc
        res = client.DeleteStoredProcedure(replaced_sproc['_self'])
        # read sprocs after deletion
        self.__AssertHTTPFailureWithStatus(404,
                                           client.ReadStoredProcedure,
                                           replaced_sproc['_self'])

    def test_collection_indexing_policy(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'],
            { 'id': "sample collection" })
        self.assertEqual(collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'default indexing mode should be consistent')
        lazy_collection_definition = {
            'id': 'lazy collection',
            'indexingPolicy': {
                'indexingMode': documents.IndexingMode.Lazy
            }
        }
        coll = client.DeleteCollection(collection['_self'])
        lazy_collection = client.CreateCollection(
            db['_self'],
            lazy_collection_definition)
        self.assertEqual(lazy_collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Lazy,
                         'indexing mode should be lazy')

        consistent_collection_definition = {
            'id': 'lazy collection',
            'indexingPolicy': {
                'indexingMode': documents.IndexingMode.Consistent
            }
        }
        coll = client.DeleteCollection(lazy_collection['_self'])
        consistent_collection = client.CreateCollection(
            db['_self'], consistent_collection_definition)
        self.assertEqual(collection['indexingPolicy']['indexingMode'],
                         documents.IndexingMode.Consistent,
                         'indexing mode should be consistent')
        collection_definition = {
            'id': 'CollectionWithIndexingPolicy',
            'indexingPolicy': {
                'automatic': True,
                'indexingMode': 'Lazy',
                'IncludedPaths': [
                    {
                        'IndexType': 'Hash',
                        'Path': '/'
                    }
                ],
                'ExcludedPaths': [
                    '/"systemMetadata"/*'
                ]
            }
        }
        client.DeleteCollection(consistent_collection['_self'])
        collectio_with_indexing_policy = client.CreateCollection(
            db['_self'], collection_definition)
        self.assertEqual(2,
                         len(collectio_with_indexing_policy[
                             'indexingPolicy']['IncludedPaths']),
                         'Unexpected includedPaths length')
        self.assertEqual(1,
                         len(collectio_with_indexing_policy[
                             'indexingPolicy']['ExcludedPaths']),
                         'Unexpected excluded path count')

    def test_client_request_timeout(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 1 ms to make sure it will throw
        connection_policy.RequestTimeout = 1
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey},
                                                connection_policy)
        # create database
        with self.assertRaises(Exception):
            # Will time out.
            client.CreateDatabase({ 'id': "sample database" })

    def test_query_iterable_functionality(self):
        def __CreateResources(client):
            """Creates resources for this test.

            :Parameters:
                - `client`: document_client.DocumentClient

            :Returns:
                dict

            """
            db = client.CreateDatabase({ 'id': 'sample database' })
            collection = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection' })
            doc1 = client.CreateDocument(
                collection['_self'],
                { 'id': 'doc1', 'prop1': 'value1'})
            doc2 = client.CreateDocument(
                collection['_self'],
                { 'id': 'doc2', 'prop1': 'value2'})
            doc3 = client.CreateDocument(
                collection['_self'],
                { 'id': 'doc3', 'prop1': 'value3'})
            resources = {
                'coll': collection,
                'doc1': doc1,
                'doc2': doc2,
                'doc3': doc3
            }
            return resources

        # Validate QueryIterable by converting it to a list.
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        resources = __CreateResources(client)
        results = client.ReadDocuments(resources['coll']['_self'],
                                       {'maxItemCount':2})
        docs = list(iter(results))
        self.assertEqual(3,
                         len(docs),
                         'QueryIterable should return all documents' +
                         ' using continuation')
        self.assertEqual(resources['doc1']['id'], docs[0]['id'])
        self.assertEqual(resources['doc2']['id'], docs[1]['id'])
        self.assertEqual(resources['doc3']['id'], docs[2]['id'])

        # Validate QueryIterable iterator with 'for'.
        counter = 0
        # test QueryIterable with 'for'.
        for doc in iter(results):
            counter += 1
            if counter == 1:
                self.assertEqual(resources['doc1']['id'],
                                 doc['id'],
                                 'first document should be doc1')
            elif counter == 2:
                self.assertEqual(resources['doc2']['id'],
                                 doc['id'],
                                 'second document should be doc2')
            elif counter == 3:
                self.assertEqual(resources['doc3']['id'],
                                 doc['id'],
                                 'third document should be doc3')
        self.assertEqual(counter, 3)

        # Get query results page by page.
        results = client.ReadDocuments(resources['coll']['_self'],
                                       {'maxItemCount':2})
        first_block = results.fetch_next_block()
        self.assertEqual(2,
                         len(first_block),
                         'First block should have 2 entries.')
        self.assertEqual(resources['doc1']['id'], first_block[0]['id'])
        self.assertEqual(resources['doc2']['id'], first_block[1]['id'])
        self.assertEqual(1,
                         len(results.fetch_next_block()),
                         'Second block should have 1 entry.')
        self.assertEqual(0,
                         len(results.fetch_next_block()),
                         'Then its empty.')

    def test_trigger_functionality(self):
        triggers_in_collection1 = [
        {
            'id': 't1',
            'body': (
                'function() {' +
                '    var item = getContext().getRequest().getBody();' +
                '    item.id = item.id.toUpperCase() + \'t1\';' +
                '    getContext().getRequest().setBody(item);' +
                '}'),
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        },
        {
            'id': 'response1',
            'body': (
                'function() {' +
                '    var prebody = getContext().getRequest().getBody();' +
                '    if (prebody.id != \'TESTING POST TRIGGERt1\')'
                '        throw \'id mismatch\';' +
                '    var postbody = getContext().getResponse().getBody();' +
                '    if (postbody.id != \'TESTING POST TRIGGERt1\')'
                '        throw \'id mismatch\';'
                '}'),
            'triggerType': documents.TriggerType.Post,
            'triggerOperation': documents.TriggerOperation.All
        },
        {
            'id': 'response2',
            # can't be used because setValue is currently disabled
            'body': (
                'function() {' +
                '    var predoc = getContext().getRequest().getBody();' +
                '    var postdoc = getContext().getResponse().getBody();' +
                '    getContext().getResponse().setValue(' +
                '        \'predocname\', predoc.id + \'response2\');' +
                '    getContext().getResponse().setValue(' +
                '        \'postdocname\', postdoc.id + \'response2\');' +
                '}'),
                'triggerType': documents.TriggerType.Post,
                'triggerOperation': documents.TriggerOperation.All,
        }]
        triggers_in_collection2 = [
        {
            'id': "t2",
            'body': "function() { }", # trigger already stringified
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        },
        {
            'id': "t3",
            'body': (
                'function() {' +
                '    var item = getContext().getRequest().getBody();' +
                '    item.id = item.id.toLowerCase() + \'t3\';' +
                '    getContext().getRequest().setBody(item);' +
                '}'),
            'triggerType': documents.TriggerType.Pre,
            'triggerOperation': documents.TriggerOperation.All
        }]
        triggers_in_collection3 = [
        {
            'id': 'triggerOpType',
            'body': 'function() { }',
            'triggerType': documents.TriggerType.Post,
            'triggerOperation': documents.TriggerOperation.Delete,
        }]

        def __CreateTriggers(client, collection, triggers):
            """Creates triggers.

            :Parameters:
                - `client`: document_client.DocumentClient
                - `collection`: dict

            """
            for trigger_i in triggers:
                trigger = client.CreateTrigger(collection['_self'],
                                               trigger_i)
                for property in trigger_i:
                    self.assertEqual(
                        trigger[property],
                        trigger_i[property],
                        'property {property} should match'.format(property=property))

        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collections
        collection1 = client.CreateCollection(
            db['_self'], { 'id': 'sample collection 1' })
        collection2 = client.CreateCollection(
            db['_self'], { 'id': 'sample collection 2' })
        collection3 = client.CreateCollection(
            db['_self'], { 'id': 'sample collection 3' })
        # create triggers
        __CreateTriggers(client, collection1, triggers_in_collection1)
        __CreateTriggers(client, collection2, triggers_in_collection2)
        __CreateTriggers(client, collection3, triggers_in_collection3)
        # create document
        triggers_1 = list(client.ReadTriggers(collection1['_self']))
        self.assertEqual(len(triggers_1), 3)
        document_1_1 = client.CreateDocument(collection1['_self'],
                                             { 'id': 'doc1',
                                               'key': 'value' },
                                             { 'preTriggerInclude': 't1' })
        self.assertEqual(document_1_1['id'],
                         'DOC1t1',
                         'id should be capitalized')
        document_1_2 = client.CreateDocument(
            collection1['_self'],
            { 'id': 'testing post trigger' },
            { 'postTriggerInclude': 'response1',
              'preTriggerInclude': 't1' })
        self.assertEqual(document_1_2['id'], 'TESTING POST TRIGGERt1')
        document_1_3 = client.CreateDocument(collection1['_self'],
                                             { 'id': 'responseheaders' },
                                             { 'preTriggerInclude': 't1' })
        self.assertEqual(document_1_3['id'], "RESPONSEHEADERSt1")

        triggers_2 = list(client.ReadTriggers(collection2['_self']))
        self.assertEqual(len(triggers_2), 2)
        document_2_1 = client.CreateDocument(collection2['_self'],
                                             { 'id': 'doc2',
                                               'key2': 'value2' },
                                             { 'preTriggerInclude': 't2' })
        self.assertEqual(document_2_1['id'],
                         'doc2',
                         'id shouldn\'t change')
        document_2_2 = client.CreateDocument(collection2['_self'],
                                             { 'id': 'Doc3',
                                               'prop': 'empty' },
                                             { 'preTriggerInclude': 't3' })
        self.assertEqual(document_2_2['id'], 'doc3t3')

        triggers_3 = list(client.ReadTriggers(collection3['_self']))
        self.assertEqual(len(triggers_3), 1)
        with self.assertRaises(Exception):
            client.CreateDocument(collection3['_self'],
                                  { 'id': 'Docoptype' },
                                  { 'postTriggerInclude': 'triggerOpType' })

    def test_stored_procedure_functionality(self):
        client = document_client.DocumentClient(host,
                                                { 'masterKey': masterKey })
        # create database
        db = client.CreateDatabase({ 'id': 'sample database' })
        # create collection
        collection = client.CreateCollection(
            db['_self'], { 'id': 'sample collection' })
        sproc1 = {
            'id': 'storedProcedure1',
            'body': (
                'function () {' +
                '  for (var i = 0; i < 1000; i++) {' +
                '    var item = getContext().getResponse().getBody();' +
                '    if (i > 0 && item != i - 1) throw \'body mismatch\';' +
                '    getContext().getResponse().setBody(i);' +
                '  }' +
                '}')
        }

        retrieved_sproc = client.CreateStoredProcedure(collection['_self'],
                                                       sproc1)
        result = client.ExecuteStoredProcedure(retrieved_sproc['_self'],
                                               None)
        self.assertEqual(result, 999)
        sproc2 = {
            'id': 'storedProcedure2',
            'body': (
                'function () {' +
                '  for (var i = 0; i < 10; i++) {' +
                '    getContext().getResponse().appendValue(\'Body\', i);' +
                '  }' +
                '}')
        }
        retrieved_sproc2 = client.CreateStoredProcedure(collection['_self'],
                                                        sproc2)
        result = client.ExecuteStoredProcedure(retrieved_sproc2['_self'],
                                               None)
        self.assertEqual(int(result), 123456789)
        sproc3 = {
            'id': 'storedProcedure3',
            'body': (
                'function (input) {' +
                    '  getContext().getResponse().setBody(' +
                    '      \'a\' + input.temp);' +
                '}')
        }
        retrieved_sproc3 = client.CreateStoredProcedure(collection['_self'],
                                                        sproc3)
        result = client.ExecuteStoredProcedure(retrieved_sproc3['_self'],
                                               {'temp': 'so'})
        self.assertEqual(result, 'aso')

    def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
        self.assert_(offer.get('id'), 'Id cannot be null.')
        self.assert_(offer.get('_rid'), 'Resource Id (Rid) cannot be null.')
        self.assert_(offer.get('_self'), 'Self Link cannot be null.')
        self.assert_(offer.get('resource'), 'Resource Link cannot be null.')
        self.assertTrue(offer['_self'].find(offer['id']) != -1,
                        'Offer id not contained in offer self link.')
        self.assertEqual(expected_coll_link.strip('/'), offer['resource'].strip('/'))
        if (expected_offer_type):
            self.assertEqual(expected_offer_type, offer.get('offerType'))

    def test_offer_read_and_query(self):
        client = document_client.DocumentClient(host, { 'masterKey': masterKey })
        # Create database.
        db = client.CreateDatabase({ 'id': 'sample database' })
        # Create collection.
        collection = client.CreateCollection(db['_self'], { 'id': 'sample collection' })
        offers = list(client.ReadOffers({}))
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), None)
        # Read the offer.
        read_offer = client.ReadOffer(expected_offer.get('_self'))
        self.__ValidateOfferResponseBody(read_offer, collection.get('_self'), expected_offer.get('offerType'))
        # Check if the read resource is what we expected.
        self.assertEqual(expected_offer.get('id'), read_offer.get('id'))
        self.assertEqual(expected_offer.get('_rid'), read_offer.get('_rid'))
        self.assertEqual(expected_offer.get('_self'), read_offer.get('_self'))
        self.assertEqual(expected_offer.get('resource'), read_offer.get('resource'))
        # Query for the offer.

        offers = list(client.QueryOffers(
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name': '@id', 'value': expected_offer['id']}
                ]
            }, {}))
        self.assertEqual(1, len(offers))
        query_one_offer = offers[0]
        self.__ValidateOfferResponseBody(query_one_offer, collection.get('_self'), expected_offer.get('offerType'))
        # Check if the query result is what we expected.
        self.assertEqual(expected_offer.get('id'), query_one_offer.get('id'))
        self.assertEqual(expected_offer.get('_rid'), query_one_offer.get('_rid'))
        self.assertEqual(expected_offer.get('_self'), query_one_offer.get('_self'))
        self.assertEqual(expected_offer.get('resource'), query_one_offer.get('resource'))
        # Expects an exception when reading offer with bad offer link.
        self.__AssertHTTPFailureWithStatus(400, client.ReadOffer, expected_offer.get('_self')[:-1] + 'x')
        # Now delete the collection.
        client.DeleteCollection(collection.get('_self'))
        # Reading fails.
        self.__AssertHTTPFailureWithStatus(404, client.ReadOffer, expected_offer.get('_self'))
        # Read feed now returns 0 results.
        offers = list(client.ReadOffers())
        self.assert_(not offers)

    def test_offer_replace(self):
        client = document_client.DocumentClient(host, { 'masterKey': masterKey })
        # Create database.
        db = client.CreateDatabase({ 'id': 'sample database' })
        # Create collection.
        collection = client.CreateCollection(db['_self'], { 'id': 'sample collection' })
        offers = list(client.ReadOffers())
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), None)
        # Replace the offer.
        offer_to_replace = dict(expected_offer)
        offer_to_replace['offerType'] = 'S2'
        replaced_offer = client.ReplaceOffer(offer_to_replace['_self'], offer_to_replace)
        self.__ValidateOfferResponseBody(replaced_offer, collection.get('_self'), 'S2')
        # Check if the replaced offer is what we expect.
        self.assertEqual(offer_to_replace.get('id'), replaced_offer.get('id'))
        self.assertEqual(offer_to_replace.get('_rid'), replaced_offer.get('_rid'))
        self.assertEqual(offer_to_replace.get('_self'), replaced_offer.get('_self'))
        self.assertEqual(offer_to_replace.get('resource'), replaced_offer.get('resource'))
        # Expects an exception when replacing an offer with bad id.
        offer_to_replace_bad_id = dict(offer_to_replace)
        offer_to_replace_bad_id['_rid'] = 'NotAllowed'
        self.__AssertHTTPFailureWithStatus(
            400, client.ReplaceOffer, offer_to_replace_bad_id['_self'], offer_to_replace_bad_id)
        # Expects an exception when replacing an offer with bad rid.
        offer_to_replace_bad_rid = dict(offer_to_replace)
        offer_to_replace_bad_rid['_rid'] = 'InvalidRid'
        self.__AssertHTTPFailureWithStatus(
            400, client.ReplaceOffer, offer_to_replace_bad_rid['_self'], offer_to_replace_bad_rid)
        # Expects an exception when replaceing an offer with null id and rid.
        offer_to_replace_null_ids = dict(offer_to_replace)
        offer_to_replace_null_ids['id'] = None
        offer_to_replace_null_ids['_rid'] = None
        self.__AssertHTTPFailureWithStatus(
            400, client.ReplaceOffer, offer_to_replace_null_ids['_self'], offer_to_replace_null_ids)

    def test_collection_with_offer_type(self):
        client = document_client.DocumentClient(host,
                                                {'masterKey': masterKey})
        # create database
        created_db = client.CreateDatabase({ 'id': 'sample database' })
        collections = list(client.ReadCollections(created_db['_self']))
        # create a collection
        before_create_collections_count = len(collections)
        collection_definition = { 'id': 'sample collection' }
        collection = client.CreateCollection(created_db['_self'],
                                             collection_definition,
                                             {
                                                 'offerType': 'S2'
                                             })
        # We should have an offer of type S2.
        offers = list(client.ReadOffers())
        self.assertEqual(1, len(offers))
        expected_offer = offers[0]
        self.__ValidateOfferResponseBody(expected_offer, collection.get('_self'), 'S2')

    def test_database_account_functionality(self):
        # Validate database account functionality.
        client = document_client.DocumentClient(host,
                                                { 'masterKey':
                                                  masterKey })
        database_account = client.GetDatabaseAccount()
        self.assertEqual(database_account.DatabasesLink, '/dbs/')
        self.assertEqual(database_account.MediaLink , '/media/')
        if (http_constants.HttpHeaders.MaxMediaStorageUsageInMB in
            client.last_response_headers):
            self.assertEqual(
                database_account.MaxMediaStorageUsageInMB,
                client.last_response_headers[
                    http_constants.HttpHeaders.MaxMediaStorageUsageInMB])
        if (http_constants.HttpHeaders.CurrentMediaStorageUsageInMB in
            client.last_response_headers):
            self.assertEqual(
                database_account.CurrentMediaStorageUsageInMB,
                client.last_response_headers[
                    http_constants.HttpHeaders.
                    CurrentMediaStorageUsageInMB])
        self.assertTrue(
            database_account.ConsistencyPolicy['defaultConsistencyLevel']
            != None)

    # To run this test, please provide your own CA certs file or download one from
    #     http://curl.haxx.se/docs/caextract.html
    #
    # def test_ssl_connection(self):
    #     connection_policy = documents.ConnectionPolicy()
    #     connection_policy.SSLConfiguration = documents.SSLConfiguration()
    #     connection_policy.SSLConfiguration.SSLCaCerts = './cacert.pem'
    #     client = document_client.DocumentClient(host, {'masterKey': masterKey}, connection_policy)
    #     # Read databases after creation.
    #     databases = list(client.ReadDatabases())


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise