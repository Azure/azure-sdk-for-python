# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Document client.
"""


import pydocumentdb.base as base
import pydocumentdb.documents as documents
import pydocumentdb.http_constants as http_constants
import pydocumentdb.query_iterator as query_iterator
import pydocumentdb.runtime_constants as runtime_constants
import pydocumentdb.synchronized_request as synchronized_request


class DocumentClient(object):
    """Represents a document client.

    Provides a client-side logical representation of the Azure DocumentDB
    service. This client is used to configure and execute requests against the
    service.

    The service client encapsulates the endpoint and credentials used to access
    the DocumentDB service.
    """

    def __init__(self,
                 url_connection,
                 auth,
                 connection_policy=None,
                 consistency_level=None):
        """
        :Parameters:
            - `url_connection`: str, the URL for connecting to the DB server.
            - `auth`: dict, contains 'masterKey' or 'resourceTokens', where
               auth['masterKey'] is the default authorization key to use to
               create the client, and auth['resourceTokens'] is the alternative
               authorization key.
            - `connection_policy`: documents.ConnectionPolicy, the connection
              policy for the client.
            - `consistency_level`: documents.ConsistencyLevel, the default
              consistency policy for client operations.

        """
        self.url_connection = url_connection

        self.master_key = None
        self.resource_tokens = None
        if auth != None:
            self.master_key = (auth['masterKey']
                               if 'masterKey' in auth else None)
            self.resource_tokens = (auth['resourceTokens']
                                    if 'resourceTokens' in auth else None)

            if 'permissionFeed' in auth and auth['permissionFeed']:
                self.resource_tokens = {}
                for permission_feed in auth['permissionFeed']:
                    resource_parts = permission_feed['resource'].split('/')
                    id = resource_parts[-1]
                    self.resource_tokens[id] = permission_feed['_token']

        self.connection_policy = (connection_policy or
                                  documents.ConnectionPolicy())

        self.default_headers = {
            http_constants.HttpHeaders.CacheControl: 'no-cache',
            http_constants.HttpHeaders.Version:
                http_constants.Versions.CurrentVersion,
            http_constants.HttpHeaders.UserAgent:
                http_constants.Versions.UserAgent
        }

        if consistency_level != None:
            self.default_headers[
                http_constants.HttpHeaders.ConsistencyLevel] = consistency_level
        # Keeps the latest response headers from server.
        self.last_response_headers = None

    def CreateDatabase(self, body, options={}):
        """Creates a database.

        :Parameters:
            - `body`: dict, the Azure DocumentDB database to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/dbs'
        return self.Create(body, path, 'dbs', None, None, options)

    def ReadDatabase(self, database_link, options={}):
        """Reads a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + database_link
        database_id = base.GetIdFromLink(database_link)
        return self.Read(path, 'dbs', database_id, None, options)

    def ReadDatabases(self, options={}):
        """Reads all databases.

        :Parameters:
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryDatabases(None, options)

    def QueryDatabases(self, query, options={}):
        """Queries databases.

        :Parameters:
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        def fetch_fn(options):
            def result_fn(result):
                return result['Databases']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed('/dbs',
                                    'dbs',
                                    '',
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def ReadCollections(self, database_link, options={}):
        """Reads all collections in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryCollections(database_link, None, options)

    def QueryCollections(self, database_link, query, options={}):
        """Queries collections in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + database_link + 'colls/'
        database_id = base.GetIdFromLink(database_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['DocumentCollections']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'colls',
                                    database_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def CreateCollection(self, database_link, body, options={}):
        """Creates a collection in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `body`: dict, , the Azure DocumentDB collection to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + database_link + 'colls/'
        database_id = base.GetIdFromLink(database_link)
        return self.Create(body,
                           path,
                           'colls',
                           database_id,
                           None,
                           options)

    def ReadCollection(self, collection_link, options={}):
        """Reads a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + collection_link
        collection_id = base.GetIdFromLink(collection_link)
        return self.Read(path,
                         'colls',
                         collection_id,
                         None,
                         options)

    def CreateUser(self, database_link, body, options={}):
        """Creates a user.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `body`: dict, the Azure DocumentDB user to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + database_link + 'users/'
        database_id = base.GetIdFromLink(database_link)
        return self.Create(body,
                           path,
                           'users',
                           database_id,
                           None,
                           options)

    def ReadUser(self, user_link, options={}):
        """Reads a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + user_link
        user_id = base.GetIdFromLink(user_link)
        return self.Read(path, 'users', user_id, None, options)

    def ReadUsers(self, database_link, options={}):
        """Reads all users in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.
        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryUsers(database_link, None, options)

    def QueryUsers(self, database_link, query, options={}):
        """Queries users in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + database_link + 'users/'
        database_id = base.GetIdFromLink(database_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['Users']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'users',
                                    database_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def ReplaceDatabase(self, database_link, db, options={}):
        """Replaces a database and returns it.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `db`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + database_link
        database_id = base.GetIdFromLink(database_link)
        return self.Replace(db,
                            path,
                            'dbs',
                            database_id,
                            None,
                            options)

    def DeleteDatabase(self, database_link, options={}):
        """Deletes a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + database_link
        database_id = base.GetIdFromLink(database_link)
        return self.DeleteResource(path,
                                   'dbs',
                                   database_id,
                                   None,
                                   options)

    def CreatePermission(self, user_link, body, options={}):
        """Creates a permission for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `body`: dict, the Azure DocumentDB user permission to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + user_link + 'permissions/'
        user_id = base.GetIdFromLink(user_link)
        return self.Create(body,
                           path,
                           'permissions',
                           user_id,
                           None,
                           options)

    def ReadPermission(self, permission_link, options={}):
        """Reads a permission.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + permission_link
        permission_id = base.GetIdFromLink(permission_link)
        return self.Read(path,
                         'permissions',
                          permission_id,
                          None,
                          options)

    def ReadPermissions(self, user_link, options={}):
        """Reads all permissions for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryPermissions(user_link, None, options)

    def QueryPermissions(self, user_link, query, options={}):
        """Queries permissions for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + user_link + 'permissions/'
        user_id = base.GetIdFromLink(user_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['Permissions']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'permissions',
                                    user_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def ReplaceUser(self, user_link, user, options={}):
        """Replaces a user and return it.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `user`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + user_link
        user_id = base.GetIdFromLink(user_link)
        return self.Replace(user,
                            path,
                            'users',
                            user_id,
                            None,
                            options)

    def DeleteUser(self, user_link, options={}):
        """Deletes a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + user_link
        user_id = base.GetIdFromLink(user_link)
        return self.DeleteResource(path,
                                   'users',
                                   user_id,
                                   None,
                                   options)

    def ReplacePermission(self, permission_link, permission, options={}):
        """Replaces a permission and return it.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `permission`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + permission_link
        permission_id = base.GetIdFromLink(permission_link)
        return self.Replace(permission,
                            path,
                            'permissions',
                            permission_id,
                            None,
                            options)

    def DeletePermission(self, permission_link, options={}):
        """Deletes a permission.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + permission_link
        permission_id = base.GetIdFromLink(permission_link)
        return self.DeleteResource(path,
                                   'permissions',
                                   permission_id,
                                   None,
                                   options)

    def ReadDocuments(self, collection_link, feed_options={}):
        """Reads all documents in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `feed_options`: dict

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryDocuments(collection_link, None, feed_options)

    def QueryDocuments(self, collection_link, query, options={}):
        """Queries documents in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + collection_link + 'docs/'
        collection_id = base.GetIdFromLink(collection_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['Documents']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'docs',
                                    collection_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def CreateDocument(self, collection_link, body, options={}):
        """Creates a document in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `body`: dict, the Azure DocumentDB document to create.
            - `body['id']`: str, id of the document, MUST be unique for each
              document.
            - `options`: dict, the request options for the request.
            - `options['disableAutomaticIdGeneration']`: bool, disables the
              automatic id generation. If id is missing in the body and this
              option is true, an error will be returned.

        :Returns:
            dict

        """
        body = body.copy()
        if (((not 'id' in body) or (not body['id'])) and
            ((not 'disableAutomaticIdGeneration' in options) or
             (not options['disableAutomaticIdGeneration']))):
            body['id'] = base.GenerateGuidId()
        path = '/' + collection_link + 'docs/'
        collection_id = base.GetIdFromLink(collection_link)
        return self.Create(body,
                           path,
                           'docs',
                           collection_id,
                           None,
                           options)
 
    def ReadDocument(self, document_link, options={}):
        """Reads a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + document_link
        document_id = base.GetIdFromLink(document_link)
        return self.Read(path,
                         'docs',
                         document_id,
                         None,
                         options)

    def ReadTriggers(self, collection_link, options={}):
        """Reads all triggers in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryTriggers(collection_link, None, options)

    def QueryTriggers(self, collection_link, query, options={}):
        """Queries triggers in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + collection_link + 'triggers/'
        collection_id = base.GetIdFromLink(collection_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['Triggers']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'triggers',
                                    collection_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def CreateTrigger(self, collection_link, trigger, options={}):
        """Creates a trigger in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `trigger`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        trigger = trigger.copy()
        if 'serverScript' in trigger:
            trigger['body'] = str(trigger['serverScript'])
            trigger.pop('serverScript', None)
        elif 'body' in trigger:
            trigger['body'] = str(trigger['body'])
 
        path = '/' + collection_link + 'triggers/'
        collection_id = base.GetIdFromLink(collection_link)
        return self.Create(trigger,
                           path,
                           'triggers',
                           collection_id,
                           None,
                           options)

    def ReadTrigger(self, trigger_link, options={}):
        """Reads a trigger.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + trigger_link
        trigger_id = base.GetIdFromLink(trigger_link)
        return self.Read(path, 'triggers', trigger_id, None, options)

    def ReadUserDefinedFunctions(self, collection_link, options={}):
        """Reads all user defined functions in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryUserDefinedFunctions(collection_link, None, options)

    def QueryUserDefinedFunctions(self, collection_link, query, options={}):
        """Queries user defined functions in a collection.

        :Parameters:
            - `collection_link`: str, the link to the collection.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + collection_link + 'udfs/'
        collection_id = base.GetIdFromLink(collection_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['UserDefinedFunctions']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'udfs',
                                    collection_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def CreateUserDefinedFunction(self, collection_link, udf, options={}):
        """Creates a user defined function in a collection.

        :Parameters:
            - `collection_link`: str, the link to the collection.
            - `udf`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        udf = udf.copy()
        if 'serverScript' in udf:
            udf['body'] = str(udf['serverScript'])
            udf.pop('serverScript', None)
        elif 'body' in udf:
            udf['body'] = str(udf['body'])

        path = '/' + collection_link + 'udfs/'
        collection_id = base.GetIdFromLink(collection_link)
        return self.Create(udf,
                           path,
                           'udfs',
                           collection_id,
                           None,
                           options)

    def ReadUserDefinedFunction(self, udf_link, options={}):
        """Reads a user defined function.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + udf_link
        udf_id = base.GetIdFromLink(udf_link)
        return self.Read(path, 'udfs', udf_id, None, options)

    def ReadStoredProcedures(self, collection_link, options={}):
        """Reads all store procedures in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryStoredProcedures(collection_link, None, options)

    def QueryStoredProcedures(self, collection_link, query, options={}):
        """Queries stored procedures in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + collection_link + 'sprocs/'
        collection_id = base.GetIdFromLink(collection_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['StoredProcedures']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'sprocs',
                                    collection_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def CreateStoredProcedure(self, collection_link, sproc, options={}):
        """Creates a stored procedure in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `sproc`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        sproc = sproc.copy()
        if 'serverScript' in sproc:
            sproc['body'] = str(sproc['serverScript'])
            sproc.pop('serverScript', None)
        elif 'body' in sproc:
            sproc['body'] = str(sproc['body'])
        path = '/' + collection_link + 'sprocs/'
        collection_id = base.GetIdFromLink(collection_link)
        return self.Create(sproc,
                           path,
                           'sprocs',
                           collection_id,
                           None,
                           options)

    def ReadStoredProcedure(self, sproc_link, options={}):
        """Reads a stored procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + sproc_link
        sproc_id = base.GetIdFromLink(sproc_link)
        return self.Read(path, 'sprocs', sproc_id, None, options)

    def ReadConflicts(self, collection_link, feed_options={}):
        """Reads conflicts.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `feed_options`: dict

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + collection_link + 'conflicts/'
        collection_id = base.GetIdFromLink(collection_link)
        def fetch_fn(options):
            def result_fn(result):
                return result['Conflicts']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'conflicts',
                                    collection_id,
                                    result_fn,
                                    create_fn,
                                    '',
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)

    def ReadConflict(self, conflict_link, options={}):
        """Reads a conflict.

        :Parameters:
            - `conflict_link`: str, the link to the conflict.
            - `opitions`: dict

        :Returns:
            dict

        """
        path = '/' + conflict_link
        conflict_id = base.GetIdFromLink(conflict_link)
        return self.Read(path,
                         'conflicts',
                         conflict_id,
                         None,
                         options)

    def DeleteCollection(self, collection_link, options={}):
        """Deletes a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + collection_link
        collection_id = base.GetIdFromLink(collection_link)
        return self.DeleteResource(path,
                                   'colls',
                                   collection_id,
                                   None,
                                   options)

    def ReplaceDocument(self, document_link, new_document, options={}):
        """Replaces a document and returns it.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `new_document`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + document_link
        document_id = base.GetIdFromLink(document_link)
        return self.Replace(new_document,
                            path,
                            'docs',
                            document_id,
                            None,
                            options)

    def DeleteDocument(self, document_link, options={}):
        """Deletes a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + document_link
        document_id = base.GetIdFromLink(document_link)
        return self.DeleteResource(path,
                                   'docs',
                                   document_id,
                                   None,
                                   options)

    def CreateAttachment(self, document_link, body, options={}):
        """Creates an attachment in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `body`: dict, the Azure DocumentDB attachment to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + document_link + 'attachments/'
        document_id = base.GetIdFromLink(document_link)
        return self.Create(body,
                           path,
                           'attachments',
                           document_id,
                           None,
                           options)

    def CreateAttachmentAndUploadMedia(self,
                                       document_link,
                                       readable_stream,
                                       options={}):
        """Creates an attachment and upload media.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `readable_stream`: file-like stream object
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        initial_headers = base.Extend({}, self.default_headers)

        # Add required headers slug and content-type.
        if 'slug' in options:
            initial_headers[http_constants.HttpHeaders.Slug] = options['slug']

        if 'contentType' in options:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                options['contentType'])
        else:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                runtime_constants.MediaTypes.OctetStream)

        path = '/' + document_link + 'attachments/'
        document_id = base.GetIdFromLink(document_link)
        return self.Create(readable_stream,
                           path,
                           'attachments',
                           document_id,
                           initial_headers,
                           options)

    def ReadAttachment(self, attachment_link, options={}):
        """Reads an attachment.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + attachment_link
        attachment_id = base.GetIdFromLink(attachment_link)
        return self.Read(path,
                         'attachments',
                         attachment_id,
                         None,
                         options)

    def ReadAttachments(self, document_link, options={}):
        """Reads all attachments in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        return self.QueryAttachments(document_link, None, options)

    def QueryAttachments(self, document_link, query, options={}):
        """Queries attachments in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterator.QueryIterator

        """
        path = '/' + document_link + 'attachments/'
        document_id = base.GetIdFromLink(document_link)

        def fetch_fn(options):
            def result_fn(result):
                return result['Attachments']
            def create_fn(parent, body):
                return body
            return self.__QueryFeed(path,
                                    'attachments',
                                    document_id,
                                    result_fn,
                                    create_fn,
                                    query,
                                    options), self.last_response_headers
        return query_iterator.QueryIterator(options, fetch_fn)


    def ReadMedia(self, media_link):
        """Reads a media.

        When self.connection_policy.MediaReadMode ==
        documents.MediaReadMode.Streamed, returns a file-like stream object;
        otherwise, returns a str.

        :Parameters:
            - `media_link`: str, the link to the media.

        :Returns:
            str or file-link stream object

        """
        default_headers = self.default_headers
        url_connection = self.url_connection
        path = '/' + media_link
        media_id = base.GetIdFromLink(media_link)
        attachment_id = base.GetAttachmentIdFromMediaId(media_id)
        headers = base.GetHeaders(self,
                                  default_headers,
                                  'get',
                                  path,
                                  attachment_id,
                                  'media',
                                  {})

        result, self.last_response_headers = self.__Get(url_connection,
                                                        path,
                                                        headers)
        return result

    def UpdateMedia(self, media_link, readable_stream, options={}):
        """Updates a media and returns it.

        :Parameters:
            - `media_link`: str, the link to the media.
            - `readable_stream`: file-like stream object
            - `options`: dict, the request options for the request.

        :Returns:
            str or file-like stream object

        """
        default_headers = self.default_headers
        initial_headers = base.Extend({}, default_headers)

        # Add required headers slug and content-type in case the body is a stream
        if 'slug' in options:
            initial_headers[http_constants.HttpHeaders.Slug] = options['slug']

        if 'contentType' in options:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                options['contentType'])
        else:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                runtime_constants.MediaTypes.OctetStream)

        url_connection = self.url_connection
        path = '/' + media_link
        media_id = base.GetIdFromLink(media_link)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'put',
                                  path,
                                  media_id,
                                  'media',
                                  options)

        result, self.last_response_headers = self.__Put(url_connection,
                                                        path,
                                                        readable_stream,
                                                        headers)
        return result

    def ReplaceAttachment(self, attachment_link, attachment, options={}):
        """Replaces an attachment and returns it.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `attachment`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + attachment_link
        attachment_id = base.GetIdFromLink(attachment_link)
        return self.Replace(attachment,
                            path,
                            'attachments',
                            attachment_id,
                            None,
                            options)

    def DeleteAttachment(self, attachment_link, options={}):
        """Deletes an attachment.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + attachment_link
        attachment_id = base.GetIdFromLink(attachment_link)
        return self.DeleteResource(path,
                                   'attachments',
                                   attachment_id,
                                   None,
                                   options)

    def ReplaceTrigger(self, trigger_link, trigger, options={}):
        """Replaces a trigger and returns it.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `trigger`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        trigger = trigger.copy()
        if 'serverScript' in trigger:
            trigger['body'] = str(trigger['serverScript'])
        elif 'body' in trigger:
            trigger['body'] = str(trigger['body'])
            
        path = '/' + trigger_link
        trigger_id = base.GetIdFromLink(trigger_link)
        return self.Replace(trigger,
                            path,
                            'triggers',
                            trigger_id,
                            None,
                            options)

    def DeleteTrigger(self, trigger_link, options={}):
        """Deletes a trigger.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + trigger_link
        trigger_id = base.GetIdFromLink(trigger_link)
        return self.DeleteResource(path,
                                   'triggers',
                                   trigger_id,
                                   None,
                                   options)

    def ReplaceUserDefinedFunction(self, udf_link, udf, options={}):
        """Replaces a user defined function and returns it.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `udf`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        udf = udf.copy()
        if 'serverScript' in udf:
            udf['body'] = str(udf['serverScript'])
        elif 'body' in udf:
            udf['body'] = str(udf['body'])

        path = '/' + udf_link
        udf_id = base.GetIdFromLink(udf_link)
        return self.Replace(udf,
                            path,
                            'udfs',
                            udf_id,
                            None,
                            options)

    def DeleteUserDefinedFunction(self, udf_link, options={}):
        """Deletes a user defined function.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + udf_link
        udf_id = base.GetIdFromLink(udf_link)
        return self.DeleteResource(path,
                                   'udfs',
                                   udf_id,
                                   None,
                                   options)

    def ExecuteStoredProcedure(self, sproc_link, params):
        """Executes a store procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `params`: dict, list or None

        :Returns:
            dict

        """
        default_headers = self.default_headers
        initial_headers = {
            http_constants.HttpHeaders.Accept: (
                runtime_constants.MediaTypes.Json)
        }

        initial_headers = base.Extend(initial_headers, default_headers)
        if params and not type(params) is list:
            params = [params]

        url_connection = self.url_connection
        path = '/' + sproc_link
        sproc_id = base.GetIdFromLink(sproc_link)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  sproc_id,
                                  'sprocs',
                                  {})

        result, self.last_response_headers = self.__Post(url_connection,
                                                         path,
                                                         params,
                                                         headers)
        return result

    def ReplaceStoredProcedure(self, sproc_link, sproc, options={}):
        """Replaces a stored procedure and returns it.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `sproc`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        sproc = sproc.copy()
        if 'serverScript' in sproc:
            sproc['body'] = str(sproc['serverScript'])
        elif 'body' in sproc:
            sproc['body'] = str(sproc['body'])

        path = '/' + sproc_link
        sproc_id = base.GetIdFromLink(sproc_link)
        return self.Replace(sproc,
                            path,
                            'sprocs',
                            sproc_id,
                            None,
                            options)

    def DeleteStoredProcedure(self, sproc_link, options={}):
        """Deletes a stored procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + sproc_link
        sproc_id = base.GetIdFromLink(sproc_link)
        return self.DeleteResource(path,
                                   'sprocs',
                                   sproc_id,
                                   None,
                                   options)

    def DeleteConflict(self, conflict_link, options={}):
        """Deletes a conflict.

        :Parameters:
            - `conflict_link`: str, the link to the conflict.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        path = '/' + conflict_link
        conflict_id = base.GetIdFromLink(conflict_link)
        return self.DeleteResource(path,
                                   'conflicts',
                                   conflict_id,
                                   None,
                                   options)

    def GetDatabaseAccount(self):
        """Gets database account info.
        :Returns:
            documents.DatabaseAccount
        """
        default_headers = self.default_headers
        initial_headers = base.Extend({ }, default_headers)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'get',
                                  '',  # path
                                  '',  # id
                                  '',  # type
                                  {});
        result, self.last_response_headers = self.__Get(self.url_connection,
                                                        '',
                                                        headers)
        database_account = documents.DatabaseAccount()
        database_account.DatabasesLink = '/dbs/'
        database_account.MediaLink = '/media/'
        if (http_constants.HttpHeaders.MaxMediaStorageUsageInMB in
            self.last_response_headers):
            database_account.MaxMediaStorageUsageInMB = (
                self.last_response_headers[
                    http_constants.HttpHeaders.MaxMediaStorageUsageInMB])
        if (http_constants.HttpHeaders.CurrentMediaStorageUsageInMB in
            self.last_response_headers):
            database_account.CurrentMediaStorageUsageInMB = (
                self.last_response_headers[
                    http_constants.HttpHeaders.CurrentMediaStorageUsageInMB])
        if (http_constants.HttpHeaders.DatabaseAccountCapacityUnitsConsumed in
            self.last_response_headers):
            database_account.CapacityUnitsConsumed = self.last_response_headers[
                http_constants.HttpHeaders.DatabaseAccountCapacityUnitsConsumed]
        if (http_constants.HttpHeaders.DatabaseAccountCapacityUnitsProvisioned
            in
            self.last_response_headers):
            database_account.CapacityUnitsProvisioned = (
                self.last_response_headers[
                    http_constants.HttpHeaders.
                    DatabaseAccountCapacityUnitsProvisioned])
        if (http_constants.HttpHeaders.
                DatabaseAccountConsumedDocumentStorageInMB in
            self.last_response_headers):
            database_account.ConsumedDocumentStorageInMB = (
                self.last_response_headers[
                    http_constants.HttpHeaders.
                    DatabaseAccountConsumedDocumentStorageInMB])
        if (http_constants.HttpHeaders.
                DatabaseAccountReservedDocumentStorageInMB in
            self.last_response_headers):
            database_account.ReservedDocumentStorageInMB = (
               self.last_response_headers[
                    http_constants.HttpHeaders.
                    DatabaseAccountReservedDocumentStorageInMB])
        if (http_constants.HttpHeaders.
                DatabaseAccountProvisionedDocumentStorageInMB in
            self.last_response_headers):
            database_account.ProvisionedDocumentStorageInMB = (
                self.last_response_headers[
                    http_constants.HttpHeaders.
                    DatabaseAccountProvisionedDocumentStorageInMB])
        database_account.ConsistencyPolicy = result['userConsistencyPolicy']
        return database_account

    def Create(self, body, path, type, id, initial_headers, options={}):
        """Creates a DocumentDB resource and returns it.

        :Parameters:
            - `body`: dict
            - `path`: str
            - `type`: str
            - `id`: str
            - `initial_headers`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  id,
                                  type,
                                  options)
        result, self.last_response_headers = self.__Post(self.url_connection,
                                                         path,
                                                         body,
                                                         headers)
        return result

    def Replace(self, resource, path, type, id, initial_headers, options={}):
        """Replaces a DocumentDB resource and returns it.

        :Parameters:
            - `resource`: dict
            - `path`: str
            - `type`: str
            - `id`: str
            - `initial_headers`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'put',
                                  path,
                                  id,
                                  type,
                                  options)
        result, self.last_response_headers = self.__Put(self.url_connection,
                                                        path,
                                                        resource,
                                                        headers)
        return result

    def Read(self, path, type, id, initial_headers, options={}):
        """Reads a DocumentDB resource and returns it.

        :Parameters:
            - `path`: str
            - `type`: str
            - `id`: str
            - `initial_headers`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'get',
                                  path,
                                  id,
                                  type,
                                  options)
        result, self.last_response_headers = self.__Get(self.url_connection,
                                                        path,
                                                        headers)
        return result

    def DeleteResource(self, path, type, id, initial_headers, options={}):
        """Deletes a DocumentDB resource and returns it.

        :Parameters:
            - `path`: str
            - `type`: str
            - `id`: str
            - `initial_headers`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'delete',
                                  path,
                                  id,
                                  type,
                                  options)
        result, self.last_response_headers = self.__Delete(self.url_connection,
                                                           path,
                                                           headers)
        return result

    def __Get(self, url, path, headers):
        """DocumentDB 'GET' http request.

        :Parameters:
            - `url`: str
            - `path`: str
            - `headers`: dict

        :Returns:
            tuple (result, headers), and result and headers are both
            dicts

        """
        return synchronized_request.SynchronizedRequest(self.connection_policy,
                                                        'GET',
                                                        url,
                                                        path,
                                                        None,
                                                        None,
                                                        headers)

    def __Post(self, url, path, body, headers):
        """DocumentDB 'POST' http request.

        :Parameters:
            - `url`: str
            - `path`: str
            - `body`: str, unicode or dict
            - `headers`: dict

        :Returns:
            tuple (result, headers), and result and headers are both
            dicts

        """
        return synchronized_request.SynchronizedRequest(self.connection_policy,
                                                        'POST',
                                                        url,
                                                        path,
                                                        body,
                                                        query_params=None,
                                                        headers=headers)

    def __Put(self, url, path, body, headers):
        """DocumentDB 'PUT' http request.

        :Parameters:
            - `url`: str
            - `path`: str
            - `body`: str, unicode or dict
            - `headers`: dict

        :Returns:
            tuple (result, headers), and result and headers are both
            dicts

        """
        return synchronized_request.SynchronizedRequest(self.connection_policy,
                                                        'PUT',
                                                        url,
                                                        path,
                                                        body,
                                                        query_params=None,
                                                        headers=headers)

    def __Delete(self, url, path, headers):
        """DocumentDB 'DELETE' http request.

        :Parameters:
            - `url`: str
            - `path`: str
            - `headers`: dict

        :Returns:
            tuple (result, headers), and result and headers are both
            dicts

        """
        return synchronized_request.SynchronizedRequest(self.connection_policy,
                                                        'DELETE',
                                                        url,
                                                        path,
                                                        request_data=None,
                                                        query_params=None,
                                                        headers=headers)

    def __QueryFeed(self,
                    path,
                    type,
                    id,
                    result_fn,
                    create_fn,
                    query,
                    options={}):
        """Query for more than one DocumentDB resources.

        :Parameters:
            - `path`: str
            - `type`: str
            - `id`: str
            - `result_fn`: function
            - `create_fn`: function
            - `query`: str
            - `options`: dict, the request options for the request.

        :Returns:
            list

        """
        def __GetBodiesFromQueryResult(result):
            bodies = []
            if query:
                bodies = result_fn(result)
            else:
                for body in result_fn(result):
                    bodies.append(create_fn(self, body))
            return bodies

        url_connection = self.url_connection
        initial_headers = self.default_headers.copy()
        # Copy to make sure that default_headers won't be changed.
        if query == None:
            headers = base.GetHeaders(self,
                                      initial_headers,
                                      'get',
                                      path,
                                      id,
                                      type,
                                      options)
            result, self.last_response_headers = self.__Get(url_connection,
                                                            path,
                                                            headers)
            return __GetBodiesFromQueryResult(result)
        else:
            initial_headers[http_constants.HttpHeaders.IsQuery] = 'true'
            if 'jpath' in options and options['jpath']:
                initial_headers[http_constants.HttpHeaders.Query] = query
                headers = base.GetHeaders(self,
                                          initial_headers,
                                          'get',
                                          path,
                                          id,
                                          type,
                                          options)
                result, self.last_response_headers = self.__Get(url_connection,
                                                                path,
                                                                headers)
                return __GetBodiesFromQueryResult(result)
            else:
                initial_headers[http_constants.HttpHeaders.ContentType] = (
                    runtime_constants.MediaTypes.SQL)
                headers = base.GetHeaders(self,
                                          initial_headers,
                                          'post',
                                          path,
                                          id,
                                          type,
                                          options)
                result, self.last_response_headers = self.__Post(url_connection,
                                                                 path,
                                                                 query,
                                                                 headers)
                return __GetBodiesFromQueryResult(result)

    def __enter__(self):
        """To support `with` operator.

        :Returns:
            document_client.DocumentClient

        """
        return self

    def __exit__(self, e_type, e_value, e_trace):
        """To support `with` operator.

        :Parameters:
            - `e_type`: the type of exception
            - `e_value`: the exception instance raised.
            - `e_trance`: a traceback instance.

        """
        pass