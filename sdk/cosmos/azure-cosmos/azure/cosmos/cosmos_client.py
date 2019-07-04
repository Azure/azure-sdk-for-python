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

"""Document client class for the Azure Cosmos database service.
"""

import requests

import six
import azure.cosmos.base as base
import azure.cosmos.documents as documents
import azure.cosmos.constants as constants
import azure.cosmos.http_constants as http_constants
import azure.cosmos.query_iterable as query_iterable
import azure.cosmos.runtime_constants as runtime_constants
import azure.cosmos.request_object as request_object
import azure.cosmos.synchronized_request as synchronized_request
import azure.cosmos.global_endpoint_manager as global_endpoint_manager
import azure.cosmos.routing.routing_map_provider as routing_map_provider
import azure.cosmos.session as session
import azure.cosmos.utils as utils
import os

class CosmosClient(object):
    """Represents a document client.

    Provides a client-side logical representation of the Azure Cosmos
    service. This client is used to configure and execute requests against the
    service.

    The service client encapsulates the endpoint and credentials used to access
    the Azure Cosmos service.
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
        :param str url_connection:
            The URL for connecting to the DB server.
        :param dict auth:
            Contains 'masterKey' or 'resourceTokens', where
            auth['masterKey'] is the default authorization key to use to
            create the client, and auth['resourceTokens'] is the alternative
            authorization key.
        :param documents.ConnectionPolicy connection_policy:
            The connection policy for the client.
        :param documents.ConsistencyLevel consistency_level:
            The default consistency policy for client operations.

        if url_connection and auth are not provided,
            COSMOS_ENDPOINT and COSMOS_KEY environment variables will be used.
        """

        self.url_connection = url_connection or os.environ.get('COSMOS_ENDPOINT')

        self.master_key = None
        self.resource_tokens = None
        if auth is not None:
            self.master_key = auth.get('masterKey')
            self.resource_tokens = auth.get('resourceTokens')

            if auth.get('permissionFeed'):
                self.resource_tokens = {}
                for permission_feed in auth['permissionFeed']:
                    resource_parts = permission_feed['resource'].split('/')
                    id = resource_parts[-1]
                    self.resource_tokens[id] = permission_feed['_token']
        else:
            self.master_key = os.environ.get('COSMOS_KEY')

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

        self._useMultipleWriteLocations = False
        self._global_endpoint_manager = global_endpoint_manager._GlobalEndpointManager(self)

        # creating a requests session used for connection pooling and re-used by all requests
        self._requests_session = requests.Session()

        if self.connection_policy.ProxyConfiguration and self.connection_policy.ProxyConfiguration.Host:
            host = connection_policy.ProxyConfiguration.Host
            url = six.moves.urllib.parse.urlparse(host)
            proxy = host if url.port else host + ":" + str(connection_policy.ProxyConfiguration.Port)
            proxyDict = {url.scheme : proxy}
            self._requests_session.proxies.update(proxyDict)

        # Query compatibility mode.
        # Allows to specify compatibility mode used by client when making query requests. Should be removed when
        # application/sql is no longer supported.
        self._query_compatibility_mode = CosmosClient._QueryCompatibilityMode.Default

        # Routing map provider
        self._routing_map_provider = routing_map_provider._SmartRoutingMapProvider(self)

        database_account = self._global_endpoint_manager._GetDatabaseAccount()
        self._global_endpoint_manager.force_refresh(database_account)

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
        return self._global_endpoint_manager.get_write_endpoint()

    @property
    def ReadEndpoint(self):
        """Gets the curent read endpoint for a geo-replicated database account.
        """
        return self._global_endpoint_manager.get_read_endpoint()

    def RegisterPartitionResolver(self, database_link, partition_resolver):
        """Registers the partition resolver associated with the database link

        :param str database_link:
            Database Self Link or ID based link.
        :param object partition_resolver:
            An instance of PartitionResolver.
        
        """
        if not database_link:
            raise ValueError("database_link is None or empty.")

        if partition_resolver is None:
            raise ValueError("partition_resolver is None.")

        self.partition_resolvers = {base.TrimBeginningAndEndingSlashes(database_link): partition_resolver}


    def GetPartitionResolver(self, database_link):
        """Gets the partition resolver associated with the database link

        :param str database_link:
            Database self link or ID based link.

        :return:
            An instance of PartitionResolver.
        :rtype: object

        """
        if not database_link:
            raise ValueError("database_link is None or empty.")

        return self.partition_resolvers.get(base.TrimBeginningAndEndingSlashes(database_link))

        
    def CreateDatabase(self, database, options=None):
        """Creates a database.

        :param dict database:
            The Azure Cosmos database to create.
        :param dict options:
            The request options for the request.

        :return:
            The Database that was created.
        :rtype: dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(database)
        path = '/dbs'
        return self.Create(database, path, 'dbs', None, None, options)

    def ReadDatabase(self, database_link, options=None):
        """Reads a database.

        :param str database_link:
            The link to the database.
        :param dict options:
            The request options for the request.

        :return:
            The Database that was read.
        :rtype: dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link)
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return self.Read(path, 'dbs', database_id, None, options)

    def ReadDatabases(self, options=None):
        """Reads all databases.

        :param dict options:
            The request options for the request.

        :return: 
            Query Iterable of Databases.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryDatabases(None, options)

    def QueryDatabases(self, query, options=None):
        """Queries databases.

        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return: Query Iterable of Databases.
        :rtype:
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

    def ReadContainers(self, database_link, options=None):
        """Reads all collections in a database.

        :param str database_link:
            The link to the database.
        :param dict options:
            The request options for the request.
            
        :return: Query Iterable of Collections.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryContainers(database_link, None, options)

    def QueryContainers(self, database_link, query, options=None):
        """Queries collections in a database.

        :param str database_link:
            The link to the database.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return: Query Iterable of Collections.
        :rtype:
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

    def CreateContainer(self, database_link, collection, options=None):
        """Creates a collection in a database.

        :param str database_link:
            The link to the database.
        :param dict collection:
            The Azure Cosmos collection to create.
        :param dict options:
            The request options for the request.

        :return: The Collection that was created.
        :rtype: dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(collection)
        path = base.GetPathFromLink(database_link, 'colls')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return self.Create(collection,
                           path,
                           'colls',
                           database_id,
                           None,
                           options)

    def ReplaceContainer(self, collection_link, collection, options=None):
        """Replaces a collection and return it.

        :param str collection_link:
            The link to the collection entity.
        :param dict collection: 
            The collection to be used.
        :param dict options:
            The request options for the request.

        :return:
            The new Collection.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(collection)
        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return self.Replace(collection,
                            path,
                            'colls',
                            collection_id,
                            None,
                            options)

    def ReadContainer(self, collection_link, options=None):
        """Reads a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            The read Collection.
        :rtype:
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

        :param str database_link:
            The link to the database.
        :param dict user:
            The Azure Cosmos user to create.
        :param dict options:
            The request options for the request.

        :return:
            The created User.
        :rtype:
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

        :param str database_link:
            The link to the database.
        :param dict user:
            The Azure Cosmos user to upsert.
        :param dict options:
            The request options for the request.

        :return:
            The upserted User.
        :rtype: dict
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
        CosmosClient.__ValidateResource(user)
        path = base.GetPathFromLink(database_link, 'users')
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return database_id, path
    

    def ReadUser(self, user_link, options=None):
        """Reads a user.

        :param str user_link:
            The link to the user entity.
        :param dict options:
            The request options for the request.

        :return:
            The read User.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return self.Read(path, 'users', user_id, None, options)

    def ReadUsers(self, database_link, options=None):
        """Reads all users in a database.

        :params str database_link:
            The link to the database.
        :params dict options:
            The request options for the request.
        :return:
            Query iterable of Users.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryUsers(database_link, None, options)

    def QueryUsers(self, database_link, query, options=None):
        """Queries users in a database.

        :param str database_link:
            The link to the database.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Users.
        :rtype:   
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

        :param str database_link:
            The link to the database.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Database.
        :rtype:
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

        :param str user_link:
            The link to the user entity.
        :param dict permission:
            The Azure Cosmos user permission to create.
        :param dict options:
            The request options for the request.

        :return:
            The created Permission.
        :rtype:
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

        :param str user_link:
            The link to the user entity.
        :param dict permission:
            The Azure Cosmos user permission to upsert.
        :param dict options:
            The request options for the request.

        :return:
            The upserted permission.
        :rtype:
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
        CosmosClient.__ValidateResource(permission)
        path = base.GetPathFromLink(user_link, 'permissions')
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return path, user_id


    def ReadPermission(self, permission_link, options=None):
        """Reads a permission.

        :param str permission_link:
            The link to the permission.
        :param dict options:
            The request options for the request.

        :return:
            The read permission.
        :rtype:
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

        :param str user_link:
            The link to the user entity.
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Permissions.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryPermissions(user_link, None, options)

    def QueryPermissions(self, user_link, query, options=None):
        """Queries permissions for a user.

        :param str user_link:
            The link to the user entity.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Permissions.
        :rtype:
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

        :param str user_link:
            The link to the user entity.
        :param dict user:
        :param dict options:
            The request options for the request.

        :return:
            The new User.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(user)
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

        :param str user_link:
            The link to the user entity.
        :param dict options:
            The request options for the request.

        :return:
            The deleted user.
        :rtype:
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

        :param str permission_link:
            The link to the permission.
        :param dict permission:
        :param dict options:
            The request options for the request.

        :return:
            The new Permission.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(permission)
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

        :param str permission_link:
            The link to the permission.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Permission.
        :rtype:
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

    def ReadItems(self, collection_link, feed_options=None):
        """Reads all documents in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict feed_options:

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self.QueryItems(collection_link, None, feed_options)

    def QueryItems(self, database_or_Container_link, query, options=None, partition_key=None):
        """Queries documents in a collection.

        :param str database_or_Container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param str partition_key:
            Partition key for the query(default value None)

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        database_or_Container_link = base.TrimBeginningAndEndingSlashes(database_or_Container_link)

        if options is None:
            options = {}

        if(base.IsDatabaseLink(database_or_Container_link)):
            # Python doesn't have a good way of specifying an overloaded constructor, and this is how it's generally overloaded constructors are specified(by calling a @classmethod) and returning the 'self' instance
            return query_iterable.QueryIterable.PartitioningQueryIterable(self, query, options, database_or_Container_link, partition_key)
        else:    
            path = base.GetPathFromLink(database_or_Container_link, 'docs')
            collection_id = base.GetResourceIdOrFullNameFromLink(database_or_Container_link)
            def fetch_fn(options):
                return self.__QueryFeed(path,
                                        'docs',
                                        collection_id,
                                        lambda r: r['Documents'],
                                        lambda _, b: b,
                                        query,
                                        options), self.last_response_headers
            return query_iterable.QueryIterable(self, query, options, fetch_fn, database_or_Container_link)

    def QueryItemsChangeFeed(self, collection_link, options=None):
        """Queries documents change feed in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.
            options may also specify partition key range id.

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """

        partition_key_range_id = None
        if options is not None and 'partitionKeyRangeId' in options:
            partition_key_range_id = options['partitionKeyRangeId']

        return self._QueryChangeFeed(collection_link, "Documents" , options, partition_key_range_id)
        
    def _QueryChangeFeed(self, collection_link, resource_type, options=None, partition_key_range_id=None):
        """Queries change feed of a resource in a collection.

        :param str collection_link:
            The link to the document collection.
        :param str resource_type:
            The type of the resource.
        :param dict options:
            The request options for the request.
        :param str partition_key_range_id:
            Specifies partition key range id.

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}
        options['changeFeed'] = True

        resource_key_map = {'Documents' : 'docs'}

        # For now, change feed only supports Documents and Partition Key Range resouce type
        if resource_type not in resource_key_map:
            raise NotImplementedError(resource_type + " change feed query is not supported.")

        resource_key = resource_key_map[resource_type]
        path = base.GetPathFromLink(collection_link, resource_key)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        def fetch_fn(options):
            return self.__QueryFeed(path,
                                    resource_key,
                                    collection_id,
                                    lambda r: r[resource_type],
                                    lambda _, b: b,
                                    None,
                                    options,
                                    partition_key_range_id), self.last_response_headers
        return query_iterable.QueryIterable(self, None, options, fetch_fn, collection_link)

    def _ReadPartitionKeyRanges(self, collection_link, feed_options=None):
        """Reads Partition Key Ranges.

        :param str collection_link:
            The link to the document collection.
        :param dict feed_options:

        :return:
            Query Iterable of PartitionKeyRanges.
        :rtype:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self._QueryPartitionKeyRanges(collection_link, None, feed_options)

    def _QueryPartitionKeyRanges(self, collection_link, query, options=None):
        """Queries Partition Key Ranges in a collection.

        :param str collection_link:
            The link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of PartitionKeyRanges.
        :rtype:
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

    def CreateItem(self, database_or_Container_link, document, options=None):
        """Creates a document in a collection.

        :param str database_or_Container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param dict document:
            The Azure Cosmos document to create.
        :param dict options:
            The request options for the request.
        :param bool options['disableAutomaticIdGeneration']:
            Disables the automatic id generation. If id is missing in the body and this
            option is true, an error will be returned.

        :return:
            The created Document.
        :rtype:
            dict

        """
        # Python's default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the method
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}
        
        # We check the link to be document collection link since it can be database link in case of client side partitioning
        if(base.IsItemContainerLink(database_or_Container_link)):
            options = self._AddPartitionKey(database_or_Container_link, document, options)

        collection_id, document, path = self._GetContainerIdWithPathForItem(database_or_Container_link, document, options)
        return self.Create(document,
                           path,
                           'docs',
                           collection_id,
                           None,
                           options)

    def UpsertItem(self, database_or_Container_link, document, options=None):
        """Upserts a document in a collection.

        :param str database_or_Container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param dict document:
            The Azure Cosmos document to upsert.
        :param dict options:
            The request options for the request.
        :param bool options['disableAutomaticIdGeneration']:
            Disables the automatic id generation. If id is missing in the body and this
            option is true, an error will be returned.

        :return:
            The upserted Document.
        :rtype:
            dict

        """
        # Python's default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the method
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # We check the link to be document collection link since it can be database link in case of client side partitioning
        if(base.IsItemContainerLink(database_or_Container_link)):
            options = self._AddPartitionKey(database_or_Container_link, document, options)

        collection_id, document, path = self._GetContainerIdWithPathForItem(database_or_Container_link, document, options)
        return self.Upsert(document,
                           path,
                           'docs',
                           collection_id,
                           None,
                           options)

    PartitionResolverErrorMessage = "Couldn't find any partition resolvers for the database link provided. Ensure that the link you used when registering the partition resolvers matches the link provided or you need to register both types of database link(self link as well as ID based link)."

    # Gets the collection id and path for the document
    def _GetContainerIdWithPathForItem(self, database_or_Container_link, document, options):
        
        if not database_or_Container_link:
            raise ValueError("database_or_Container_link is None or empty.")

        if document is None:
            raise ValueError("document is None.")

        CosmosClient.__ValidateResource(document)
        document = document.copy()
        if (not document.get('id') and
            not options.get('disableAutomaticIdGeneration')):
            document['id'] = base.GenerateGuidId()
        
        collection_link = database_or_Container_link

        if(base.IsDatabaseLink(database_or_Container_link)):
            partition_resolver = self.GetPartitionResolver(database_or_Container_link)
        
            if(partition_resolver != None):
                collection_link = partition_resolver.ResolveForCreate(document)
            else:
                raise ValueError(CosmosClient.PartitionResolverErrorMessage)
        
        path = base.GetPathFromLink(collection_link, 'docs')
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, document, path
    
    def ReadItem(self, document_link, options=None):
        """Reads a document.

        :param str document_link:
            The link to the document.
        :param dict options:
            The request options for the request.

        :return:
            The read Document.
        :rtype:
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

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Triggers.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryTriggers(collection_link, None, options)

    def QueryTriggers(self, collection_link, query, options=None):
        """Queries triggers in a collection.

        :param str collection_link:
            The link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Triggers.
        :rtype:
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

        :param str collection_link:
            The link to the document collection.
        :param dict trigger:
        :param dict options:
            The request options for the request.

        :return:
            The created Trigger.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, trigger = self._GetContainerIdWithPathForTrigger(collection_link, trigger)
        return self.Create(trigger,
                           path,
                           'triggers',
                           collection_id,
                           None,
                           options)

    def UpsertTrigger(self, collection_link, trigger, options=None):
        """Upserts a trigger in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict trigger:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Trigger.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, trigger = self._GetContainerIdWithPathForTrigger(collection_link, trigger)
        return self.Upsert(trigger,
                           path,
                           'triggers',
                           collection_id,
                           None,
                           options)

    def _GetContainerIdWithPathForTrigger(self, collection_link, trigger):
        CosmosClient.__ValidateResource(trigger)
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

        :param str trigger_link:
            The link to the trigger.
        :param dict options:
            The request options for the request.

        :return:
            The read Trigger.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(trigger_link)
        trigger_id = base.GetResourceIdOrFullNameFromLink(trigger_link)
        return self.Read(path, 'triggers', trigger_id, None, options)

    def ReadUserDefinedFunctions(self, collection_link, options=None):
        """Reads all user defined functions in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of UDFs.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryUserDefinedFunctions(collection_link, None, options)

    def QueryUserDefinedFunctions(self, collection_link, query, options=None):
        """Queries user defined functions in a collection.

        :param str collection_link:
            The link to the collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of UDFs.
        :rtype:
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

        :param str collection_link:
            The link to the collection.
        :param str udf:
        :param dict options:
            The request options for the request.

        :return:
            The created UDF.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, udf = self._GetContainerIdWithPathForUDF(collection_link, udf)
        return self.Create(udf,
                           path,
                           'udfs',
                           collection_id,
                           None,
                           options)

    def UpsertUserDefinedFunction(self, collection_link, udf, options=None):
        """Upserts a user defined function in a collection.

        :param str collection_link:
            The link to the collection.
        :param str udf:
        :param dict options:
            The request options for the request.

        :return:
            The upserted UDF.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, udf = self._GetContainerIdWithPathForUDF(collection_link, udf)
        return self.Upsert(udf,
                           path,
                           'udfs',
                           collection_id,
                           None,
                           options)

    def _GetContainerIdWithPathForUDF(self, collection_link, udf):
        CosmosClient.__ValidateResource(udf)
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

        :param str udf_link:
            The link to the user defined function.
        :param dict options:
            The request options for the request.

        :return:
            The read UDF.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        return self.Read(path, 'udfs', udf_id, None, options)

    def ReadStoredProcedures(self, collection_link, options=None):
        """Reads all store procedures in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Stored Procedures.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryStoredProcedures(collection_link, None, options)

    def QueryStoredProcedures(self, collection_link, query, options=None):
        """Queries stored procedures in a collection.

        :param str collection_link:
            The link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Stored Procedures.
        :rtype:
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

        :param str collection_link:
            The link to the document collection.
        :param str sproc:
        :param dict options:
            The request options for the request.

        :return:
            The created Stored Procedure.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, sproc = self._GetContainerIdWithPathForSproc(collection_link, sproc)
        return self.Create(sproc,
                           path,
                           'sprocs',
                           collection_id,
                           None,
                           options)

    def UpsertStoredProcedure(self, collection_link, sproc, options=None):
        """Upserts a stored procedure in a collection.

        :param str collection_link:
            The link to the document collection.
        :param str sproc:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Stored Procedure.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        collection_id, path, sproc = self._GetContainerIdWithPathForSproc(collection_link, sproc)
        return self.Upsert(sproc,
                           path,
                           'sprocs',
                           collection_id,
                           None,
                           options)

    def _GetContainerIdWithPathForSproc(self, collection_link, sproc):
        CosmosClient.__ValidateResource(sproc)
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

        :param str sproc_link:
            The link to the stored procedure.
        :param dict options:
            The request options for the request.

        :return:
            The read Stored Procedure.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        return self.Read(path, 'sprocs', sproc_id, None, options)

    def ReadConflicts(self, collection_link, feed_options=None):
        """Reads conflicts.

        :param str collection_link:
            The link to the document collection.
        :param dict feed_options:

        :return:
            Query Iterable of Conflicts.
        :rtype:
            query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self.QueryConflicts(collection_link, None, feed_options)

    def QueryConflicts(self, collection_link, query, options=None):
        """Queries conflicts in a collection.

        :param str collection_link:
            The link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Conflicts.
        :rtype:
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

        :param str conflict_link:
            The link to the conflict.
        :param dict options:

        :return:
            The read Conflict.
        :rtype:
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

    def DeleteContainer(self, collection_link, options=None):
        """Deletes a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Collection.
        :rtype:
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

    def ReplaceItem(self, document_link, new_document, options=None):
        """Replaces a document and returns it.

        :param str document_link:
            The link to the document.
        :param dict new_document:
        :param dict options:
            The request options for the request.

        :return:
            The new Document.
        :rtype:
            dict

        """
        CosmosClient.__ValidateResource(new_document)
        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        
        # Python's default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). 
        # This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.
        # So, using a non-mutable deafult in this case(None) and assigning an empty dict(mutable) inside the function so that it remains local
        # For more details on this gotcha, please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # Extract the document collection link and add the partition key to options
        collection_link = base.GetItemContainerLink(document_link)
        options = self._AddPartitionKey(collection_link, new_document, options)
        
        return self.Replace(new_document,
                            path,
                            'docs',
                            document_id,
                            None,
                            options)

    def DeleteItem(self, document_link, options=None):
        """Deletes a document.

        :param str document_link:
            The link to the document.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Document.
        :rtype:
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

        :param str document_link:
            The link to the document.
        :param dict attachment:
            The Azure Cosmos attachment to create.
        :param dict options:
            The request options for the request.

        :return:
            The created Attachment.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        document_id, path = self._GetItemIdWithPathForAttachment(attachment, document_link)
        return self.Create(attachment,
                           path,
                           'attachments',
                           document_id,
                           None,
                           options)

    def UpsertAttachment(self, document_link, attachment, options=None):
        """Upserts an attachment in a document.

        :param str document_link:
            The link to the document.
        :param dict attachment:
            The Azure Cosmos attachment to upsert.
        :param dict options:
            The request options for the request.

        :return:
            The upserted Attachment.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        document_id, path = self._GetItemIdWithPathForAttachment(attachment, document_link)
        return self.Upsert(attachment,
                           path,
                           'attachments',
                           document_id,
                           None,
                           options)

    def _GetItemIdWithPathForAttachment(self, attachment, document_link):
        CosmosClient.__ValidateResource(attachment)
        path = base.GetPathFromLink(document_link, 'attachments')
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        return document_id, path

    def CreateAttachmentAndUploadMedia(self,
                                       document_link,
                                       readable_stream,
                                       options=None):
        """Creates an attachment and upload media.

        :param str document_link:
            The link to the document.
        :param (file-like stream object) readable_stream: 
        :param dict options:
            The request options for the request.

        :return:
            The created Attachment.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        document_id, initial_headers, path = self._GetItemIdWithPathForAttachmentMedia(document_link, options)
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

        :param str document_link:
            The link to the document.
        :param (file-like stream object) readable_stream:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Attachment.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        document_id, initial_headers, path = self._GetItemIdWithPathForAttachmentMedia(document_link, options)
        return self.Upsert(readable_stream,
                           path,
                           'attachments',
                           document_id,
                           initial_headers,
                           options)

    def _GetItemIdWithPathForAttachmentMedia(self, document_link, options):
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

        :param str attachment_link:
            The link to the attachment.
        :param dict options:
            The request options for the request.

        :return:
            The read Attachment.
        :rtype:
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

        :param str document_link:
            The link to the document.
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Attachments.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryAttachments(document_link, None, options)

    def QueryAttachments(self, document_link, query, options=None):
        """Queries attachments in a document.

        :param str document_link:
            The link to the document.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.

        :return:
            Query Iterable of Attachments.
        :rtype:
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

        :param str media_link:
            The link to the media.

        :return:
            The read Media.
        :rtype:
            str or file-like stream object

        """
        default_headers = self.default_headers

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

        # ReadMedia will always use WriteEndpoint since it's not replicated in readable Geo regions
        request = request_object._RequestObject('media', documents._OperationType.Read)
        result, self.last_response_headers = self.__Get(path,
                                                        request,
                                                        headers)
        return result

    def UpdateMedia(self, media_link, readable_stream, options=None):
        """Updates a media and returns it.

        :param str media_link:
            The link to the media.
        :param (file-like stream object) readable_stream:
        :param dict options:
            The request options for the request.

        :return:
            The updated Media.
        :rtype:
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

        # UpdateMedia will use WriteEndpoint since it uses PUT operation
        request = request_object._RequestObject('media', documents._OperationType.Update)
        result, self.last_response_headers = self.__Put(path,
                                                        request,
                                                        readable_stream,
                                                        headers)
        
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def ReplaceAttachment(self, attachment_link, attachment, options=None):
        """Replaces an attachment and returns it.

        :param str attachment_link:
            The link to the attachment.
        :param dict attachment:
        :param dict options:
            The request options for the request.

        :return:
            The replaced Attachment
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(attachment)
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

        :param str attachment_link:
            The link to the attachment.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Attachment.
        :rtype:
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

        :param str trigger_link:
            The link to the trigger.
        :param dict trigger:
        :param dict options:
            The request options for the request.

        :return:
            The replaced Trigger.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(trigger)
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

        :param str trigger_link:
            The link to the trigger.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Trigger.
        :rtype:
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

        :param str udf_link:
            The link to the user defined function.
        :param dict udf:
        :param dict options:
            The request options for the request.

        :return:
            The new UDF.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(udf)
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

        :param str udf_link:
            The link to the user defined function.
        :param dict options:
            The request options for the request.

        :return:
            The deleted UDF.
        :rtype:
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

        :param str sproc_link:
            The link to the stored procedure.
        :param dict params:
            List or None
        :param dict options:
            The request options for the request.

        :return:
            The Stored Procedure response.
        :rtype:
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

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        headers = base.GetHeaders(self,
                                  initial_headers,
                                  'post',
                                  path,
                                  sproc_id,
                                  'sprocs',
                                  options)

        # ExecuteStoredProcedure will use WriteEndpoint since it uses POST operation
        request = request_object._RequestObject('sprocs', documents._OperationType.ExecuteJavaScript)
        result, self.last_response_headers = self.__Post(path,
                                                         request,
                                                         params,
                                                         headers)
        return result

    def ReplaceStoredProcedure(self, sproc_link, sproc, options=None):
        """Replaces a stored procedure and returns it.

        :param str sproc_link:
            The link to the stored procedure.
        :param dict sproc:
        :param dict options:
            The request options for the request.

        :return:
            The replaced Stored Procedure.
        :rtype:
            dict

        """
        if options is None:
            options = {}

        CosmosClient.__ValidateResource(sproc)
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

        :param str sproc_link:
            The link to the stored procedure.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Stored Procedure.
        :rtype:
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

        :param str conflict_link:
            The link to the conflict.
        :param dict options:
            The request options for the request.

        :return:
            The deleted Conflict.
        :rtype:
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

        :param str offer_link:
            The link to the offer.
        :param dict offer:

        :return:
            The replaced Offer.
        :rtype:
            dict

        """
        CosmosClient.__ValidateResource(offer)
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return self.Replace(offer, path, 'offers', offer_id, None, None)

    def ReadOffer(self, offer_link):
        """Reads an offer.

        :param str offer_link:
            The link to the offer.

        :return:
            The read Offer.
        :rtype:
            dict

        """
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return self.Read(path, 'offers', offer_id, None, {})

    def ReadOffers(self, options=None):
        """Reads all offers.

        :param dict options:
            The request options for the request

        :return:
            Query Iterable of Offers.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryOffers(None, options)

    def QueryOffers(self, query, options=None):
        """Query for all offers.

        :param (str or dict) query:
        :param dict options:
            The request options for the request

        :return:
            Query Iterable of Offers.
        :rtype:
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

        :return:
            The Database Account.
        :rtype:
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
                                  {})

        request = request_object._RequestObject('databaseaccount', documents._OperationType.Read, url_connection)
        result, self.last_response_headers = self.__Get('',
                                                        request,
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
        if constants._Constants.EnableMultipleWritableLocations in result:
            database_account._EnableMultipleWritableLocations = result[constants._Constants.EnableMultipleWritableLocations]

        self._useMultipleWriteLocations = self.connection_policy.UseMultipleWriteLocations and database_account._EnableMultipleWritableLocations
        return database_account

    def Create(self, body, path, type, id, initial_headers, options=None):
        """Creates a Azure Cosmos resource and returns it.

        :param dict body:
        :param str path:
        :param str type:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The created Azure Cosmos resource.
        :rtype:
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

        request = request_object._RequestObject(type, documents._OperationType.Create)
        result, self.last_response_headers = self.__Post(path,
                                                         request,
                                                         body,
                                                         headers)

        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Upsert(self, body, path, type, id, initial_headers, options=None):
        """Upserts a Azure Cosmos resource and returns it.
        
        :param dict body:
        :param str path:
        :param str type:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Azure Cosmos resource.
        :rtype:
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
        request = request_object._RequestObject(type, documents._OperationType.Upsert)
        result, self.last_response_headers = self.__Post(path,
                                                         request,
                                                         body,
                                                         headers)
        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Replace(self, resource, path, type, id, initial_headers, options=None):
        """Replaces a Azure Cosmos resource and returns it.

        :param dict resource:
        :param str path:
        :param str type:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The new Azure Cosmos resource.
        :rtype:
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
        request = request_object._RequestObject(type, documents._OperationType.Replace)
        result, self.last_response_headers = self.__Put(path,
                                                        request,
                                                        resource,
                                                        headers)
        
        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    def Read(self, path, type, id, initial_headers, options=None):
        """Reads a Azure Cosmos resource and returns it.

        :param str path:
        :param str type:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The upserted Azure Cosmos resource.
        :rtype:
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
        request = request_object._RequestObject(type, documents._OperationType.Read)
        result, self.last_response_headers = self.__Get(path,
                                                        request,
                                                        headers)
        return result

    def DeleteResource(self, path, type, id, initial_headers, options=None):
        """Deletes a Azure Cosmos resource and returns it.

        :param str path:
        :param str type:
        :param str id:
        :param dict initial_headers:
        :param dict options:
            The request options for the request.

        :return:
            The deleted Azure Cosmos resource.
        :rtype:
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
        request = request_object._RequestObject(type, documents._OperationType.Delete)
        result, self.last_response_headers = self.__Delete(path,
                                                           request,
                                                           headers)

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)


        return result

    def __Get(self, path, request, headers):
        """Azure Cosmos 'GET' http request.

        :params str url:
        :params str path:
        :params dict headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        return synchronized_request.SynchronizedRequest(self,
                                                        request,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
                                                        'GET',
                                                        path,
                                                        None,
                                                        None,
                                                        headers)

    def __Post(self, path, request, body, headers):
        """Azure Cosmos 'POST' http request.

        :params str url:
        :params str path:
        :params (str, unicode, dict) body:
        :params dict headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        return synchronized_request.SynchronizedRequest(self,
                                                        request,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
                                                        'POST',
                                                        path,
                                                        body,
                                                        query_params=None,
                                                        headers=headers)

    def __Put(self, path, request, body, headers):
        """Azure Cosmos 'PUT' http request.

        :params str url:
        :params str path:
        :params (str, unicode, dict) body:
        :params dict headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        return synchronized_request.SynchronizedRequest(self,
                                                        request,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
                                                        'PUT',
                                                        path,
                                                        body,
                                                        query_params=None,
                                                        headers=headers)

    def __Delete(self, path, request, headers):
        """Azure Cosmos 'DELETE' http request.

        :params str url:
        :params str path:
        :params dict headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        return synchronized_request.SynchronizedRequest(self,
                                                        request,
                                                        self._global_endpoint_manager,
                                                        self.connection_policy,
                                                        self._requests_session,
                                                        'DELETE',
                                                        path,
                                                        request_data=None,
                                                        query_params=None,
                                                        headers=headers)

    def QueryFeed(self, path, collection_id, query, options, partition_key_range_id = None):
        """Query Feed for Document Collection resource.

        :param str path:
            Path to the document collection.
        :param str collection_id:
            Id of the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param str partition_key_range_id:
            Partition key range id.
        :rtype:
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
        """Query for more than one Azure Cosmos resources.

        :param str path:
        :param str type:
        :param str id:
        :param function result_fn:
        :param function create_fn:
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param str partition_key_range_id:
            Specifies partition key range id.

        :rtype:
            list
        
        :raises SystemError: If the query compatibility mode is undefined.

        """
        if options is None:
            options = {}

        if query:
            __GetBodiesFromQueryResult = result_fn
        else:
            def __GetBodiesFromQueryResult(result):
                if result is not None:
                    return [create_fn(self, body) for body in result_fn(result)]
                else:
                    # If there is no change feed, the result data is empty and result is None.
                    # This case should be interpreted as an empty array.
                    return []


        initial_headers = self.default_headers.copy()
        # Copy to make sure that default_headers won't be changed.
        if query is None:
            # Query operations will use ReadEndpoint even though it uses GET(for feed requests)
            request = request_object._RequestObject(type, documents._OperationType.ReadFeed)
            headers = base.GetHeaders(self,
                                      initial_headers,
                                      'get',
                                      path,
                                      id,
                                      type,
                                      options,
                                      partition_key_range_id)
            result, self.last_response_headers = self.__Get(path,
                                                            request,
                                                            headers)
            return __GetBodiesFromQueryResult(result)
        else:
            query = self.__CheckAndUnifyQueryFormat(query)

            initial_headers[http_constants.HttpHeaders.IsQuery] = 'true'
            if (self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.Default or
                    self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.Query):
                initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.QueryJson
            elif self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.SqlQuery:
                initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.SQL
            else:
                raise SystemError('Unexpected query compatibility mode.')

            # Query operations will use ReadEndpoint even though it uses POST(for regular query operations)
            request = request_object._RequestObject(type, documents._OperationType.SqlQuery)
            headers = base.GetHeaders(self,
                                      initial_headers,
                                      'post',
                                      path,
                                      id,
                                      type,
                                      options,
                                      partition_key_range_id)
            result, self.last_response_headers = self.__Post(path,
                                                             request,
                                                             query,
                                                             headers)
            return __GetBodiesFromQueryResult(result)

    def __CheckAndUnifyQueryFormat(self, query_body):
        """Checks and unifies the format of the query body.

        :raises TypeError: If query_body is not of expected type (depending on the query compatibility mode).
        :raises ValueError: If query_body is a dict but doesn\'t have valid query text.
        :raises SystemError: If the query compatibility mode is undefined.

        :param (str or dict) query_body:

        :return:
            The formatted query body.
        :rtype:
            dict or string
        """
        if (self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.Default or
               self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.Query):
            if not isinstance(query_body, dict) and not isinstance(query_body, six.string_types):
                raise TypeError('query body must be a dict or string.')
            if isinstance(query_body, dict) and not query_body.get('query'):
                raise ValueError('query body must have valid query text with key "query".')
            if isinstance(query_body, six.string_types):
                return {'query': query_body}
        elif (self._query_compatibility_mode == CosmosClient._QueryCompatibilityMode.SqlQuery and
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
            collection = self.ReadContainer(collection_link)
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

        :param dict response_result:
        :param dict response_headers:
        :param dict response_headers

        :return:
            None, but updates the client session if necessary.

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
