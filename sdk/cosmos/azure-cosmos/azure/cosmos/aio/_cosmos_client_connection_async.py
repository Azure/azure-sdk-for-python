# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# disable (too-many-lines) check
# pylint: disable=C0302

"""Document client class for the Azure Cosmos database service.
"""
# https://github.com/PyCQA/pylint/issues/3112
# Currently pylint is locked to 2.3.3 and this is fixed in 2.4.4
from typing import Dict, Any, Optional # pylint: disable=unused-import
import six
from urllib3.util.retry import Retry
from azure.core.async_paging import AsyncItemPaged
from azure.core import AsyncPipelineClient
from azure.core.exceptions import raise_with_traceback  # type: ignore
from azure.core.pipeline.policies import (
    AsyncHTTPPolicy,
    ContentDecodePolicy,
    HeadersPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    ProxyPolicy)

from .. import _base as base
from .. import documents
from ..documents import ConnectionPolicy
from .. import _constants as constants
from .. import http_constants
from . import _query_iterable_async as query_iterable
from .. import _runtime_constants as runtime_constants
from .. import _request_object
from . import _asynchronous_request as asynchronous_request
from . import _global_endpoint_manager_async as global_endpoint_manager_async
from .._routing import routing_map_provider
from ._retry_utility_async import ConnectionRetryPolicy
from .. import _session
from .. import _utils
from ..partition_key import _Undefined, _Empty

# pylint: disable=protected-access

class CosmosClientConnection(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
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

    def __init__(
        self,
        url_connection,  # type: str
        auth,  # type: Dict[str, Any]
        connection_policy=None,  # type: Optional[ConnectionPolicy]
        consistency_level=documents.ConsistencyLevel.Session,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
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

        """
        self.url_connection = url_connection

        self.master_key = None
        self.resource_tokens = None
        if auth is not None:
            self.master_key = auth.get("masterKey")
            self.resource_tokens = auth.get("resourceTokens")

            if auth.get("permissionFeed"):
                self.resource_tokens = {}
                for permission_feed in auth["permissionFeed"]:
                    resource_parts = permission_feed["resource"].split("/")
                    id_ = resource_parts[-1]
                    self.resource_tokens[id_] = permission_feed["_token"]

        self.connection_policy = connection_policy or ConnectionPolicy()

        self.partition_resolvers = {}  # type: Dict[str, Any]

        self.partition_key_definition_cache = {}  # type: Dict[str, Any]

        self.default_headers = {
            http_constants.HttpHeaders.CacheControl: "no-cache",
            http_constants.HttpHeaders.Version: http_constants.Versions.CurrentVersion,
            # For single partition query with aggregate functions we would try to accumulate the results on the SDK.
            # We need to set continuation as not expected.
            http_constants.HttpHeaders.IsContinuationExpected: False,
        }

        if consistency_level is not None:
            self.default_headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level

        # Keeps the latest response headers from server.
        self.last_response_headers = None

        if consistency_level == documents.ConsistencyLevel.Session:
            # create a session - this is maintained only if the default consistency level
            # on the client is set to session, or if the user explicitly sets it as a property
            # via setter
            self.session = _session.Session(self.url_connection)
        else:
            self.session = None  # type: ignore

        self._useMultipleWriteLocations = False
        self._global_endpoint_manager = global_endpoint_manager_async._GlobalEndpointManager(self)

        retry_policy = None
        if isinstance(self.connection_policy.ConnectionRetryConfiguration, AsyncHTTPPolicy):
            retry_policy = self.connection_policy.ConnectionRetryConfiguration
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, int):
            retry_policy = ConnectionRetryPolicy(total=self.connection_policy.ConnectionRetryConfiguration)
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, Retry):
            # Convert a urllib3 retry policy to a Pipeline policy
            retry_policy = ConnectionRetryPolicy(
                retry_total=self.connection_policy.ConnectionRetryConfiguration.total,
                retry_connect=self.connection_policy.ConnectionRetryConfiguration.connect,
                retry_read=self.connection_policy.ConnectionRetryConfiguration.read,
                retry_status=self.connection_policy.ConnectionRetryConfiguration.status,
                retry_backoff_max=self.connection_policy.ConnectionRetryConfiguration.BACKOFF_MAX,
                retry_on_status_codes=list(self.connection_policy.ConnectionRetryConfiguration.status_forcelist),
                retry_backoff_factor=self.connection_policy.ConnectionRetryConfiguration.backoff_factor
            )
        else:
            TypeError("Unsupported retry policy. Must be an azure.cosmos.ConnectionRetryPolicy, int, or urllib3.Retry")

        proxies = kwargs.pop('proxies', {})
        if self.connection_policy.ProxyConfiguration and self.connection_policy.ProxyConfiguration.Host:
            host = self.connection_policy.ProxyConfiguration.Host
            url = six.moves.urllib.parse.urlparse(host)
            proxy = host if url.port else host + ":" + str(self.connection_policy.ProxyConfiguration.Port)
            proxies.update({url.scheme : proxy})

        policies = [
            HeadersPolicy(**kwargs),
            ProxyPolicy(proxies=proxies),
            UserAgentPolicy(base_user_agent=_utils.get_user_agent(), **kwargs),
            ContentDecodePolicy(),
            retry_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
            ]

        transport = kwargs.pop("transport", None)
        self.pipeline_client = AsyncPipelineClient(base_url=url_connection, transport=transport, policies=policies)
        self._setup_kwargs = kwargs

        # Query compatibility mode.
        # Allows to specify compatibility mode used by client when making query requests. Should be removed when
        # application/sql is no longer supported.
        self._query_compatibility_mode = CosmosClientConnection._QueryCompatibilityMode.Default

        # Routing map provider
        self._routing_map_provider = routing_map_provider.SmartRoutingMapProvider(self)

    async def _setup(self):
        if not 'database_account' in self._setup_kwargs:
            self._setup_kwargs['database_account'] = await self._global_endpoint_manager._GetDatabaseAccount(**self._setup_kwargs)
            await self._global_endpoint_manager.force_refresh(self._setup_kwargs['database_account'])

    def _GetDatabaseIdWithPathForUser(self, database_link, user):  # pylint: disable=no-self-use
        CosmosClientConnection.__ValidateResource(user)
        path = base.GetPathFromLink(database_link, "users")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return database_id, path

    async def GetDatabaseAccount(self, url_connection=None, **kwargs):
        """Gets database account info.

        :return:
            The Database Account.
        :rtype:
            documents.DatabaseAccount

        """
        if url_connection is None:
            url_connection = self.url_connection

        initial_headers = dict(self.default_headers)
        headers = base.GetHeaders(self, initial_headers, "get", "", "", "", {})  # path  # id  # type

        request_params = _request_object.RequestObject("databaseaccount", documents._OperationType.Read, url_connection)
        result, self.last_response_headers = await self.__Get("", request_params, headers, **kwargs)
        database_account = documents.DatabaseAccount()
        database_account.DatabasesLink = "/dbs/"
        database_account.MediaLink = "/media/"
        if http_constants.HttpHeaders.MaxMediaStorageUsageInMB in self.last_response_headers:
            database_account.MaxMediaStorageUsageInMB = self.last_response_headers[
                http_constants.HttpHeaders.MaxMediaStorageUsageInMB
            ]
        if http_constants.HttpHeaders.CurrentMediaStorageUsageInMB in self.last_response_headers:
            database_account.CurrentMediaStorageUsageInMB = self.last_response_headers[
                http_constants.HttpHeaders.CurrentMediaStorageUsageInMB
            ]
        database_account.ConsistencyPolicy = result.get(constants._Constants.UserConsistencyPolicy)

        # WritableLocations and ReadableLocations fields will be available only for geo-replicated database accounts
        if constants._Constants.WritableLocations in result:
            database_account._WritableLocations = result[constants._Constants.WritableLocations]
        if constants._Constants.ReadableLocations in result:
            database_account._ReadableLocations = result[constants._Constants.ReadableLocations]
        if constants._Constants.EnableMultipleWritableLocations in result:
            database_account._EnableMultipleWritableLocations = result[
                constants._Constants.EnableMultipleWritableLocations
            ]

        self._useMultipleWriteLocations = (
            self.connection_policy.UseMultipleWriteLocations and database_account._EnableMultipleWritableLocations
        )
        return database_account

    async def CreateDatabase(self, database, options=None, **kwargs):
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

        CosmosClientConnection.__ValidateResource(database)
        path = "/dbs"
        return await self.Create(database, path, "dbs", None, None, options, **kwargs)

    async def CreateUser(self, database_link, user, options=None, **kwargs):
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
        return await self.Create(user, path, "users", database_id, None, options, **kwargs)

    async def CreateContainer(self, database_link, collection, options=None, **kwargs):
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

        CosmosClientConnection.__ValidateResource(collection)
        path = base.GetPathFromLink(database_link, "colls")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return await self.Create(collection, path, "colls", database_id, None, options, **kwargs)

    async def CreateItem(self, database_or_container_link, document, options=None, **kwargs):
        """Creates a document in a collection.

        :param str database_or_container_link:
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
        # Python's default arguments are evaluated once when the function is defined,
        # not each time the function is called (like it is in say, Ruby). This means
        # that if you use a mutable default argument and mutate it, you will and have
        # mutated that object for all future calls to the function as well. So, using
        # a non-mutable default in this case(None) and assigning an empty dict(mutable)
        # inside the method For more details on this gotcha, please refer
        # http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # We check the link to be document collection link since it can be database
        # link in case of client side partitioning
        collection_id, document, path = self._GetContainerIdWithPathForItem(
            database_or_container_link, document, options
        )

        if base.IsItemContainerLink(database_or_container_link):
            options = await self._AddPartitionKey(database_or_container_link, document, options)

        return await self.Create(document, path, "docs", collection_id, None, options, **kwargs)

    async def Create(self, body, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Creates a Azure Cosmos resource and returns it.

        :param dict body:
        :param str path:
        :param str typ:
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
        headers = base.GetHeaders(self, initial_headers, "post", path, id, typ, options)
        # Create will use WriteEndpoint since it uses POST operation

        request_params = _request_object.RequestObject(typ, documents._OperationType.Create)
        result, self.last_response_headers = await self.__Post(path, request_params, body, headers, **kwargs)

        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    async def UpsertUser(self, database_link, user, options=None, **kwargs):
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
        return await self.Upsert(user, path, "users", database_id, None, options, **kwargs)

    async def UpsertItem(self, database_or_container_link, document, options=None, **kwargs):
        """Upserts a document in a collection.

        :param str database_or_container_link:
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
        # Python's default arguments are evaluated once when the function is defined,
        # not each time the function is called (like it is in say, Ruby). This means
        # that if you use a mutable default argument and mutate it, you will and have
        # mutated that object for all future calls to the function as well. So, using
        # a non-mutable deafult in this case(None) and assigning an empty dict(mutable)
        # inside the method For more details on this gotcha, please refer
        # http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # We check the link to be document collection link since it can be database
        # link in case of client side partitioning
        if base.IsItemContainerLink(database_or_container_link):
            options = await self._AddPartitionKey(database_or_container_link, document, options)

        collection_id, document, path = self._GetContainerIdWithPathForItem(
            database_or_container_link, document, options
        )
        return await self.Upsert(document, path, "docs", collection_id, None, options, **kwargs)

    async def Upsert(self, body, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Upserts a Azure Cosmos resource and returns it.

        :param dict body:
        :param str path:
        :param str typ:
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
        headers = base.GetHeaders(self, initial_headers, "post", path, id, typ, options)

        headers[http_constants.HttpHeaders.IsUpsert] = True

        # Upsert will use WriteEndpoint since it uses POST operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Upsert)
        result, self.last_response_headers = await self.__Post(path, request_params, body, headers, **kwargs)
        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    async def __Post(self, path, request_params, body, req_headers, **kwargs):
        """Azure Cosmos 'POST' async http request.

        :params str url:
        :params str path:
        :params (str, unicode, dict) body:
        :params dict req_headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        request = self.pipeline_client.post(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=body,
            **kwargs
        )

    async def ReadDatabase(self, database_link, options=None, **kwargs):
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
        return await self.Read(path, "dbs", database_id, None, options, **kwargs)

    async def ReadContainer(self, collection_link, options=None, **kwargs):
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
        return await self.Read(path, "colls", collection_id, None, options, **kwargs)

    async def ReadItem(self, document_link, options=None, **kwargs):
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
        return await self.Read(path, "docs", document_id, None, options, **kwargs)

    async def ReadConflict(self, conflict_link, options=None, **kwargs):
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
        return await self.Read(path, "conflicts", conflict_id, None, options, **kwargs)

    async def Read(self, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Reads a Azure Cosmos resource and returns it.

        :param str path:
        :param str typ:
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
        headers = base.GetHeaders(self, initial_headers, "get", path, id, typ, options)
        # Read will use ReadEndpoint since it uses GET operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Read)
        result, self.last_response_headers = await self.__Get(path, request_params, headers, **kwargs)
        return result

    async def __Get(self, path, request_params, req_headers, **kwargs):
        """Azure Cosmos 'GET' async async http request.

        :params str url:
        :params str path:
        :params dict req_headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        request = self.pipeline_client.get(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=None,
            **kwargs
        )

    async def ReplaceUser(self, user_link, user, options=None, **kwargs):
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

        CosmosClientConnection.__ValidateResource(user)
        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return await self.Replace(user, path, "users", user_id, None, options, **kwargs)

    async def ReplaceContainer(self, collection_link, collection, options=None, **kwargs):
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

        CosmosClientConnection.__ValidateResource(collection)
        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return await self.Replace(collection, path, "colls", collection_id, None, options, **kwargs)

    async def ReplaceItem(self, document_link, new_document, options=None, **kwargs):
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
        CosmosClientConnection.__ValidateResource(new_document)
        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)

        # Python's default arguments are evaluated once when the function is defined,
        # not each time the function is called (like it is in say, Ruby). This means
        # that if you use a mutable default argument and mutate it, you will and have
        # mutated that object for all future calls to the function as well. So, using
        # a non-mutable deafult in this case(None) and assigning an empty dict(mutable)
        # inside the function so that it remains local For more details on this gotcha,
        # please refer http://docs.python-guide.org/en/latest/writing/gotchas/
        if options is None:
            options = {}

        # Extract the document collection link and add the partition key to options
        collection_link = base.GetItemContainerLink(document_link)
        options = await self._AddPartitionKey(collection_link, new_document, options)

        return await self.Replace(new_document, path, "docs", document_id, None, options, **kwargs)

    async def ReplaceOffer(self, offer_link, offer, **kwargs):
        """Replaces an offer and returns it.

        :param str offer_link:
            The link to the offer.
        :param dict offer:

        :return:
            The replaced Offer.
        :rtype:
            dict

        """
        CosmosClientConnection.__ValidateResource(offer)
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return await self.Replace(offer, path, "offers", offer_id, None, None, **kwargs)

    async def Replace(self, resource, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Replaces a Azure Cosmos resource and returns it.

        :param dict resource:
        :param str path:
        :param str typ:
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
        headers = base.GetHeaders(self, initial_headers, "put", path, id, typ, options)
        # Replace will use WriteEndpoint since it uses PUT operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Replace)
        result, self.last_response_headers = await self.__Put(path, request_params, resource, headers, **kwargs)

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        return result

    async def __Put(self, path, request_params, body, req_headers, **kwargs):
        """Azure Cosmos 'PUT' async http request.

        :params str url:
        :params str path:
        :params (str, unicode, dict) body:
        :params dict req_headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        request = self.pipeline_client.put(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=body,
            **kwargs
        )

    async def DeleteDatabase(self, database_link, options=None, **kwargs):
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
        return await self.DeleteResource(path, "dbs", database_id, None, options, **kwargs)

    async def DeleteUser(self, user_link, options=None, **kwargs):
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
        return await self.DeleteResource(path, "users", user_id, None, options, **kwargs)

    async def DeleteContainer(self, collection_link, options=None, **kwargs):
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
        return await self.DeleteResource(path, "colls", collection_id, None, options, **kwargs)


    async def DeleteItem(self, document_link, options=None, **kwargs):
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
        return await self.DeleteResource(path, "docs", document_id, None, options, **kwargs)

    async def DeleteConflict(self, conflict_link, options=None, **kwargs):
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
        return await self.DeleteResource(path, "conflicts", conflict_id, None, options, **kwargs)

    async def DeleteResource(self, path, typ, id, initial_headers, options=None, **kwargs):  # pylint: disable=redefined-builtin
        """Deletes a Azure Cosmos resource and returns it.

        :param str path:
        :param str typ:
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
        headers = base.GetHeaders(self, initial_headers, "delete", path, id, typ, options)
        # Delete will use WriteEndpoint since it uses DELETE operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Delete)
        result, self.last_response_headers = await self.__Delete(path, request_params, headers, **kwargs)

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)

        return result

    async def __Delete(self, path, request_params, req_headers, **kwargs):
        """Azure Cosmos 'DELETE' async http request.

        :params str url:
        :params str path:
        :params dict req_headers:

        :return:
            Tuple of (result, headers).
        :rtype:
            tuple of (dict, dict)

        """
        request = self.pipeline_client.delete(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=None,
            **kwargs
        )

    def ReadItems(self, collection_link, feed_options=None, response_hook=None, **kwargs):
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

        return self.QueryItems(collection_link, None, feed_options, response_hook=response_hook, **kwargs)

    def QueryItems(
        self,
        database_or_container_link,
        query,
        options=None,
        partition_key=None,
        response_hook=None,
        **kwargs
    ):
        """Queries documents in a collection.

        :param str database_or_container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param str partition_key:
            Partition key for the query(default value None)
        :param response_hook:
            A callable invoked with the response metadata

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        database_or_container_link = base.TrimBeginningAndEndingSlashes(database_or_container_link)

        if options is None:
            options = {}

        if base.IsDatabaseLink(database_or_container_link):
            return AsyncItemPaged(
                self,
                query,
                options,
                database_link=database_or_container_link,
                partition_key=partition_key,
                page_iterator_class=query_iterable.QueryIterable
            )

        path = base.GetPathFromLink(database_or_container_link, "docs")
        collection_id = base.GetResourceIdOrFullNameFromLink(database_or_container_link)

        async def fetch_fn(options):
            return (
                await self.__QueryFeed(
                    path,
                    "docs",
                    collection_id,
                    lambda r: r["Documents"],
                    lambda _, b: b,
                    query,
                    options,
                    response_hook=response_hook,
                    **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self,
            query,
            options,
            fetch_function=fetch_fn,
            collection_link=database_or_container_link,
            page_iterator_class=query_iterable.QueryIterable
        )

    def QueryItemsChangeFeed(self, collection_link, options=None, response_hook=None, **kwargs):
        """Queries documents change feed in a collection.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.
            options may also specify partition key range id.
        :param response_hook:
            A callable invoked with the response metadata

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """

        partition_key_range_id = None
        if options is not None and "partitionKeyRangeId" in options:
            partition_key_range_id = options["partitionKeyRangeId"]

        return self._QueryChangeFeed(
            collection_link, "Documents", options, partition_key_range_id, response_hook=response_hook, **kwargs
        )

    def _QueryChangeFeed(
        self, collection_link, resource_type, options=None, partition_key_range_id=None, response_hook=None, **kwargs
    ):
        """Queries change feed of a resource in a collection.

        :param str collection_link:
            The link to the document collection.
        :param str resource_type:
            The type of the resource.
        :param dict options:
            The request options for the request.
        :param str partition_key_range_id:
            Specifies partition key range id.
        :param response_hook:
            A callable invoked with the response metadata

        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}
        options["changeFeed"] = True

        resource_key_map = {"Documents": "docs"}

        # For now, change feed only supports Documents and Partition Key Range resouce type
        if resource_type not in resource_key_map:
            raise NotImplementedError(resource_type + " change feed query is not supported.")

        resource_key = resource_key_map[resource_type]
        path = base.GetPathFromLink(collection_link, resource_key)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options):
            return (
                await self.__QueryFeed(
                    path,
                    resource_key,
                    collection_id,
                    lambda r: r[resource_type],
                    lambda _, b: b,
                    None,
                    options,
                    partition_key_range_id,
                    response_hook=response_hook,
                    **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self,
            None,
            options,
            fetch_function=fetch_fn,
            collection_link=collection_link,
            page_iterator_class=query_iterable.QueryIterable
        )

    def QueryOffers(self, query, options=None, **kwargs):
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

        async def fetch_fn(options):
            return (
                await self.__QueryFeed(
                    "/offers", "offers", "", lambda r: r["Offers"], lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, 
            query, 
            options, 
            fetch_function=fetch_fn, 
            page_iterator_class=query_iterable.QueryIterable
        )

    def ReadConflicts(self, collection_link, feed_options=None, **kwargs):
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

        return self.QueryConflicts(collection_link, None, feed_options, **kwargs)

    def QueryConflicts(self, collection_link, query, options=None, **kwargs):
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

        path = base.GetPathFromLink(collection_link, "conflicts")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options):
            return (
                await self.__QueryFeed(
                    path, "conflicts", collection_id, lambda r: r["Conflicts"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    async def __QueryFeed(
        self,
        path,
        typ,
        id_,
        result_fn,
        create_fn,
        query,
        options=None,
        partition_key_range_id=None,
        response_hook=None,
        is_query_plan=False,
        **kwargs
    ):
        """Query for more than one Azure Cosmos resources.

        :param str path:
        :param str typ:
        :param str id_:
        :param function result_fn:
        :param function create_fn:
        :param (str or dict) query:
        :param dict options:
            The request options for the request.
        :param str partition_key_range_id:
            Specifies partition key range id.
        :param function response_hook:
        :param bool is_query_plan:
            Specififes if the call is to fetch query plan

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
                # If there is no change feed, the result data is empty and result is None.
                # This case should be interpreted as an empty array.
                return []

        initial_headers = self.default_headers.copy()
        # Copy to make sure that default_headers won't be changed.
        if query is None:
            # Query operations will use ReadEndpoint even though it uses GET(for feed requests)
            request_params = _request_object.RequestObject(typ,
                        documents._OperationType.QueryPlan if is_query_plan else documents._OperationType.ReadFeed)
            headers = base.GetHeaders(self, initial_headers, "get", path, id_, typ, options, partition_key_range_id)
            result, self.last_response_headers = await self.__Get(path, request_params, headers, **kwargs)
            if response_hook:
                response_hook(self.last_response_headers, result)
            return __GetBodiesFromQueryResult(result)

        query = self.__CheckAndUnifyQueryFormat(query)

        initial_headers[http_constants.HttpHeaders.IsQuery] = "true"
        if not is_query_plan:
            initial_headers[http_constants.HttpHeaders.IsQuery] = "true"

        if (
            self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.Default
            or self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.Query
        ):
            initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.QueryJson
        elif self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.SqlQuery:
            initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.SQL
        else:
            raise SystemError("Unexpected query compatibility mode.")

        # Query operations will use ReadEndpoint even though it uses POST(for regular query operations)
        request_params = _request_object.RequestObject(typ, documents._OperationType.SqlQuery)
        req_headers = base.GetHeaders(self, initial_headers, "post", path, id_, typ, options, partition_key_range_id)
        result, self.last_response_headers = await self.__Post(path, request_params, query, req_headers, **kwargs)

        if response_hook:
            response_hook(self.last_response_headers, result)

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
        if (
            self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.Default
            or self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.Query
        ):
            if not isinstance(query_body, dict) and not isinstance(query_body, six.string_types):
                raise TypeError("query body must be a dict or string.")
            if isinstance(query_body, dict) and not query_body.get("query"):
                raise ValueError('query body must have valid query text with key "query".')
            if isinstance(query_body, six.string_types):
                return {"query": query_body}
        elif (
            self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.SqlQuery
            and not isinstance(query_body, six.string_types)
        ):
            raise TypeError("query body must be a string.")
        else:
            raise SystemError("Unexpected query compatibility mode.")

        return query_body

    def _UpdateSessionIfRequired(self, request_headers, response_result, response_headers):
        """
        Updates session if necessary.

        :param dict response_result:
        :param dict response_headers:
        :param dict response_headers

        :return:
            None, but updates the client session if necessary.

        """

        # if this request was made with consistency level as session, then update the session
        if response_result is None or response_headers is None:
            return

        is_session_consistency = False
        if http_constants.HttpHeaders.ConsistencyLevel in request_headers:
            if documents.ConsistencyLevel.Session == request_headers[http_constants.HttpHeaders.ConsistencyLevel]:
                is_session_consistency = True

        if is_session_consistency:
            # update session
            self.session.update_session(response_result, response_headers)

    PartitionResolverErrorMessage = (
        "Couldn't find any partition resolvers for the database link provided. "
        + "Ensure that the link you used when registering the partition resolvers "
        + "matches the link provided or you need to register both types of database "
        + "link(self link as well as ID based link)."
    )

    # Gets the collection id and path for the document
    def _GetContainerIdWithPathForItem(self, database_or_container_link, document, options):

        if not database_or_container_link:
            raise ValueError("database_or_container_link is None or empty.")

        if document is None:
            raise ValueError("document is None.")

        CosmosClientConnection.__ValidateResource(document)
        document = document.copy()
        if not document.get("id") and not options.get("disableAutomaticIdGeneration"):
            document["id"] = base.GenerateGuidId()

        collection_link = database_or_container_link

        if base.IsDatabaseLink(database_or_container_link):
            partition_resolver = self.GetPartitionResolver(database_or_container_link)

            if partition_resolver is not None:
                collection_link = partition_resolver.ResolveForCreate(document)
            else:
                raise ValueError(CosmosClientConnection.PartitionResolverErrorMessage)

        path = base.GetPathFromLink(collection_link, "docs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, document, path

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

    # Adds the partition key to options
    async def _AddPartitionKey(self, collection_link, document, options):
        collection_link = base.TrimBeginningAndEndingSlashes(collection_link)

        # TODO: Refresh the cache if partition is extracted automatically and we get a 400.1001

        # If the document collection link is present in the cache, then use the cached partitionkey definition
        if collection_link in self.partition_key_definition_cache:
            partitionKeyDefinition = self.partition_key_definition_cache.get(collection_link)
        # Else read the collection from backend and add it to the cache
        else:
            collection = await self.ReadContainer(collection_link)
            partitionKeyDefinition = collection.get("partitionKey")
            self.partition_key_definition_cache[collection_link] = partitionKeyDefinition

        # If the collection doesn't have a partition key definition, skip it as it's a legacy collection
        if partitionKeyDefinition:
            # If the user has passed in the partitionKey in options use that elase extract it from the document
            if "partitionKey" not in options:
                partitionKeyValue = self._ExtractPartitionKey(partitionKeyDefinition, document)
                options["partitionKey"] = partitionKeyValue

        return options

    # Extracts the partition key from the document using the partitionKey definition
    def _ExtractPartitionKey(self, partitionKeyDefinition, document):

        # Parses the paths into a list of token each representing a property
        partition_key_parts = base.ParsePaths(partitionKeyDefinition.get("paths"))
        # Check if the partitionKey is system generated or not
        is_system_key = partitionKeyDefinition["systemKey"] if "systemKey" in partitionKeyDefinition else False

        # Navigates the document to retrieve the partitionKey specified in the paths
        return self._retrieve_partition_key(partition_key_parts, document, is_system_key)

    # Navigates the document to retrieve the partitionKey specified in the partition key parts
    def _retrieve_partition_key(self, partition_key_parts, document, is_system_key):
        expected_matchCount = len(partition_key_parts)
        matchCount = 0
        partitionKey = document

        for part in partition_key_parts:
            # At any point if we don't find the value of a sub-property in the document, we return as Undefined
            if part not in partitionKey:
                return self._return_undefined_or_empty_partition_key(is_system_key)

            partitionKey = partitionKey.get(part)
            matchCount += 1
            # Once we reach the "leaf" value(not a dict), we break from loop
            if not isinstance(partitionKey, dict):
                break

        # Match the count of hops we did to get the partitionKey with the length of
        # partition key parts and validate that it's not a dict at that level
        if (matchCount != expected_matchCount) or isinstance(partitionKey, dict):
            return self._return_undefined_or_empty_partition_key(is_system_key)

        return partitionKey

    async def _GetQueryPlanThroughGateway(self, query, resource_link, **kwargs):
        supported_query_features = (documents._QueryFeature.Aggregate + "," +
                                    documents._QueryFeature.CompositeAggregate + "," +
                                    documents._QueryFeature.Distinct + "," +
                                    documents._QueryFeature.MultipleOrderBy + "," +
                                    documents._QueryFeature.OffsetAndLimit + "," +
                                    documents._QueryFeature.OrderBy + "," +
                                    documents._QueryFeature.Top)

        options = {
            "contentType": runtime_constants.MediaTypes.Json,
            "isQueryPlanRequest": True,
            "supportedQueryFeatures": supported_query_features,
            "queryVersion": http_constants.Versions.QueryVersion
            }

        resource_link = base.TrimBeginningAndEndingSlashes(resource_link)
        path = base.GetPathFromLink(resource_link, "docs")
        resource_id = base.GetResourceIdOrFullNameFromLink(resource_link)

        return await self.__QueryFeed(path,
                                "docs",
                                resource_id,
                                lambda r: r,
                                None,
                                query,
                                options,
                                is_query_plan=True,
                                **kwargs)

    @staticmethod
    def _return_undefined_or_empty_partition_key(is_system_key):
        if is_system_key:
            return _Empty
        return _Undefined

    @staticmethod
    def __ValidateResource(resource):
        id_ = resource.get("id")
        if id_:
            try:
                if id_.find("/") != -1 or id_.find("\\") != -1 or id_.find("?") != -1 or id_.find("#") != -1:
                    raise ValueError("Id contains illegal chars.")

                if id_[-1] == " ":
                    raise ValueError("Id ends with a space.")
            except AttributeError:
                raise_with_traceback(TypeError, message="Id type must be a string.")