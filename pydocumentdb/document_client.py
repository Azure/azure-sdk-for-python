#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Document client class for the Azure DocumentDB database service.
"""

import requests

import six
import pydocumentdb.base as base
import pydocumentdb.documents as documents
import pydocumentdb.constants as constants
import pydocumentdb.http_constants as http_constants
import pydocumentdb.query_iterable as query_iterable
import pydocumentdb.runtime_constants as runtime_constants
import pydocumentdb.synchronized_request as synchronized_request
import pydocumentdb.global_endpoint_manager as global_endpoint_manager
import pydocumentdb.routing.routing_map_provider as routing_map_provider
import pydocumentdb.session as session
import pydocumentdb.utils as utils

class DocumentClient(object):
    """Represents a document client.

    Provides a client-side logical representation of the Azure DocumentDB
    service. This client is used to configure and execute requests against the
    service.

    The service client encapsulates the endpoint and credentials used to access
    the DocumentDB service.
    """

    class _QueryCompatibilityMode:
        Default = 0
        Query = 1
        SqlQuery = 2

    # default number precisions
    _DefaultNumberHashPrecision = 3
    _DefaultNumberRangePrecision = -1

    # default string precision
    _DefaultStringHashPrecision = 3
    _DefaultStringRangePrecision = -1

    def __init__(self,
                 url_connection,
                 auth,
                 connection_policy=None,
                 consistency_level=documents.ConsistencyLevel.Session):
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
            self.master_key = auth.get('masterKey')
            self.resource_tokens = auth.get('resourceTokens')

            if auth.get('permissionFeed'):
                self.resource_tokens = {}
                for permission_feed in auth['permissionFeed']:
                    resource_parts = permission_feed['resource'].split('/')
                    id = resource_parts[-1]
                    self.resource_tokens[id] = permission_feed['_token']

        self.connection_policy = (connection_policy or
                                  documents.ConnectionPolicy())

        self.partition_resolvers = {}

        self.partition_key_definition_cache = {}

        self.default_headers = {
            http_constants.HttpHeaders.CacheControl: 'no-cache',
            http_constants.HttpHeaders.Version:
                http_constants.Versions.CurrentVersion,
            http_constants.HttpHeaders.UserAgent:
                utils._get_user_agent(),
            # For single partition query with aggregate functions we would try to accumulate the results on the SDK.
            # We need to set continuation as not expected.
            http_constants.HttpHeaders.IsContinuationExpected: False
        }

        if consistency_level != None:
            self.default_headers[
                http_constants.HttpHeaders.ConsistencyLevel] = consistency_level

        # Keeps the latest response headers from server.
        self.last_response_headers = None

        if consistency_level == documents.ConsistencyLevel.Session:
            '''create a session - this is maintained only if the default consistency level
            on the client is set to session, or if the user explicitly sets it as a property
            via setter'''
            self.session = session.Session(self.url_connection)
        else:
            self.session = None

        self._global_endpoint_manager = global_endpoint_manager._GlobalEndpointManager(self)

        # creating a requests session used for connection pooling and re-used by all requests
        self._requests_session = requests.Session()

        # Query compatibility mode.
        # Allows to specify compatibility mode used by client when making query requests. Should be removed when
        # application/sql is no longer supported.
        self._query_compatibility_mode = DocumentClient._QueryCompatibilityMode.Default

        # Routing map provider
        self._routing_map_provider = routing_map_provider._SmartRoutingMapProvider(self)

    @property
    def Session(self):
        """ Gets the session object from the client """
        return self.session

    @Session.setter
    def Session(self, session):
        """ Sets a session object on the document client
            This will override the existing session
        """
        self.session = session

    @property
    def WriteEndpoint(self):
        """Gets the curent write endpoint for a geo-replicated database account.
        """
        return self._global_endpoint_manager.WriteEndpoint

    @property
    def ReadEndpoint(self):
        """Gets the curent read endpoint for a geo-replicated database account.
        """
        return self._global_endpoint_manager.ReadEndpoint

    def RegisterPartitionResolver(self, database_link, partition_resolver):
        """Registers the partition resolver associated with the database link

        :Parameters:
            - `database_link`: str, database Self Link or ID based link
            - `partition_resolver`: object, an instance of PartitionResolver
        
        """
        if not database_link:
            raise ValueError("database_link is None or empty.")

        if partition_resolver is None:
            raise ValueError("partition_resolver is None.")

        self.partition_resolvers = {base.TrimBeginningAndEndingSlashes(database_link): partition_resolver}


    def GetPartitionResolver(self, database_link):
        """Gets the partition resolver associated with the database link

        :Parameters:
            - `database_link`: str, database self link or ID based link

        :Returns:
            object, an instance of PartitionResolver
        
        """
        if not database_link:
            raise ValueError("database_link is None or empty.")

        return self.partition_resolvers.get(base.TrimBeginningAndEndingSlashes(database_link))

        
    def CreateDatabase(self, database, options=None):
        """Creates a database.

        :Parameters:
            - `database`: dict, the Azure DocumentDB database to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(database)
        path = '/dbs'
        return self.Create(database, path, 'dbs', None, None, options)

    def ReadDatabase(self, database_link, options=None):
        """Reads a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link)
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return self.Read(path, 'dbs', database_id, None, options)

    def ReadDatabases(self, options=None):
        """Reads all databases.

        :Parameters:
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryDatabases(None, options)

    def QueryDatabases(self, query, options=None):
        """Queries databases.

        :Parameters:
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        def fetch_fn(options):
            return self.__QueryFeed('/dbs',
                                    'dbs',
                                    '',
                                    lambda r: r['Databases'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def ReadCollections(self, database_link, options=None):
        """Reads all collections in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryCollections(database_link, None, options)

    def QueryCollections(self, database_link, query, options=None):
        """Queries collections in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link, 'colls')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'colls',
                                    database_id,
                                    lambda r: r['DocumentCollections'],
                                    lambda _, body: body,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def CreateCollection(self, database_link, collection, options=None):
        """Creates a collection in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `collection`: dict, the Azure DocumentDB collection to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(collection)
        path = base.GetPathFromLink(database_link, 'colls')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return self.Create(collection,
                           path,
                           'colls',
                           database_id,
                           None,
                           options)

    def ReplaceCollection(self, collection_link, collection, options=None):
        """Replaces a collection and return it.

        :Parameters:
            - `collection_link`: str, the link to the collection entity.
            - `collection`: dict, the collection to be used.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(collection)
        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return self.Replace(collection,
                            path,
                            'colls',
                            collection_id,
                            None,
                            options)

    def ReadCollection(self, collection_link, options=None):
        """Reads a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return self.Read(path,
                         'colls',
                         collection_id,
                         None,
                         options)

    def CreateUser(self, database_link, user, options=None):
        """Creates a user.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `user`: dict, the Azure DocumentDB user to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        database_id, path = self._GetDatabaseIdWithPathForUser(database_link, user)
        return self.Create(user,
                           path,
                           'users',
                           database_id,
                           None,
                           options)

    def UpsertUser(self, database_link, user, options=None):
        """Upserts a user.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `user`: dict, the Azure DocumentDB user to upsert.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        database_id, path = self._GetDatabaseIdWithPathForUser(database_link, user)
        return self.Upsert(user,
                           path,
                           'users',
                           database_id,
                           None,
                           options)

    def _GetDatabaseIdWithPathForUser(self, database_link, user):
        DocumentClient.__ValidateResource(user)
        path = base.GetPathFromLink(database_link, 'users')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return database_id, path
    

    def ReadUser(self, user_link, options=None):
        """Reads a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return self.Read(path, 'users', user_id, None, options)

    def ReadUsers(self, database_link, options=None):
        """Reads all users in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.
        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryUsers(database_link, None, options)

    def QueryUsers(self, database_link, query, options=None):
        """Queries users in a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link, 'users')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'users',
                                    database_id,
                                    lambda r: r['Users'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def DeleteDatabase(self, database_link, options=None):
        """Deletes a database.

        :Parameters:
            - `database_link`: str, the link to the database.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link)
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return self.DeleteResource(path,
                                   'dbs',
                                   database_id,
                                   None,
                                   options)

    def CreatePermission(self, user_link, permission, options=None):
        """Creates a permission for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `permission`: dict, the Azure DocumentDB user permission to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path, user_id = self._GetUserIdWithPathForPermission(permission, user_link)
        return self.Create(permission,
                           path,
                           'permissions',
                           user_id,
                           None,
                           options)

    def UpsertPermission(self, user_link, permission, options=None):
        """Upserts a permission for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `permission`: dict, the Azure DocumentDB user permission to upsert.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path, user_id = self._GetUserIdWithPathForPermission(permission, user_link)
        return self.Upsert(permission,
                            path,
                            'permissions',
                            user_id,
                            None,
                            options)

    def _GetUserIdWithPathForPermission(self, permission, user_link):
        DocumentClient.__ValidateResource(permission)
        path = base.GetPathFromLink(user_link, 'permissions')
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return path, user_id


    def ReadPermission(self, permission_link, options=None):
        """Reads a permission.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(permission_link)
        permission_id = base.GetResourceIdOrFullNameFromLink(permission_link)
        return self.Read(path,
                         'permissions',
                          permission_id,
                          None,
                          options)

    def ReadPermissions(self, user_link, options=None):
        """Reads all permissions for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryPermissions(user_link, None, options)

    def QueryPermissions(self, user_link, query, options=None):
        """Queries permissions for a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(user_link, 'permissions')
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'permissions',
                                    user_id,
                                    lambda r: r['Permissions'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def ReplaceUser(self, user_link, user, options=None):
        """Replaces a user and return it.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `user`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(user)
        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return self.Replace(user,
                            path,
                            'users',
                            user_id,
                            None,
                            options)

    def DeleteUser(self, user_link, options=None):
        """Deletes a user.

        :Parameters:
            - `user_link`: str, the link to the user entity.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return self.DeleteResource(path,
                                   'users',
                                   user_id,
                                   None,
                                   options)

    def ReplacePermission(self, permission_link, permission, options=None):
        """Replaces a permission and return it.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `permission`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(permission)
        path = base.GetPathFromLink(permission_link)
        permission_id = base.GetResourceIdOrFullNameFromLink(permission_link)
        return self.Replace(permission,
                            path,
                            'permissions',
                            permission_id,
                            None,
                            options)

    def DeletePermission(self, permission_link, options=None):
        """Deletes a permission.

        :Parameters:
            - `permission_link`: str, the link to the permission.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(permission_link)
        permission_id = base.GetResourceIdOrFullNameFromLink(permission_link)
        return self.DeleteResource(path,
                                   'permissions',
                                   permission_id,
                                   None,
                                   options)

    def ReadDocuments(self, collection_link, feed_options=None):
        """Reads all documents in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `feed_options`: dict

        :Returns:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self.QueryDocuments(collection_link, None, feed_options)

    def QueryDocuments(self, database_or_collection_link, query, options=None, partition_key=None):
        """Queries documents in a collection.

        :Parameters:
            - `database_or_collection_link`: str, the link to the database when using partitioning, otherwise link to the document collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.
            - `partition_key`: str, partition key for the query(default value None)

        :Returns:
            query_iterable.QueryIterable

        """
        database_or_collection_link = base.TrimBeginningAndEndingSlashes(database_or_collection_link)

        if options is None:
            options = {}

        if(base.IsDatabaseLink(database_or_collection_link)):
            # Python doesn't have a good way of specifying an overloaded constructor, and this is how it's generally overloaded constructors are specified(by calling a @classmethod) and returning the 'self' instance
            return query_iterable.QueryIterable.PartitioningQueryIterable(self, query, options, database_or_collection_link, partition_key)
        else:    
            path = base.GetPathFromLink(database_or_collection_link, 'docs')
            collection_id = base.GetResourceIdOrFullNameFromLink(database_or_collection_link)
            def fetch_fn(options):
                return self.__QueryFeed(path,
                                        'docs',
                                        collection_id,
                                        lambda r: r['Documents'],
                                        lambda _, b: b,
                                        query,
                                        options), self.last_response_headers
            return query_iterable.QueryIterable(self, query, options, fetch_fn, database_or_collection_link)

    def _ReadPartitionKeyRanges(self, collection_link, feed_options=None):
        """Reads Partition Key Ranges.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `feed_options`: dict

        :Returns:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self._QueryPartitionKeyRanges(collection_link, None, feed_options)

    def _QueryPartitionKeyRanges(self, collection_link, query, options=None):
        """Queries Partition Key Ranges in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, 'pkranges')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'pkranges',
                                    collection_id,
                                    lambda r: r['PartitionKeyRanges'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def CreateDocument(self, database_or_collection_link, document, options=None):
        """Creates a document in a collection.

        :Parameters:
            - `database_or_collection_link`: str, the link to the database when using partitioning, otherwise link to the document collection.
            - `document`: dict, the Azure DocumentDB document to create.
            - `options`: dict, the request options for the request.
            - `options['disableAutomaticIdGeneration']`: bool, disables the
              automatic id generation. If id is missing in the body and this
              option is true, an error will be returned.

        :Returns:
            dict

        """
        # Python’s default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the method
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}
        
        # We check the link to be document collection link since it can be database link in case of client side partitioning
        if(base.IsDocumentCollectionLink(database_or_collection_link)):
            options = self._AddPartitionKey(database_or_collection_link, document, options)

        collection_id, document, path = self._GetCollectionIdWithPathForDocument(database_or_collection_link, document, options)
        return self.Create(document,
                           path,
                           'docs',
                           collection_id,
                           None,
                           options)

    def UpsertDocument(self, database_or_collection_link, document, options=None):
        """Upserts a document in a collection.

        :Parameters:
            - `database_or_collection_link`: str, the link to the database when using partitioning, otherwise link to the document collection.
            - `document`: dict, the Azure DocumentDB document to upsert.
            - `options`: dict, the request options for the request.
            - `options['disableAutomaticIdGeneration']`: bool, disables the
              automatic id generation. If id is missing in the body and this
              option is true, an error will be returned.

        :Returns:
            dict

        """
        # Python’s default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the method
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # We check the link to be document collection link since it can be database link in case of client side partitioning
        if(base.IsDocumentCollectionLink(database_or_collection_link)):
            options = self._AddPartitionKey(database_or_collection_link, document, options)

        collection_id, document, path = self._GetCollectionIdWithPathForDocument(database_or_collection_link, document, options)
        return self.Upsert(document,
                           path,
                           'docs',
                           collection_id,
                           None,
                           options)

    PartitionResolverErrorMessage = "Couldn't find any partition resolvers for the database link provided. Ensure that the link you used when registering the partition resolvers matches the link provided or you need to register both types of database link(self link as well as ID based link)."

    # Gets the collection id and path for the document
    def _GetCollectionIdWithPathForDocument(self, database_or_collection_link, document, options):
        
        if not database_or_collection_link:
            raise ValueError("database_or_collection_link is None or empty.")

        if document is None:
            raise ValueError("document is None.")

        DocumentClient.__ValidateResource(document)
        document = document.copy()
        if (not document.get('id') and
            not options.get('disableAutomaticIdGeneration')):
            document['id'] = base.GenerateGuidId()
        
        collection_link = database_or_collection_link

        if(base.IsDatabaseLink(database_or_collection_link)):
            partition_resolver = self.GetPartitionResolver(database_or_collection_link)
        
            if(partition_resolver != None):
                collection_link = partition_resolver.ResolveForCreate(document)
            else:
                raise ValueError(DocumentClient.PartitionResolverErrorMessage)
        
        path = base.GetPathFromLink(collection_link, 'docs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, document, path
    
    def ReadDocument(self, document_link, options=None):
        """Reads a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        return self.Read(path,
                         'docs',
                         document_id,
                         None,
                         options)

    def ReadTriggers(self, collection_link, options=None):
        """Reads all triggers in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryTriggers(collection_link, None, options)

    def QueryTriggers(self, collection_link, query, options=None):
        """Queries triggers in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, 'triggers')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'triggers',
                                    collection_id,
                                    lambda r: r['Triggers'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def CreateTrigger(self, collection_link, trigger, options=None):
        """Creates a trigger in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `trigger`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, trigger = self._GetCollectionIdWithPathForTrigger(collection_link, trigger)
        return self.Create(trigger,
                           path,
                           'triggers',
                           collection_id,
                           None,
                           options)

    def UpsertTrigger(self, collection_link, trigger, options=None):
        """Upserts a trigger in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `trigger`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, trigger = self._GetCollectionIdWithPathForTrigger(collection_link, trigger)
        return self.Upsert(trigger,
                           path,
                           'triggers',
                           collection_id,
                           None,
                           options)

    def _GetCollectionIdWithPathForTrigger(self, collection_link, trigger):
        DocumentClient.__ValidateResource(trigger)
        trigger = trigger.copy()
        if  trigger.get('serverScript'):
            trigger['body'] = str(trigger.pop('serverScript', ''))
        elif trigger.get('body'):
            trigger['body'] = str(trigger['body'])
        
        path = base.GetPathFromLink(collection_link, 'triggers')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, trigger
    

    def ReadTrigger(self, trigger_link, options=None):
        """Reads a trigger.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(trigger_link)
        trigger_id = base.GetResourceIdOrFullNameFromLink(trigger_link)
        return self.Read(path, 'triggers', trigger_id, None, options)

    def ReadUserDefinedFunctions(self, collection_link, options=None):
        """Reads all user defined functions in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryUserDefinedFunctions(collection_link, None, options)

    def QueryUserDefinedFunctions(self, collection_link, query, options=None):
        """Queries user defined functions in a collection.

        :Parameters:
            - `collection_link`: str, the link to the collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, 'udfs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'udfs',
                                    collection_id,
                                    lambda r: r['UserDefinedFunctions'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def CreateUserDefinedFunction(self, collection_link, udf, options=None):
        """Creates a user defined function in a collection.

        :Parameters:
            - `collection_link`: str, the link to the collection.
            - `udf`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, udf = self._GetCollectionIdWithPathForUDF(collection_link, udf)
        return self.Create(udf,
                           path,
                           'udfs',
                           collection_id,
                           None,
                           options)

    def UpsertUserDefinedFunction(self, collection_link, udf, options=None):
        """Upserts a user defined function in a collection.

        :Parameters:
            - `collection_link`: str, the link to the collection.
            - `udf`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, udf = self._GetCollectionIdWithPathForUDF(collection_link, udf)
        return self.Upsert(udf,
                           path,
                           'udfs',
                           collection_id,
                           None,
                           options)

    def _GetCollectionIdWithPathForUDF(self, collection_link, udf):
        DocumentClient.__ValidateResource(udf)
        udf = udf.copy()
        if udf.get('serverScript'):
            udf['body'] = str(udf.pop('serverScript', ''))
        elif udf.get('body'):
            udf['body'] = str(udf['body'])
        
        path = base.GetPathFromLink(collection_link, 'udfs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, udf
    

    def ReadUserDefinedFunction(self, udf_link, options=None):
        """Reads a user defined function.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        return self.Read(path, 'udfs', udf_id, None, options)

    def ReadStoredProcedures(self, collection_link, options=None):
        """Reads all store procedures in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryStoredProcedures(collection_link, None, options)

    def QueryStoredProcedures(self, collection_link, query, options=None):
        """Queries stored procedures in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, 'sprocs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'sprocs',
                                    collection_id,
                                    lambda r: r['StoredProcedures'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def CreateStoredProcedure(self, collection_link, sproc, options=None):
        """Creates a stored procedure in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `sproc`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, sproc = self._GetCollectionIdWithPathForSproc(collection_link, sproc)
        return self.Create(sproc,
                           path,
                           'sprocs',
                           collection_id,
                           None,
                           options)

    def UpsertStoredProcedure(self, collection_link, sproc, options=None):
        """Upserts a stored procedure in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `sproc`: str
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, sproc = self._GetCollectionIdWithPathForSproc(collection_link, sproc)
        return self.Upsert(sproc,
                           path,
                           'sprocs',
                           collection_id,
                           None,
                           options)

    def _GetCollectionIdWithPathForSproc(self, collection_link, sproc):
        DocumentClient.__ValidateResource(sproc)
        sproc = sproc.copy()
        if sproc.get('serverScript'):
            sproc['body'] = str(sproc.pop('serverScript', ''))
        elif sproc.get('body'):
            sproc['body'] = str(sproc['body'])
        path = base.GetPathFromLink(collection_link, 'sprocs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, sproc
    

    def ReadStoredProcedure(self, sproc_link, options=None):
        """Reads a stored procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        return self.Read(path, 'sprocs', sproc_id, None, options)

    def ReadConflicts(self, collection_link, feed_options=None):
        """Reads conflicts.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `feed_options`: dict

        :Returns:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self.QueryConflicts(collection_link, None, feed_options)

    def QueryConflicts(self, collection_link, query, options=None):
        """Queries conflicts in a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, 'conflicts')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'conflicts',
                                    collection_id,
                                    lambda r: r['Conflicts'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def ReadConflict(self, conflict_link, options=None):
        """Reads a conflict.

        :Parameters:
            - `conflict_link`: str, the link to the conflict.
            - `opitions`: dict

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(conflict_link)
        conflict_id = base.GetResourceIdOrFullNameFromLink(conflict_link)
        return self.Read(path,
                         'conflicts',
                         conflict_id,
                         None,
                         options)

    def DeleteCollection(self, collection_link, options=None):
        """Deletes a collection.

        :Parameters:
            - `collection_link`: str, the link to the document collection.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return self.DeleteResource(path,
                                   'colls',
                                   collection_id,
                                   None,
                                   options)

    def ReplaceDocument(self, document_link, new_document, options=None):
        """Replaces a document and returns it.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `new_document`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        DocumentClient.__ValidateResource(new_document)
        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        
        # Python’s default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the function so that it remains local
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # Extract the document collection link and add the partition key to options
        collection_link = base.GetDocumentCollectionLink(document_link)
        options = self._AddPartitionKey(collection_link, new_document, options)
        
        return self.Replace(new_document,
                            path,
                            'docs',
                            document_id,
                            None,
                            options)

    def DeleteDocument(self, document_link, options=None):
        """Deletes a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        return self.DeleteResource(path,
                                   'docs',
                                   document_id,
                                   None,
                                   options)

    def CreateAttachment(self, document_link, attachment, options=None):
        """Creates an attachment in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `attachment`: dict, the Azure DocumentDB attachment to create.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        document_id, path = self._GetDocumentIdWithPathForAttachment(attachment, document_link)
        return self.Create(attachment,
                           path,
                           'attachments',
                           document_id,
                           None,
                           options)

    def UpsertAttachment(self, document_link, attachment, options=None):
        """Upserts an attachment in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `attachment`: dict, the Azure DocumentDB attachment to upsert.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        document_id, path = self._GetDocumentIdWithPathForAttachment(attachment, document_link)
        return self.Upsert(attachment,
                           path,
                           'attachments',
                           document_id,
                           None,
                           options)

    def _GetDocumentIdWithPathForAttachment(self, attachment, document_link):
        DocumentClient.__ValidateResource(attachment)
        path = base.GetPathFromLink(document_link, 'attachments')
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        return document_id, path

    def CreateAttachmentAndUploadMedia(self,
                                       document_link,
                                       readable_stream,
                                       options=None):
        """Creates an attachment and upload media.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `readable_stream`: file-like stream object
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        document_id, initial_headers, path = self._GetDocumentIdWithPathForAttachmentMedia(document_link, options)
        return self.Create(readable_stream,
                           path,
                           'attachments',
                           document_id,
                           initial_headers,
                           options)

    def UpsertAttachmentAndUploadMedia(self,
                                       document_link,
                                       readable_stream,
                                       options=None):
        """Upserts an attachment and upload media.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `readable_stream`: file-like stream object
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        document_id, initial_headers, path = self._GetDocumentIdWithPathForAttachmentMedia(document_link, options)
        return self.Upsert(readable_stream,
                           path,
                           'attachments',
                           document_id,
                           initial_headers,
                           options)

    def _GetDocumentIdWithPathForAttachmentMedia(self, document_link, options):
        initial_headers = dict(self.default_headers)
        
        # Add required headers slug and content-type.
        if options.get('slug'):
            initial_headers[http_constants.HttpHeaders.Slug] = options['slug']
        
        if options.get('contentType'):
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                options['contentType'])
        else:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                runtime_constants.MediaTypes.OctetStream)
        
        path = base.GetPathFromLink(document_link, 'attachments')
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        return document_id, initial_headers, path


    def ReadAttachment(self, attachment_link, options=None):
        """Reads an attachment.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(attachment_link)
        attachment_id = base.GetResourceIdOrFullNameFromLink(attachment_link)
        return self.Read(path,
                         'attachments',
                         attachment_id,
                         None,
                         options)

    def ReadAttachments(self, document_link, options=None):
        """Reads all attachments in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryAttachments(document_link, None, options)

    def QueryAttachments(self, document_link, query, options=None):
        """Queries attachments in a document.

        :Parameters:
            - `document_link`: str, the link to the document.
            - `query`: str or dict.
            - `options`: dict, the request options for the request.

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(document_link, 'attachments')
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)

        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    'attachments',
                                    document_id,
                                    lambda r: r['Attachments'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)


    def ReadMedia(self, media_link):
        """Reads a media.

        When self.connection_policy.MediaReadMode ==
        documents.MediaReadMode.Streamed, returns a file-like stream object;
        otherwise, returns a str.

        :Parameters:
            - `media_link`: str, the link to the media.

        :Returns:
            str or file-like stream object

        """
        default_headers = self.default_headers
        # ReadMedia will always use WriteEndpoint since it's not replicated in readable Geo regions
        url_connection = self._global_endpoint_manager.WriteEndpoint

        path = base.GetPathFromLink(media_link)
        media_id = base.GetResourceIdOrFullNameFromLink(media_link)
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

    def UpdateMedia(self, media_link, readable_stream, options=None):
        """Updates a media and returns it.

        :Parameters:
            - `media_link`: str, the link to the media.
            - `readable_stream`: file-like stream object
            - `options`: dict, the request options for the request.

        :Returns:
            str or file-like stream object

        """
        if options is None:
            options = {}

        initial_headers = dict(self.default_headers)

        # Add required headers slug and content-type in case the body is a stream
        if options.get('slug'):
            initial_headers[http_constants.HttpHeaders.Slug] = options['slug']

        if options.get('contentType'):
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                options['contentType'])
        else:
            initial_headers[http_constants.HttpHeaders.ContentType] = (
                runtime_constants.MediaTypes.OctetStream)

        # UpdateMedia will use WriteEndpoint since it uses PUT operation
        url_connection = self._global_endpoint_manager.WriteEndpoint

        path = base.GetPathFromLink(media_link)
        media_id = base.GetResourceIdOrFullNameFromLink(media_link)
        attachment_id = base.GetAttachmentIdFromMediaId(media_id)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'put',
                                  path,
                                  attachment_id,
                                  'media',
                                  options)

        result, self.last_response_headers = self.__Put(url_connection,
                                                        path,
                                                        readable_stream,
                                                        headers)
        
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def ReplaceAttachment(self, attachment_link, attachment, options=None):
        """Replaces an attachment and returns it.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `attachment`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(attachment)
        path = base.GetPathFromLink(attachment_link)
        attachment_id = base.GetResourceIdOrFullNameFromLink(attachment_link)
        return self.Replace(attachment,
                            path,
                            'attachments',
                            attachment_id,
                            None,
                            options)

    def DeleteAttachment(self, attachment_link, options=None):
        """Deletes an attachment.

        :Parameters:
            - `attachment_link`: str, the link to the attachment.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(attachment_link)
        attachment_id = base.GetResourceIdOrFullNameFromLink(attachment_link)
        return self.DeleteResource(path,
                                   'attachments',
                                   attachment_id,
                                   None,
                                   options)

    def ReplaceTrigger(self, trigger_link, trigger, options=None):
        """Replaces a trigger and returns it.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `trigger`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(trigger)
        trigger = trigger.copy()
        if trigger.get('serverScript'):
            trigger['body'] = str(trigger['serverScript'])
        elif trigger.get('body'):
            trigger['body'] = str(trigger['body'])

        path = base.GetPathFromLink(trigger_link)
        trigger_id = base.GetResourceIdOrFullNameFromLink(trigger_link)
        return self.Replace(trigger,
                            path,
                            'triggers',
                            trigger_id,
                            None,
                            options)

    def DeleteTrigger(self, trigger_link, options=None):
        """Deletes a trigger.

        :Parameters:
            - `trigger_link`: str, the link to the trigger.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(trigger_link)
        trigger_id = base.GetResourceIdOrFullNameFromLink(trigger_link)
        return self.DeleteResource(path,
                                   'triggers',
                                   trigger_id,
                                   None,
                                   options)

    def ReplaceUserDefinedFunction(self, udf_link, udf, options=None):
        """Replaces a user defined function and returns it.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `udf`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(udf)
        udf = udf.copy()
        if udf.get('serverScript'):
            udf['body'] = str(udf['serverScript'])
        elif udf.get('body'):
            udf['body'] = str(udf['body'])

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        return self.Replace(udf,
                            path,
                            'udfs',
                            udf_id,
                            None,
                            options)

    def DeleteUserDefinedFunction(self, udf_link, options=None):
        """Deletes a user defined function.

        :Parameters:
            - `udf_link`: str, the link to the user defined function.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        return self.DeleteResource(path,
                                   'udfs',
                                   udf_id,
                                   None,
                                   options)

    def ExecuteStoredProcedure(self, sproc_link, params, options=None):
        """Executes a store procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `params`: dict, list or None
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        initial_headers = dict(self.default_headers)
        initial_headers.update({
            http_constants.HttpHeaders.Accept: (
                runtime_constants.MediaTypes.Json)
        })

        if params and not type(params) is list:
            params = [params]

        # ExecuteStoredProcedure will use WriteEndpoint since it uses POST operation
        url_connection = self._global_endpoint_manager.WriteEndpoint

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  sproc_id,
                                  'sprocs',
                                  options)

        result, self.last_response_headers = self.__Post(url_connection,
                                                         path,
                                                         params,
                                                         headers)
        return result

    def ReplaceStoredProcedure(self, sproc_link, sproc, options=None):
        """Replaces a stored procedure and returns it.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `sproc`: dict
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        DocumentClient.__ValidateResource(sproc)
        sproc = sproc.copy()
        if sproc.get('serverScript'):
            sproc['body'] = str(sproc['serverScript'])
        elif sproc.get('body'):
            sproc['body'] = str(sproc['body'])

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        return self.Replace(sproc,
                            path,
                            'sprocs',
                            sproc_id,
                            None,
                            options)

    def DeleteStoredProcedure(self, sproc_link, options=None):
        """Deletes a stored procedure.

        :Parameters:
            - `sproc_link`: str, the link to the stored procedure.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        return self.DeleteResource(path,
                                   'sprocs',
                                   sproc_id,
                                   None,
                                   options)

    def DeleteConflict(self, conflict_link, options=None):
        """Deletes a conflict.

        :Parameters:
            - `conflict_link`: str, the link to the conflict.
            - `options`: dict, the request options for the request.

        :Returns:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(conflict_link)
        conflict_id = base.GetResourceIdOrFullNameFromLink(conflict_link)
        return self.DeleteResource(path,
                                   'conflicts',
                                   conflict_id,
                                   None,
                                   options)

    def ReplaceOffer(self, offer_link, offer):
        """Replaces an offer and returns it.

        :Parameters:
            - `offer_link`: str, the link to the offer.
            - `offer`: dict

        :Returns:
            dict

        """
        DocumentClient.__ValidateResource(offer)
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return self.Replace(offer, path, 'offers', offer_id, None, None)

    def ReadOffer(self, offer_link):
        """Reads an offer.

        :Parameters:
            - `offer_link`: str, the link to the offer.

        :Returns:
            dict

        """
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return self.Read(path, 'offers', offer_id, None, {})

    def ReadOffers(self, options=None):
        """Reads all offers.

        :Parameters:
            - `options`: dict, the request options for the request

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryOffers(None, options)

    def QueryOffers(self, query, options=None):
        """Query for all offers.

        :Parameters:
            - `query`: str or dict.
            - `options`: dict, the request options for the request

        :Returns:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        def fetch_fn(options):
            return self.__QueryFeed('/offers',
                                    'offers',
                                    '',
                                    lambda r: r['Offers'],
                                    lambda _, b: b,
                                    query,
                                    options), self.last_response_headers
        return query_iterable.QueryIterable(self, query, options, fetch_fn)

    def GetDatabaseAccount(self, url_connection=None):
        """Gets database account info.

        :Returns:
            documents.DatabaseAccount

        """
        if url_connection is None:
            url_connection = self.url_connection

        initial_headers = dict(self.default_headers)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'get',
                                  '',  # path
                                  '',  # id
                                  '',  # type
                                  {});
        result, self.last_response_headers = self.__Get(url_connection,
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
        database_account.ConsistencyPolicy = result.get(constants._Constants.UserConsistencyPolicy)

        # WritableLocations and ReadableLocations fields will be available only for geo-replicated database accounts
        if constants._Constants.WritableLocations in result:
            database_account._WritableLocations = result[constants._Constants.WritableLocations]
        if constants._Constants.ReadableLocations in result:
            database_account._ReadableLocations = result[constants._Constants.ReadableLocations]
        return database_account

    def Create(self, body, path, type, id, initial_headers, options=None):
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
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  id,
                                  type,
                                  options)
        # Create will use WriteEndpoint since it uses POST operation
        url_connection = self._global_endpoint_manager.WriteEndpoint
        result, self.last_response_headers = self.__Post(url_connection,
                                                         path,
                                                         body,
                                                         headers)

        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Upsert(self, body, path, type, id, initial_headers, options=None):
        """Upserts a DocumentDB resource and returns it.

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
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  id,
                                  type,
                                  options)

        headers[http_constants.HttpHeaders.IsUpsert] = True

        # Upsert will use WriteEndpoint since it uses POST operation
        url_connection = self._global_endpoint_manager.WriteEndpoint
        result, self.last_response_headers = self.__Post(url_connection,
                                                         path,
                                                         body,
                                                         headers)
        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Replace(self, resource, path, type, id, initial_headers, options=None):
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
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'put',
                                  path,
                                  id,
                                  type,
                                  options)
        # Replace will use WriteEndpoint since it uses PUT operation
        url_connection = self._global_endpoint_manager.WriteEndpoint
        result, self.last_response_headers = self.__Put(url_connection,
                                                        path,
                                                        resource,
                                                        headers)
        
        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Read(self, path, type, id, initial_headers, options=None):
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
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'get',
                                  path,
                                  id,
                                  type,
                                  options)
        # Read will use ReadEndpoint since it uses GET operation
        url_connection = self._global_endpoint_manager.ReadEndpoint
        result, self.last_response_headers = self.__Get(url_connection,
                                                        path,
                                                        headers)
        return result

    def DeleteResource(self, path, type, id, initial_headers, options=None):
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
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'delete',
                                  path,
                                  id,
                                  type,
                                  options)
        # Delete will use WriteEndpoint since it uses DELETE operation
        url_connection = self._global_endpoint_manager.WriteEndpoint
        result, self.last_response_headers = self.__Delete(url_connection,
                                                           path,
                                                           headers)

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)


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
        return synchronized_request.SynchronizedRequest(self,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
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
        return synchronized_request.SynchronizedRequest(self,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
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
        return synchronized_request.SynchronizedRequest(self,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
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
        return synchronized_request.SynchronizedRequest(self,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
                                                        'DELETE',
                                                        url,
                                                        path,
                                                        request_data=None,
                                                        query_params=None,
                                                        headers=headers)

    def QueryFeed(self, path, collection_id, query, options, partition_key_range_id = None):
        """Query Feed for Document Collection resource.

        :Parameters:
            - `path`: str, path to the document collection
            - `collection_id`: str, id of the document collection
            - `query`: str or dict
            - `options`: dict, the request options for the request.
            - `partition_key_range_id`: str, partition key range id
        :Returns:
            tuple

        """
        return self.__QueryFeed(path,
                                'docs',
                                collection_id,
                                lambda r: r['Documents'],
                                lambda _, b: b,
                                query,
                                options,
                                partition_key_range_id), self.last_response_headers
    
    def __QueryFeed(self,
                    path,
                    type,
                    id,
                    result_fn,
                    create_fn,
                    query,
                    options=None,
                    partition_key_range_id=None):
        """Query for more than one DocumentDB resources.

        Raises :exc:`SystemError` is the query compatibility mode is undefined.

        :Parameters:
            - `path`: str
            - `type`: str
            - `id`: str
            - `result_fn`: function
            - `create_fn`: function
            - `query`: str or dict
            - `options`: dict, the request options for the request.
            - `partition_key_range_id`: str, specifies partition key range id

        :Returns:
            list

        """
        if options is None:
            options = {}

        if query:
            __GetBodiesFromQueryResult = result_fn
        else:
            def __GetBodiesFromQueryResult(result):
                return [create_fn(self, body) for body in result_fn(result)]

        # Query operations will use ReadEndpoint even though it uses GET(for feed requests) and POST(for regular query operations)
        url_connection = self._global_endpoint_manager.ReadEndpoint

        initial_headers = self.default_headers.copy()
        # Copy to make sure that default_headers won't be changed.
        if query is None:
            headers = base.GetHeaders(self,
                                      initial_headers,
                                      'get',
                                      path,
                                      id,
                                      type,
                                      options,
                                      partition_key_range_id)
            result, self.last_response_headers = self.__Get(url_connection,
                                                            path,
                                                            headers)
            return __GetBodiesFromQueryResult(result)
        else:
            query = self.__CheckAndUnifyQueryFormat(query)

            initial_headers[http_constants.HttpHeaders.IsQuery] = 'true'
            if (self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.Default or
                    self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.Query):
                initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.QueryJson
            elif self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.SqlQuery:
                initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.SQL
            else:
                raise SystemError('Unexpected query compatibility mode.')

            headers = base.GetHeaders(self,
                                      initial_headers,
                                      'post',
                                      path,
                                      id,
                                      type,
                                      options,
                                      partition_key_range_id)
            result, self.last_response_headers = self.__Post(url_connection,
                                                             path,
                                                             query,
                                                             headers)
            return __GetBodiesFromQueryResult(result)

    def __CheckAndUnifyQueryFormat(self, query_body):
        """Checks and unifies the format of the query body.

        Raises :exc:`TypeError` if query_body is not of expected type (depending on the query compatibility mode).
        Raises :exc:`ValueError` is query_body is a dict but doesn\'t have valid query text.
        Raises :exc:`SystemError` is the query compatibility mode is undefined.

        :Parameters:
            - `query_body`: str or dict

        :Returns:
            dict or string, the formatted query body.
        """
        if (self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.Default or
               self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.Query):
            if not isinstance(query_body, dict) and not isinstance(query_body, six.string_types):
                raise TypeError('query body must be a dict or string.')
            if isinstance(query_body, dict) and not query_body.get('query'):
                raise ValueError('query body must have valid query text with key "query".')
            if isinstance(query_body, six.string_types):
                return {'query': query_body}
        elif (self._query_compatibility_mode == DocumentClient._QueryCompatibilityMode.SqlQuery and
              not isinstance(query_body, six.string_types)):
            raise TypeError('query body must be a string.')
        else:
            raise SystemError('Unexpected query compatibility mode.')

        return query_body

    @staticmethod
    def __ValidateResource(resource):
        id = resource.get('id')
        if id:
            if id.find('/') != -1 or id.find('\\') != -1 or id.find('?') != -1 or id.find('#') != -1:
                raise ValueError('Id contains illegal chars.')

            if id[-1] == ' ':
                raise ValueError('Id ends with a space.')

    # Adds the partition key to options
    def _AddPartitionKey(self, collection_link, document, options):
        collection_link = base.TrimBeginningAndEndingSlashes(collection_link)
        
        #TODO: Refresh the cache if partition is extracted automatically and we get a 400.1001

        # If the document collection link is present in the cache, then use the cached partitionkey definition
        if collection_link in self.partition_key_definition_cache:
            partitionKeyDefinition = self.partition_key_definition_cache.get(collection_link)
        # Else read the collection from backend and add it to the cache
        else:
            collection = self.ReadCollection(collection_link)
            partitionKeyDefinition = collection.get('partitionKey')
            self.partition_key_definition_cache[collection_link] = partitionKeyDefinition
        
        # If the collection doesn't have a partition key definition, skip it as it's a legacy collection 
        if partitionKeyDefinition:
            # If the user has passed in the partitionKey in options use that elase extract it from the document
            if('partitionKey' not in options):
                partitionKeyValue = self._ExtractPartitionKey(partitionKeyDefinition, document)
                options['partitionKey'] = partitionKeyValue
        
        return options

    # Extracts the partition key from the document using the partitionKey definition
    def _ExtractPartitionKey(self, partitionKeyDefinition, document):

        # Parses the paths into a list of token each representing a property
        partition_key_parts = base.ParsePaths(partitionKeyDefinition.get('paths'))

        # Navigates the document to retrieve the partitionKey specified in the paths
        return self._RetrievePartitionKey(partition_key_parts, document)

    # Navigates the document to retrieve the partitionKey specified in the partition key parts
    def _RetrievePartitionKey(self, partition_key_parts, document):
        expected_matchCount = len(partition_key_parts)
        matchCount = 0
        partitionKey = document

        for part in partition_key_parts:
            # At any point if we don't find the value of a sub-property in the document, we return as Undefined
            if part not in partitionKey:
                return documents.Undefined
            else:
                partitionKey = partitionKey.get(part)
                matchCount += 1
                # Once we reach the "leaf" value(not a dict), we break from loop
                if not isinstance(partitionKey, dict):
                    break

        # Match the count of hops we did to get the partitionKey with the length of partition key parts and validate that it's not a dict at that level
        if ((matchCount != expected_matchCount) or isinstance(partitionKey, dict)):
            return documents.Undefined
         
        return partitionKey
    
    def _UpdateSessionIfRequired(self, request_headers, response_result, response_headers):    
        """
        Updates session if necessary.

        :Parameters:
            - `response_result`- response result
            - `response_headers` - response headers

        :Returns:
            None, but updates the client session if necessary

        """

        '''if this request was made with consistency level as session, then update
        the session'''

        if response_result is None or response_headers is None:
            return

        is_session_consistency = False
        if http_constants.HttpHeaders.ConsistencyLevel in request_headers:
            if documents.ConsistencyLevel.Session == request_headers[http_constants.HttpHeaders.ConsistencyLevel]:
                is_session_consistency = True
              
        if is_session_consistency:
            # update session
            self.session.update_session(response_result, response_headers)