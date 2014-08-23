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
masterKey = 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='
host = 'https://localhost:443'


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
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            databases = client.ReadDatabases().ToArray()
            if len(databases) == 0:
                return
            for database in databases:
                client.DeleteDatabase(database['_self'])

    def test_validate_database_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # read databases.
            databases = client.ReadDatabases().ToArray()
            self.assertTrue(type(databases) is list, 'Value should be an array')
            # create a database.
            before_create_databases_count = len(databases)
            database_definition = { 'id': 'sample database' }
            created_db = client.CreateDatabase(database_definition)
            self.assertEqual(created_db['id'], database_definition['id'])
            # Read databases after creation.
            databases = client.ReadDatabases().ToArray()
            self.assertEqual(len(databases),
                             before_create_databases_count + 1,
                             'create should increase the number of databases')
            # query databases.
            databases = client.QueryDatabases('^/?', {'jpath': True}).ToArray()
            self.assertTrue(len(databases) > 0,
                            'number of databases for the query should be > 0')
            databases = client.QueryDatabases(
                'SELECT * FROM root r WHERE r.id=\'' +
                database_definition['id'] + '\'').ToArray()
            self.assertTrue(len(databases) > 0,
                            'number of results for the query should be > 0')
            # replace database.
            created_db['id'] = 'replaced db'
            replaced_db = client.ReplaceDatabase(created_db['_self'], created_db)
            self.assertEqual(replaced_db['id'],
                             'replaced db',
                             'Db id should change')
            self.assertEqual(created_db['id'],
                             replaced_db['id'],
                            'Db id should stay the same')
            # read database.
            one_db_from_read = client.ReadDatabase(replaced_db['_self'])
            self.assertEqual(replaced_db['id'], one_db_from_read['id'])
            # delete database.
            client.DeleteDatabase(replaced_db['_self'])
            # read database after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadDatabase,
                                               created_db['_self'])

    def test_validate_collection_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            created_db = client.CreateDatabase({ 'id': 'sample database' })
            collections = client.ReadCollections(created_db['_self']).ToArray()
            self.assertTrue(type(collections) is list,
                           'Value should be an array')
            # create a collection
            before_create_collections_count = len(collections)
            collection_definition = { 'id': 'sample collection' }
            created_collection = client.CreateCollection(created_db['_self'],
                                                         collection_definition)
            self.assertEqual(created_collection['id'],
                             collection_definition['id'])
            # read collections after creation
            collections = client.ReadCollections(created_db['_self']).ToArray()
            self.assertEqual(len(collections),
                             before_create_collections_count + 1,
                             'create should increase the number of collections')
            # query collections
            collections = client.QueryCollections(created_db['_self'],
                                                  '^/?',
                                                  {'jpath': True}).ToArray()
            self.assertGreater(
                len(collections),
                0,
                'number of collections for the query should be > 0')
            collections = client.QueryCollections(
                created_db['_self'],
                'SELECT * FROM root r WHERE r.id=\'' +
                collection_definition['id'] + '\'').ToArray()
            self.assertGreater(len(collections),
                               0,
                               'number of results for the query should be > 0')
            # delete collection
            client.DeleteCollection(created_collection['_self'])
            # read collection after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadCollection,
                                               created_collection['_self'])

    def test_validate_document_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            created_db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection
            created_collection = client.CreateCollection(
                created_db['_self'],
                { 'id': 'sample collection' })
            # read documents
            documents = client.ReadDocuments(
                created_collection['_self']).ToArray()
            self.assertTrue(type(documents) is list, 'Value should be an array')
            # create a document
            before_create_documents_count = len(documents)
            document_definition = {'name': 'sample document',
                                   'foo': 'bar',
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
            # read documents after creation
            documents = client.ReadDocuments(
                created_collection['_self']).ToArray()
            self.assertEqual(
                len(documents),
                before_create_documents_count + 1,
                'create should increase the number of documents')
            # query documents
            documents = client.QueryDocuments(created_collection['_self'],
                                              '^/?',
                                              {'jpath': True}).ToArray()
            self.assertGreater(
                len(documents),
                0,
                'number of documents for the query should be > 0')
            documents = client.QueryDocuments(
                created_collection['_self'],
                'SELECT * FROM root r WHERE r.name=\'' +
                document_definition['name'] + '\'').ToArray()
            self.assertGreater(
                len(documents),
                0,
                'number of results for the query should be > 0')
            # replace document.
            created_document['name'] = 'replaced document'
            created_document['foo'] = 'not bar'
            replaced_document = client.ReplaceDocument(
                created_document['_self'],                                      
                created_document)
            self.assertEqual(replaced_document['name'],
                             'replaced document',
                             'document id property should change')
            self.assertEqual(replaced_document['foo'],
                             'not bar',
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

    def test_validate_attachment_crud(self):
        import StringIO
        class __ReadableStream(StringIO.StringIO):
            """Customized file-like stream.
            """

            def __init__(self, first_chunk=None, second_chunk=None):
                """Initialization.

                :Parameters:
                    - `first_chunk`: str, unicode or None
                    - `second_chunk`: str, unicode or None

                """
                self.__first_chunk = (first_chunk
                                      if first_chunk else 'first chunk ')
                self.__second_chunk = (second_chunk
                                       if second_chunk else 'second chunk')
                self.__length = (len(self.__first_chunk) +
                                 len(self.__second_chunk))
                self.__chunk_count = 0
                StringIO.StringIO.__init__(
                    self,
                    self.__first_chunk + self.__second_chunk)

            def read(self, n=-1):
                """Simulates the read method in a file stream.

                :Parameters:
                    - `n`: int

                :Returns:
                    str

                """
                output = None
                if self.__chunk_count == 0:
                    output = StringIO.StringIO.read(self,
                                                    len(self.__first_chunk))
                elif self.__chunk_count == 1:
                    output = StringIO.StringIO.read(self,
                                                    len(self.__second_chunk))
                else:
                    output = StringIO.StringIO.read(self)
                self.__chunk_count += 1
                return output

            def __len__(self):
                """To make len(__ReadableStream) work.
                """
                return self.__length

        def __ReadMediaResponse(media_response):
            """Reads and returns the content of a media response file stream.

            :Parameters:
                - `media_response`: file-like stream object

            :Returns:
                str

            """
            return media_response.read()

        # Should do attachment CRUD operations successfully
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection
            collection = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection' })
            # create document
            document = client.CreateDocument(collection['_self'],
                                             { 'id': 'sample document',
                                               'foo': 'bar',
                                               'key': 'value' })
            # list all attachments
            attachments = client.ReadAttachments(document['_self']).ToArray()
            self.assertTrue(type(attachments) is list,
                            'Value should be an array')
            initial_count = len(attachments)
            valid_media_options = { 'slug': 'attachment id',
                                    'contentType': 'application/text' }
            invalid_media_options = { 'slug': 'attachment name',
                                      'contentType': 'junt/test' }
            # create attachment with invalid content-type
            content_stream = __ReadableStream()
            self.__AssertHTTPFailureWithStatus(
                400,
                client.CreateAttachmentAndUploadMedia,
                document['_self'],
                content_stream,
                invalid_media_options)
            content_stream = __ReadableStream()
            # create streamed attachment with valid content-type
            valid_attachment = client.CreateAttachmentAndUploadMedia(
                document['_self'], content_stream, valid_media_options)
            self.assertEqual(valid_attachment['id'],
                             'attachment id',
                             'id of created attachment should be the'
                             ' same as the one in the request')
            content_stream = __ReadableStream()
            # create colliding attachment
            self.__AssertHTTPFailureWithStatus(
                409,
                client.CreateAttachmentAndUploadMedia,
                document['_self'],
                content_stream,
                valid_media_options)

            content_stream = __ReadableStream()
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
            attachments = client.ReadAttachments(document['_self']).ToArray()
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
            content_stream = __ReadableStream('modified first chunk ',
                                              'modified second chunk')
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
            self.assertEqual(__ReadMediaResponse(media_response),
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
            attachments = client.ReadAttachments(document['_self']).ToArray()
            self.assertEqual(len(attachments), 0)

    def test_validate_user_crud(self):
        # Should do User CRUD operations successfully.
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # list users
            users = client.ReadUsers(db['_self']).ToArray()
            self.assertTrue(type(users) is list, 'Value should be an array')
            before_create_count = len(users)
            # create user
            user = client.CreateUser(db['_self'], { 'id': 'new user' })
            self.assertEqual(user['id'], 'new user', 'user id error')
            # list users after creation
            users = client.ReadUsers(db['_self']).ToArray()
            self.assertEqual(len(users), before_create_count + 1)
            # query users
            users = client.QueryUsers(db['_self'], '^/?',
                                      {'jpath': True}).ToArray()
            self.assertGreater(len(users),
                               0,
                               'number of users for the query should be > 0')
            results = client.QueryUsers(
                db['_self'],
                'SELECT * FROM root r WHERE r.id="'
                + 'new user' + '"').ToArray()
            self.assertGreater(len(results),
                               0,
                               'number of results for the query should be > 0')
            # replace user
            user['id'] = 'replaced user'
            replaced_user = client.ReplaceUser(user['_self'], user)
            self.assertEqual(replaced_user['id'],
                             'replaced user',
                             'user id should change')
            self.assertEqual(user['id'],
                             replaced_user['id'],
                             "user id should stay the same")
            # read user
            user = client.ReadUser(replaced_user['_self'])
            self.assertEqual(replaced_user['id'], user['id'])
            # delete user
            client.DeleteUser(user['_self'])
            # read user after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadUser,
                                               user['_self'])

    def test_validate_permission_crud(self):
        # Should do Permission CRUD operations successfully
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create user
            user = client.CreateUser(db['_self'], { 'id': 'new user' })
            # list permissions
            permissions = client.ReadPermissions(user['_self']).ToArray()
            self.assertTrue(type(permissions) is list,
                            'Value should be an array')
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
            permissions = client.ReadPermissions(user['_self']).ToArray()
            self.assertEqual(len(permissions), before_create_count + 1)
            # query permissions
            permissions = client.QueryPermissions(
                user['_self'], '^/?', {'jpath': True}).ToArray()
            self.assertGreater(
                len(permissions),
                0,
                'number of permissions for the query should be > 0')
            results = client.QueryPermissions(
                user['_self'],
                'SELECT * FROM root r WHERE r.id="' +
                permission['id'] + '"').ToArray()
            self.assertGreater(len(results),
                               0,
                               'number of results for the query should be > 0')
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

    def test_validate_authorization(self):
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
                                                'foo': 'bar',
                                                'key': 'value' })
            # create document 2
            document2 = client.CreateDocument(
                collection1['_self'],
                { 'id': 'coll1doc2', 'foo': 'bar2', 'key': 'value2' })
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

        with document_client.DocumentClient(host, {}) as client:
            self.__AssertHTTPFailureWithStatus(401,
                                               client.ReadDatabases().ToArray)
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
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
            success_documents = col1_client.ReadDocuments(
                success_coll1['_self']).ToArray()
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

    def test_validate_trigger_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection
            collection = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection' })
            # read triggers
            triggers = client.ReadTriggers(collection['_self']).ToArray()
            self.assertTrue(type(triggers) is list, 'Value should be an array')
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
                    self.assertEqual(trigger[property],
                                     trigger_definition[property],
                                     "property " + property + " should match")
                else:
                        self.assertEqual(trigger['body'],
                                         'function () {var x = 10;}')

            # read triggers after creation
            triggers = client.ReadTriggers(collection['_self']).ToArray()
            self.assertEqual(len(triggers),
                             before_create_triggers_count + 1,
                             'create should increase the number of triggers')
            # query triggers
            triggers = client.QueryTriggers(
                collection['_self'],
                '(^/"id"/"' + trigger_definition['id'] + '")/"_rid"!?',
                {'jpath': True}).ToArray()
            self.assertGreater(len(triggers),
                               0,
                               'number of triggers for the query should be > 0')
            results = client.QueryTriggers(
                collection['_self'],
                'SELECT * FROM root r WHERE r.id="' +
                trigger_definition['id'] + '"').ToArray()
            self.assertGreater(len(results),
                               0,
                               'number of results for the query should be > 0')
            # replace trigger
            trigger['body'] = 'function() {var x = 20;}'
            replaced_trigger = client.ReplaceTrigger(trigger['_self'], trigger)
            for property in trigger_definition:
                if property != "serverScript":
                    self.assertEqual(replaced_trigger[property],
                                     trigger[property],
                                     'property ' + property + ' should match')
                else:
                    self.assertEqual(replaced_trigger['body'],
                                     'function () {var x = 20;}')

            # read trigger
            trigger = client.ReadTrigger(replaced_trigger['_self'])
            self.assertEqual(replaced_trigger['id'], trigger['id'])
            # delete trigger
            res = client.DeleteTrigger(replaced_trigger['_self'])
            # read triggers after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadTrigger,
                                               replaced_trigger['_self'])

    def test_validate_udf_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection
            collection = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection' })
            # read udfs
            udfs = client.ReadUserDefinedFunctions(collection['_self']).ToArray()
            self.assertTrue(type(udfs) is list, 'Value should be an array')
            # create a udf
            before_create_udfs_count = len(udfs)
            udf_definition = {
                'id': 'sample udf',
                'body': 'function() {var x = 10;}'
            }
            udf = client.CreateUserDefinedFunction(collection['_self'],
                                                   udf_definition)
            for property in udf_definition:
                    self.assertEqual(udf[property],
                                     udf_definition[property],
                                     'property ' + property + ' should match')
                                
            # read udfs after creation
            udfs = client.ReadUserDefinedFunctions(collection['_self']).ToArray()
            self.assertEqual(len(udfs),
                             before_create_udfs_count + 1,
                             'create should increase the number of udfs')
            # query udfs
            udfs = client.QueryUserDefinedFunctions(
                collection['_self'],
                '(^/"id"/"' + udf_definition['id'] + '")/"_rid"!?',
                {'jpath': True}).ToArray()
            self.assertGreater(len(udfs),
                               0,
                               'number of udfs for the query should be > 0')
            results = client.QueryUserDefinedFunctions(
                collection['_self'],
                'SELECT * FROM root r WHERE r.id="' +
                udf_definition['id'] + '"').ToArray()
            self.assertGreater(len(results),
                               0,
                               'number of results for the query should be > 0')
            # replace udf
            udf['body'] = 'function() {var x = 20;}'
            replaced_udf = client.ReplaceUserDefinedFunction(udf['_self'], udf)
            for property in udf_definition:
                    self.assertEqual(replaced_udf[property],
                                     udf[property],
                                     'property ' + property + ' should match')
            # read udf
            udf = client.ReadUserDefinedFunction(replaced_udf['_self'])
            self.assertEqual(replaced_udf['id'], udf['id'])
            # delete udf
            res = client.DeleteUserDefinedFunction(replaced_udf['_self'])
            # read udfs after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadUserDefinedFunction,
                                               replaced_udf['_self'])

    def test_validate_sproc_crud(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            # create database
            db = client.CreateDatabase({ 'id': 'sample database' })
            # create collection
            collection = client.CreateCollection(
                db['_self'],
                { 'id': 'sample collection' })
            # read sprocs
            sprocs = client.ReadStoredProcedures(collection['_self']).ToArray()
            self.assertTrue(type(sprocs) is list, 'Value should be an array')
            # create a sproc
            before_create_sprocs_count = len(sprocs)
            sproc_definition = {
                'id': 'sample sproc',
                'serverScript': 'function() {var x = 10;}}'
            }
            sproc = client.CreateStoredProcedure(collection['_self'],
                                                 sproc_definition)
            for property in sproc_definition:
                if property != "serverScript":
                    self.assertEqual(sproc[property],
                                     sproc_definition[property],
                                     'property ' + property + ' should match')
                else:
                    self.assertEqual(sproc['body'], 'function () {var x = 10;}')
                                
            # read sprocs after creation
            sprocs = client.ReadStoredProcedures(collection['_self']).ToArray()
            self.assertEqual(len(sprocs),
                             before_create_sprocs_count + 1,
                             'create should increase the number of sprocs')
            # query sprocs
            sprocs = client.QueryStoredProcedures(
                collection['_self'],
                '(^/"id"/"' + sproc_definition['id'] + '")/"_rid"!?',
                {'jpath': True}).ToArray()
            self.assertGreater(len(sprocs),
                               0,
                               'number of sprocs for the query should be > 0')
            # replace sproc
            sproc['body'] = 'function() {var x = 20;}'
            replaced_sproc = client.ReplaceStoredProcedure(sproc['_self'], sproc)
            for property in sproc_definition:
                if property != 'serverScript':
                    self.assertEqual(replaced_sproc[property],
                                     sproc[property],
                                     'property ' + property + ' should match')
                else:
                    self.assertEqual(replaced_sproc['body'],
                                     "function () {var x = 20;}")
            # read sproc
            sproc = client.ReadStoredProcedure(replaced_sproc['_self'])
            self.assertEqual(replaced_sproc['id'], sproc['id'])
            # delete sproc
            res = client.DeleteStoredProcedure(replaced_sproc['_self'])
            # read sprocs after deletion
            self.__AssertHTTPFailureWithStatus(404,
                                               client.ReadStoredProcedure,
                                               replaced_sproc['_self'])

    def test_validate_collection_indexing_policy(self):
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
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
                'id': 'TestQueryDocumentsSecondaryIndexCollection',
                'indexingPolicy': {
                    'automatic': True,
                    'indexingMode': 'Lazy',
                    'paths': {
                        'Frequent': ['/'],
                        'InFrequent': ['/"A"/"B"', '/"A"/"D"'],
                        'Excluded': ['/"X"/"D"']
                    }
                }
            }
            coll = client.DeleteCollection(consistent_collection['_self'])
            collection_with_secondary_index = client.CreateCollection(
                db['_self'], collection_definition)
            self.assertEqual(len(collection_with_secondary_index[
                                 'indexingPolicy']['paths']['Frequent']),
                             1,
                             'Unexpected frequent path count')
            self.assertEqual(len(collection_with_secondary_index[
                                 'indexingPolicy']['paths']['InFrequent']),
                             2,
                             'Unexpected infrequent path count')
            self.assertEqual(len(collection_with_secondary_index[
                                 'indexingPolicy']['paths']['Excluded']),
                             1,
                             'Unexpected excluded path count')

    def test_validate_client_request_timeout(self):
        connection_policy = documents.ConnectionPolicy()
        # making timeout 1 ms to make sure it will throw
        connection_policy.RequestTimeout = 1
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey},
                                            connection_policy) as client:
            # create database
            import httplib
            with self.assertRaises(Exception):
                # Will time out.
                client.CreateDatabase({ 'id': "sample database" })

    def test_validate_query_iterator_functionality(self):
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

        # Validate QueryIterator iterator ToArray.
        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
            resources = __CreateResources(client)
            with client.ReadDocuments(resources['coll']['_self'],
                                      {'maxItemCount':2}) as query_iterator:
                docs = query_iterator.ToArray()
                self.assertEqual(
                            len(docs),
                            3,
                            'queryIterator should return all documents' +
                            ' using continuation')
                self.assertEqual(docs[0]['id'], resources['doc1']['id'])
                self.assertEqual(docs[1]['id'], resources['doc2']['id'])
                self.assertEqual(docs[2]['id'], resources['doc3']['id'])

                # Validate QueryIterator iterator with 'for'.
                query_iterator.Reset()
                counter = 0
                # test QueryIterator with 'for'.
                for doc in query_iterator:
                    counter += 1
                    if counter == 1:
                        self.assertEqual(doc['id'],
                                         resources['doc1']['id'],
                                         'first document should be doc1')
                    elif counter == 2:
                        self.assertEqual(doc['id'],
                                         resources['doc2']['id'],
                                         'second document should be doc2')
                    elif counter == 3:
                        self.assertEqual(doc['id'],
                                         resources['doc3']['id'],
                                         'third document should be doc3')
                self.assertLess(counter, 5, 'iterator should have stopped')

                # Validate queryIterator reading all entries.
                query_iterator.Reset()
                counter = 0
                for doc in query_iterator:
                    counter += 1
                    if counter == 1:
                        self.assertEqual(doc['id'],
                                         resources['doc1']['id'],
                                                 'call queryIterator.nextItem after' +
                                                 ' reset should return first document')
                    elif counter == 2:
                        self.assertEqual(doc['id'],
                                         resources['doc2']['id'],
                                                 'call queryIterator.nextItem again' +
                                                 ' should return second document')
                    elif counter == 3:
                        self.assertEqual(doc['id'],
                                         resources['doc3']['id'],
                                                 'call queryIterator.nextItem again' +
                                                 ' should return third document')
                self.assertEqual(counter, 3)
                
                # Validate queryIterator iterator NextBatchToArray.
                query_iterator.Reset()
                docs = query_iterator.NextBatchToArray()
                self.assertEqual(len(docs), 2, 'first batch size should be 2')
                self.assertEqual(docs[0]['id'],
                                 resources['doc1']['id'],
                                 'first batch first document should be doc1')
                self.assertEqual(docs[1]['id'],
                                 resources['doc2']['id'],
                                 'batch first second document should be doc2')
                docs = query_iterator.NextBatchToArray()
                self.assertEqual(len(docs), 1, 'second batch size should be 2')
                self.assertEqual(docs[0]['id'],
                                 resources['doc3']['id'],
                                 'second batch element should be doc3')

    def test_validate_trigger_functionality(self):
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
                    self.assertEqual(trigger[property],
                                     trigger_i[property],
                                     'property ' + property + ' should match')

        with document_client.DocumentClient(host,
                                            {'masterKey': masterKey}) as client:
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
            triggers_1 = client.ReadTriggers(collection1['_self']).ToArray()
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

            triggers_2 = client.ReadTriggers(collection2['_self']).ToArray()
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

            triggers_3 = client.ReadTriggers(collection3['_self']).ToArray()
            self.assertEqual(len(triggers_3), 1)
            with self.assertRaises(Exception):
                client.CreateDocument(collection3['_self'],
                                      { 'id': 'Docoptype' },
                                      { 'postTriggerInclude': 'triggerOpType' })

    def test_validate_stored_procedure_functionality(self):
        with document_client.DocumentClient(host,
                                            { 'masterKey': masterKey }
                                            ) as client:
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

    def test_validate_database_account_functionality(self):
        # Validate database account functionality.
        with document_client.DocumentClient(host,
                                            { 'masterKey':
                                              masterKey }) as client:
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
            if (http_constants.HttpHeaders.DatabaseAccountCapacityUnitsConsumed
                in
                client.last_response_headers):
                self.assertEqual(
                    database_account.CapacityUnitsConsumed,
                    client.last_response_headers[
                        http_constants.HttpHeaders.
                        DatabaseAccountCapacityUnitsConsumed])
            if (http_constants.HttpHeaders.
                    DatabaseAccountCapacityUnitsProvisioned in
                client.last_response_headers):
                self.assertEqual(
                    database_account.CapacityUnitsProvisioned,
                    client.last_response_headers[
                        http_constants.HttpHeaders.
                        DatabaseAccountCapacityUnitsProvisioned])
            if (http_constants.HttpHeaders.
                    DatabaseAccountConsumedDocumentStorageInMB in
                client.last_response_headers):
                self.assertEqual(
                    database_account.ConsumedDocumentStorageInMB,
                    client.last_response_headers[
                        http_constants.HttpHeaders.
                        DatabaseAccountConsumedDocumentStorageInMB])
            if (http_constants.HttpHeaders.
                DatabaseAccountReservedDocumentStorageInMB in
                client.last_response_headers):
                self.assertEqual(
                    database_account.ReservedDocumentStorageInMB,
                    client.last_response_headers[
                                http_constants.HttpHeaders.
                                DatabaseAccountReservedDocumentStorageInMB])
            if (http_constants.HttpHeaders.
                DatabaseAccountProvisionedDocumentStorageInMB in
                client.last_response_headers):
                self.assertEqual(
                    database_account.ProvisionedDocumentStorageInMB,
                    client.last_response_headers[
                        http_constants.HttpHeaders.
                        DatabaseAccountProvisionedDocumentStorageInMB])
            self.assertTrue(
                database_account.ConsistencyPolicy['defaultConsistencyLevel']
                != None)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise