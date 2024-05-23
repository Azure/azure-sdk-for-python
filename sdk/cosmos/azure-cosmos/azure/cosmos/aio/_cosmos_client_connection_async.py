# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

# pylint: disable=protected-access,too-many-lines

"""Document client class for the Azure Cosmos database service.
"""
import os
from urllib.parse import urlparse
from typing import (
    Callable, Dict, Any, Iterable, Mapping, Optional, List,
    Sequence, Tuple, Type, Union, cast
)

from typing_extensions import TypedDict
from urllib3.util.retry import Retry

from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials_async import AsyncTokenCredential
from azure.core import AsyncPipelineClient
from azure.core.pipeline.transport import HttpRequest, AsyncHttpResponse  # pylint: disable=no-legacy-azure-core-http-response-import
from azure.core.pipeline.policies import (
    AsyncHTTPPolicy,
    ContentDecodePolicy,
    HeadersPolicy,
    UserAgentPolicy,
    NetworkTraceLoggingPolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    ProxyPolicy)

from .. import _base as base
from .. import documents
from .._routing import routing_range
from ..documents import ConnectionPolicy, DatabaseAccount
from .._constants import _Constants as Constants
from .. import http_constants, exceptions
from . import _query_iterable_async as query_iterable
from .. import _runtime_constants as runtime_constants
from .. import _request_object
from . import _asynchronous_request as asynchronous_request
from . import _global_endpoint_manager_async as global_endpoint_manager_async
from .._routing.aio.routing_map_provider import SmartRoutingMapProvider
from ._retry_utility_async import _ConnectionRetryPolicy
from .. import _session
from .. import _utils
from ..partition_key import (
    _Undefined,
    PartitionKey,
    _return_undefined_or_empty_partition_key,
    NonePartitionKeyValue
)
from ._auth_policy_async import AsyncCosmosBearerTokenCredentialPolicy
from .._cosmos_http_logging_policy import CosmosHttpLoggingPolicy
from .._range_partition_resolver import RangePartitionResolver


PartitionKeyType = Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]]  # pylint: disable=line-too-long
class CredentialDict(TypedDict, total=False):
    masterKey: str
    resourceTokens: Mapping[str, Any]
    permissionFeed: Iterable[Mapping[str, Any]]
    clientSecretCredential: AsyncTokenCredential


class CosmosClientConnection:  # pylint: disable=too-many-public-methods,too-many-instance-attributes
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
            url_connection: str,
            auth: CredentialDict,
            connection_policy: Optional[ConnectionPolicy] = None,
            consistency_level: Optional[str] = None,
            **kwargs: Any
    ) -> None:
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
        self.master_key: Optional[str] = None
        self.resource_tokens: Optional[Mapping[str, Any]] = None
        self.aad_credentials: Optional[AsyncTokenCredential] = None
        if auth is not None:
            self.master_key = auth.get("masterKey")
            self.resource_tokens = auth.get("resourceTokens")
            self.aad_credentials = auth.get("clientSecretCredential")

            if auth.get("permissionFeed"):
                self.resource_tokens = {}
                for permission_feed in auth["permissionFeed"]:
                    resource_parts = permission_feed["resource"].split("/")
                    id_ = resource_parts[-1]
                    self.resource_tokens[id_] = permission_feed["_token"]

        self.connection_policy = connection_policy or ConnectionPolicy()
        self.partition_resolvers: Dict[str, RangePartitionResolver] = {}
        self.partition_key_definition_cache: Dict[str, Any] = {}
        self.default_headers: Dict[str, Any] = {
            http_constants.HttpHeaders.CacheControl: "no-cache",
            http_constants.HttpHeaders.Version: http_constants.Versions.CurrentVersion,
            # For single partition query with aggregate functions we would try to accumulate the results on the SDK.
            # We need to set continuation as not expected.
            http_constants.HttpHeaders.IsContinuationExpected: False,
        }

        if consistency_level is not None:
            self.default_headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level

        # Keeps the latest response headers from the server.
        self.last_response_headers: Dict[str, Any] = {}
        self.UseMultipleWriteLocations = False
        self._global_endpoint_manager = global_endpoint_manager_async._GlobalEndpointManager(self)

        retry_policy = None
        if isinstance(self.connection_policy.ConnectionRetryConfiguration, AsyncHTTPPolicy):
            retry_policy = self.connection_policy.ConnectionRetryConfiguration
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, int):
            retry_policy = _ConnectionRetryPolicy(total=self.connection_policy.ConnectionRetryConfiguration)
        elif isinstance(self.connection_policy.ConnectionRetryConfiguration, Retry):
            # Convert a urllib3 retry policy to a Pipeline policy
            retry_policy = _ConnectionRetryPolicy(
                retry_total=self.connection_policy.ConnectionRetryConfiguration.total,
                retry_connect=self.connection_policy.ConnectionRetryConfiguration.connect,
                retry_read=self.connection_policy.ConnectionRetryConfiguration.read,
                retry_status=self.connection_policy.ConnectionRetryConfiguration.status,
                retry_backoff_max=self.connection_policy.ConnectionRetryConfiguration.DEFAULT_BACKOFF_MAX,
                retry_on_status_codes=list(self.connection_policy.ConnectionRetryConfiguration.status_forcelist),
                retry_backoff_factor=self.connection_policy.ConnectionRetryConfiguration.backoff_factor
            )
        else:
            raise TypeError(
                "Unsupported retry policy. Must be an azure.cosmos.ConnectionRetryPolicy, int, or urllib3.Retry")

        proxies = kwargs.pop('proxies', {})
        if self.connection_policy.ProxyConfiguration and self.connection_policy.ProxyConfiguration.Host:
            host = self.connection_policy.ProxyConfiguration.Host
            url = urlparse(host)
            proxy = host if url.port else host + ":" + str(self.connection_policy.ProxyConfiguration.Port)
            proxies.update({url.scheme: proxy})

        self._user_agent = _utils.get_user_agent_async()

        credentials_policy = None
        if self.aad_credentials:
            scope = base.create_scope_from_url(self.url_connection)
            credentials_policy = AsyncCosmosBearerTokenCredentialPolicy(self.aad_credentials, scope)

        policies = [
            HeadersPolicy(**kwargs),
            ProxyPolicy(proxies=proxies),
            UserAgentPolicy(base_user_agent=self._user_agent, **kwargs),
            ContentDecodePolicy(),
            retry_policy,
            credentials_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            CosmosHttpLoggingPolicy(enable_diagnostics_logging=kwargs.pop("enable_diagnostics_logging", False),
                                    **kwargs),
        ]

        transport = kwargs.pop("transport", None)
        self.pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse] = AsyncPipelineClient(
            base_url=url_connection,
            transport=transport,
            policies=policies
        )
        self._setup_kwargs: Dict[str, Any] = kwargs
        self.session: Optional[_session.Session] = None

        # Query compatibility mode.
        # Allows to specify compatibility mode used by client when making query requests. Should be removed when
        # application/sql is no longer supported.
        self._query_compatibility_mode: int = CosmosClientConnection._QueryCompatibilityMode.Default

        # Routing map provider
        self._routing_map_provider: SmartRoutingMapProvider = SmartRoutingMapProvider(self)

    @property
    def _Session(self) -> Optional[_session.Session]:
        """Gets the session object from the client.
         :returns: the session for the client.
         :rtype: _session.Session
        """
        return self.session

    @_Session.setter
    def _Session(self, session: Optional[_session.Session]) -> None:
        """Sets a session object on the document client.

        This will override the existing session
        :param _session.Session session: the client session to set.
        """
        self.session = session

    @property
    def _WriteEndpoint(self) -> str:
        """Gets the current write endpoint for a geo-replicated database account.
        :returns: the write endpoint for the database account
        :rtype: str
        """
        return self._global_endpoint_manager.get_write_endpoint()

    @property
    def _ReadEndpoint(self) -> str:
        """Gets the current read endpoint for a geo-replicated database account.
        :returns: the read endpoint for the database account
        :rtype: str
        """
        return self._global_endpoint_manager.get_read_endpoint()

    async def _setup(self) -> None:
        if 'database_account' not in self._setup_kwargs:
            database_account = await self._global_endpoint_manager._GetDatabaseAccount(
                **self._setup_kwargs
            )
            self._setup_kwargs['database_account'] = database_account
            await self._global_endpoint_manager.force_refresh(self._setup_kwargs['database_account'])
        else:
            database_account = self._setup_kwargs['database_account']

        # Save the choice that was made (either None or some value) and branch to set or get the consistency
        if self.default_headers.get(http_constants.HttpHeaders.ConsistencyLevel):
            user_defined_consistency = self.default_headers[http_constants.HttpHeaders.ConsistencyLevel]
        else:
            # Use database_account if no consistency passed in to verify consistency level to be used
            user_defined_consistency = self._check_if_account_session_consistency(database_account)

        if user_defined_consistency == documents.ConsistencyLevel.Session:
            # create a Session if the user wants Session consistency
            self.session = _session.Session(self.url_connection)
        else:
            self.session = None

    def _check_if_account_session_consistency(self, database_account: DatabaseAccount) -> Optional[str]:
        """Checks account consistency level to set header if needed.

        :param database_account: The database account to be used to check consistency levels
        :type database_account: ~azure.cosmos.documents.DatabaseAccount
        :returns consistency_level: the account consistency level
        :rtype: str
        """
        # Set to default level present in account
        user_consistency_policy = database_account.ConsistencyPolicy
        if user_consistency_policy:
            consistency_level = user_consistency_policy[Constants.DefaultConsistencyLevel]
            if consistency_level == documents.ConsistencyLevel.Session:
                # We only set the header if we're using session consistency in the account in order to keep
                # the current update_session logic which uses the header
                self.default_headers[http_constants.HttpHeaders.ConsistencyLevel] = consistency_level
            return consistency_level
        return None

    def _GetDatabaseIdWithPathForUser(
        self,
        database_link: str,
        user: Mapping[str, Any]
    ) -> Tuple[Optional[str], str]:
        base._validate_resource(user)
        path = base.GetPathFromLink(database_link, "users")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return database_id, path

    def _GetContainerIdWithPathForSproc(
        self,
        collection_link: str,
        sproc: Mapping[str, Any]
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        base._validate_resource(sproc)
        sproc = dict(sproc)
        if sproc.get("serverScript"):
            sproc["body"] = str(sproc.pop("serverScript", ""))
        elif sproc.get("body"):
            sproc["body"] = str(sproc["body"])
        path = base.GetPathFromLink(collection_link, "sprocs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, sproc

    def _GetContainerIdWithPathForTrigger(
        self,
        collection_link: str,
        trigger: Mapping[str, Any]
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        base._validate_resource(trigger)
        trigger = dict(trigger)
        if trigger.get("serverScript"):
            trigger["body"] = str(trigger.pop("serverScript", ""))
        elif trigger.get("body"):
            trigger["body"] = str(trigger["body"])

        path = base.GetPathFromLink(collection_link, "triggers")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, trigger

    def _GetContainerIdWithPathForUDF(
        self,
        collection_link: str,
        udf: Mapping[str, Any]
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        base._validate_resource(udf)
        udf = dict(udf)
        if udf.get("serverScript"):
            udf["body"] = str(udf.pop("serverScript", ""))
        elif udf.get("body"):
            udf["body"] = str(udf["body"])

        path = base.GetPathFromLink(collection_link, "udfs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return collection_id, path, udf

    async def GetDatabaseAccount(
        self,
        url_connection: Optional[str] = None,
        **kwargs: Any
    ) -> documents.DatabaseAccount:
        """Gets database account info.

        :param str url_connection: the endpoint used to get the database account
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
        database_account.ConsistencyPolicy = result.get(Constants.UserConsistencyPolicy)

        # WritableLocations and ReadableLocations fields will be available only for geo-replicated database accounts
        if Constants.WritableLocations in result:
            database_account._WritableLocations = result[Constants.WritableLocations]
        if Constants.ReadableLocations in result:
            database_account._ReadableLocations = result[Constants.ReadableLocations]
        if Constants.EnableMultipleWritableLocations in result:
            database_account._EnableMultipleWritableLocations = result[
                Constants.EnableMultipleWritableLocations
            ]

        self.UseMultipleWriteLocations = (
                self.connection_policy.UseMultipleWriteLocations and database_account._EnableMultipleWritableLocations
        )
        return database_account

    async def CreateDatabase(
        self,
        database: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

        base._validate_resource(database)
        path = "/dbs"
        return await self.Create(database, path, "dbs", None, None, options, **kwargs)

    async def CreateUser(
        self,
        database_link: str,
        user: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def CreateContainer(
        self,
        database_link: str,
        collection: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ):
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

        base._validate_resource(collection)
        path = base.GetPathFromLink(database_link, "colls")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        return await self.Create(collection, path, "colls", database_id, None, options, **kwargs)

    async def CreateItem(
        self,
        database_or_container_link: str,
        document: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Creates a document in a collection.

        :param str database_or_container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param dict document:
            The Azure Cosmos document to create.
        :param dict options:
            The request options for the request.
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

    async def CreatePermission(
        self,
        user_link: str,
        permission: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Create(permission, path, "permissions", user_id, None, options, **kwargs)

    async def CreateUserDefinedFunction(
        self,
        collection_link: str,
        udf: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Creates a user-defined function in a collection.

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
        return await self.Create(udf, path, "udfs", collection_id, None, options, **kwargs)

    async def CreateTrigger(
        self,
        collection_link: str,
        trigger: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Create(trigger, path, "triggers", collection_id, None, options, **kwargs)

    async def CreateStoredProcedure(
        self,
        collection_link: str,
        sproc: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
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
        return await self.Create(sproc, path, "sprocs", collection_id, None, options, **kwargs)

    async def ExecuteStoredProcedure(
        self,
        sproc_link: str,
        params: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        initial_headers.update({http_constants.HttpHeaders.Accept: (runtime_constants.MediaTypes.Json)})

        if params and not isinstance(params, list):
            params = [params]

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        headers = base.GetHeaders(self, initial_headers, "post", path, sproc_id, "sprocs", options)

        # ExecuteStoredProcedure will use WriteEndpoint since it uses POST operation
        request_params = _request_object.RequestObject("sprocs", documents._OperationType.ExecuteJavaScript)
        result, self.last_response_headers = await self.__Post(path, request_params, params, headers, **kwargs)
        return result

    async def Create(
        self,
        body: Dict[str, Any],
        path: str,
        typ: str,
        id: Optional[str],
        initial_headers: Optional[Mapping[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Creates an Azure Cosmos resource and returns it.

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
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "post", path, id, typ, options)
        # Create will use WriteEndpoint since it uses POST operation

        request_params = _request_object.RequestObject(typ, documents._OperationType.Create)
        result, last_response_headers = await self.__Post(path, request_params, body, headers, **kwargs)
        self.last_response_headers = last_response_headers

        # update session for write request
        self._UpdateSessionIfRequired(headers, result, last_response_headers)
        if response_hook:
            response_hook(last_response_headers, result)
        return result

    async def UpsertUser(
        self,
        database_link: str,
        user: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def UpsertPermission(
        self,
        user_link: str,
        permission: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Upsert(permission, path, "permissions", user_id, None, options, **kwargs)

    async def UpsertItem(
        self,
        database_or_container_link: str,
        document: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Upserts a document in a collection.

        :param str database_or_container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param dict document:
            The Azure Cosmos document to upsert.
        :param dict options:
            The request options for the request.
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

    async def Upsert(
        self,
        body: Dict[str, Any],
        path: str,
        typ: str,
        id: Optional[str],
        initial_headers: Optional[Mapping[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Upserts an Azure Cosmos resource and returns it.

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
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "post", path, id, typ, options)

        headers[http_constants.HttpHeaders.IsUpsert] = True

        # Upsert will use WriteEndpoint since it uses POST operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Upsert)
        result, last_response_headers = await self.__Post(path, request_params, body, headers, **kwargs)
        self.last_response_headers = last_response_headers
        # update session for write request
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        if response_hook:
            response_hook(last_response_headers, result)
        return result

    async def __Post(
        self,
        path: str,
        request_params: _request_object.RequestObject,
        body: Optional[Union[str, List[Dict[str, Any]], Dict[str, Any]]],
        req_headers: Dict[str, Any],
        **kwargs: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Azure Cosmos 'POST' async http request.

        :param str path: the url to be used for the request.
        :param ~azure.cosmos._request_object.RequestObject request_params: the request parameters.
        :param Union[str, List[Dict[str, Any]], Dict[Any, Any]] body: the request body.
        :param Dict[str, Any] req_headers: the request headers.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
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

    async def ReadDatabase(
        self,
        database_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def ReadContainer(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def ReadItem(
        self,
        document_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def ReadUser(
        self,
        user_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Read(path, "users", user_id, None, options, **kwargs)

    async def ReadPermission(
        self,
        permission_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Read(path, "permissions", permission_id, None, options, **kwargs)

    async def ReadUserDefinedFunction(
        self,
        udf_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Reads a user-defined function.

        :param str udf_link:
            The link to the user-defined function.
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
        return await self.Read(path, "udfs", udf_id, None, options, **kwargs)

    async def ReadStoredProcedure(
        self,
        sproc_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Read(path, "sprocs", sproc_id, None, options, **kwargs)

    async def ReadTrigger(
        self,
        trigger_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        return await self.Read(path, "triggers", trigger_id, None, options, **kwargs)

    async def ReadConflict(
        self,
        conflict_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

    async def Read(
        self,
        path: str,
        typ: str,
        id: Optional[str],
        initial_headers: Optional[Mapping[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Reads an Azure Cosmos resource and returns it.

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
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "get", path, id, typ, options)
        # Read will use ReadEndpoint since it uses GET operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Read)
        result, last_response_headers = await self.__Get(path, request_params, headers, **kwargs)
        self.last_response_headers = last_response_headers
        if response_hook:
            response_hook(last_response_headers, result)
        return result

    async def __Get(
        self,
        path: str,
        request_params: _request_object.RequestObject,
        req_headers: Dict[str, Any],
        **kwargs: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Azure Cosmos 'GET' async http request.

        :param str path: the url to be used for the request.
        :param ~azure.cosmos._request_object.RequestObject request_params: the request parameters.
        :param Dict[str, Any] req_headers: the request headers.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
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

    async def ReplaceUser(
        self,
        user_link: str,
        user: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

        base._validate_resource(user)
        path = base.GetPathFromLink(user_link)
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return await self.Replace(user, path, "users", user_id, None, options, **kwargs)

    async def ReplacePermission(
        self,
        permission_link: str,
        permission: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

        base._validate_resource(permission)
        path = base.GetPathFromLink(permission_link)
        permission_id = base.GetResourceIdOrFullNameFromLink(permission_link)
        return await self.Replace(permission, path, "permissions", permission_id, None, options, **kwargs)

    async def ReplaceContainer(
        self,
        collection_link: str,
        collection: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

        base._validate_resource(collection)
        path = base.GetPathFromLink(collection_link)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        return await self.Replace(collection, path, "colls", collection_id, None, options, **kwargs)

    async def ReplaceUserDefinedFunction(
        self,
        udf_link: str,
        udf: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replaces a user-defined function and returns it.

        :param str udf_link:
            The link to the user-defined function.
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

        base._validate_resource(udf)
        udf = udf.copy()
        if udf.get("serverScript"):
            udf["body"] = str(udf.pop("serverScript", ""))
        elif udf.get("body"):
            udf["body"] = str(udf["body"])

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        return await self.Replace(udf, path, "udfs", udf_id, None, options, **kwargs)

    async def ReplaceTrigger(
        self,
        trigger_link: str,
        trigger: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
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

        base._validate_resource(trigger)
        trigger = trigger.copy()
        if trigger.get("serverScript"):
            trigger["body"] = str(trigger.pop("serverScript", ""))
        elif trigger.get("body"):
            trigger["body"] = str(trigger["body"])

        path = base.GetPathFromLink(trigger_link)
        trigger_id = base.GetResourceIdOrFullNameFromLink(trigger_link)
        return await self.Replace(trigger, path, "triggers", trigger_id, None, options, **kwargs)

    async def ReplaceItem(
        self,
        document_link: str,
        new_document: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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
        base._validate_resource(new_document)
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

    async def PatchItem(
        self,
        document_link: str,
        operations: List[Dict[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Patches a document and returns it.

        :param str document_link: The link to the document.
        :param list operations: The operations for the patch request.
        :param dict options: The request options for the request.
        :return:
            The new Document.
        :rtype:
            dict

        """
        response_hook = kwargs.pop("response_hook", None)
        path = base.GetPathFromLink(document_link)
        document_id = base.GetResourceIdOrFullNameFromLink(document_link)
        typ = "docs"

        if options is None:
            options = {}

        initial_headers = self.default_headers
        headers = base.GetHeaders(self, initial_headers, "patch", path, document_id, typ, options)
        # Patch will use WriteEndpoint since it uses PUT operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Patch)
        request_data = {}
        if options.get("filterPredicate"):
            request_data["condition"] = options.get("filterPredicate")
        request_data["operations"] = operations
        result, last_response_headers = await self.__Patch(path, request_params, request_data, headers, **kwargs)
        self.last_response_headers = last_response_headers

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, last_response_headers)
        if response_hook:
            response_hook(last_response_headers, result)
        return result

    async def ReplaceOffer(
        self,
        offer_link: str,
        offer: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replaces an offer and returns it.

        :param str offer_link:
            The link to the offer.
        :param dict offer:
        :return:
            The replaced Offer.
        :rtype:
            dict

        """
        base._validate_resource(offer)
        path = base.GetPathFromLink(offer_link)
        offer_id = base.GetResourceIdOrFullNameFromLink(offer_link)
        return await self.Replace(offer, path, "offers", offer_id, None, None, **kwargs)

    async def ReplaceStoredProcedure(
        self,
        sproc_link: str,
        sproc: Dict[str, Any],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
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

        base._validate_resource(sproc)
        sproc = sproc.copy()
        if sproc.get("serverScript"):
            sproc["body"] = str(sproc.pop("serverScript", ""))
        elif sproc.get("body"):
            sproc["body"] = str(sproc["body"])

        path = base.GetPathFromLink(sproc_link)
        sproc_id = base.GetResourceIdOrFullNameFromLink(sproc_link)
        return await self.Replace(sproc, path, "sprocs", sproc_id, None, options, **kwargs)

    async def Replace(
        self,
        resource: Dict[str, Any],
        path: str,
        typ: str,
        id: Optional[str],
        initial_headers: Optional[Mapping[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replaces an Azure Cosmos resource and returns it.

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
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "put", path, id, typ, options)
        # Replace will use WriteEndpoint since it uses PUT operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Replace)
        result, last_response_headers = await self.__Put(path, request_params, resource, headers, **kwargs)
        self.last_response_headers = last_response_headers

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, self.last_response_headers)
        if response_hook:
            response_hook(last_response_headers, result)
        return result

    async def __Put(
        self,
        path: str,
        request_params: _request_object.RequestObject,
        body: Dict[str, Any],
        req_headers: Dict[str, Any],
        **kwargs: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Azure Cosmos 'PUT' async http request.

        :param str path: the url to be used for the request.
        :param ~azure.cosmos._request_object.RequestObject request_params: the request parameters.
        :param Union[str, unicode, Dict[Any, Any]] body: the request body.
        :param Dict[str, Any] req_headers: the request headers.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
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

    async def __Patch(
        self,
        path: str,
        request_params: _request_object.RequestObject,
        request_data: Dict[str, Any],
        req_headers: Dict[str, Any],
        **kwargs: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Azure Cosmos 'PATCH' http request.

        :param str path: the url to be used for the request.
        :param ~azure.cosmos._request_object.RequestObject request_params: the request parameters.
        :param Union[str, unicode, Dict[Any, Any]] request_data: the request body.
        :param Dict[str, Any] req_headers: the request headers.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
        """
        request = self.pipeline_client.patch(url=path, headers=req_headers)
        return await asynchronous_request.AsynchronousRequest(
            client=self,
            request_params=request_params,
            global_endpoint_manager=self._global_endpoint_manager,
            connection_policy=self.connection_policy,
            pipeline_client=self.pipeline_client,
            request=request,
            request_data=request_data,
            **kwargs
        )

    async def DeleteDatabase(
        self,
        database_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Deletes a database.

        :param str database_link:
            The link to the database.
        :param dict options:
            The request options for the request.
        :return:
            The deleted Database.
        :rtype:
            None
        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(database_link)
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)
        await self.DeleteResource(path, "dbs", database_id, None, options, **kwargs)

    async def DeleteUser(
        self,
        user_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "users", user_id, None, options, **kwargs)

    async def DeletePermission(
        self,
        permission_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "permissions", permission_id, None, options, **kwargs)

    async def DeleteContainer(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "colls", collection_id, None, options, **kwargs)

    async def DeleteItem(
        self,
        document_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "docs", document_id, None, options, **kwargs)

    async def DeleteUserDefinedFunction(
        self,
        udf_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Deletes a user-defined function.

        :param str udf_link:
            The link to the user-defined function.
        :param dict options:
            The request options for the request.
        :return:
            The deleted UDF.
        :rtype:
            None
        """
        if options is None:
            options = {}

        path = base.GetPathFromLink(udf_link)
        udf_id = base.GetResourceIdOrFullNameFromLink(udf_link)
        await self.DeleteResource(path, "udfs", udf_id, None, options, **kwargs)

    async def DeleteTrigger(
        self,
        trigger_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "triggers", trigger_id, None, options, **kwargs)

    async def DeleteStoredProcedure(
        self,
        sproc_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "sprocs", sproc_id, None, options, **kwargs)

    async def DeleteConflict(
        self,
        conflict_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
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
        await self.DeleteResource(path, "conflicts", conflict_id, None, options, **kwargs)

    async def DeleteResource(
        self,
        path: str,
        typ: str,
        id: Optional[str],
        initial_headers: Optional[Mapping[str, Any]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Deletes an Azure Cosmos resource and returns it.

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
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        initial_headers = initial_headers or self.default_headers
        headers = base.GetHeaders(self, initial_headers, "delete", path, id, typ, options)
        # Delete will use WriteEndpoint since it uses DELETE operation
        request_params = _request_object.RequestObject(typ, documents._OperationType.Delete)
        result, last_response_headers = await self.__Delete(path, request_params, headers, **kwargs)
        self.last_response_headers = last_response_headers

        # update session for request mutates data on server side
        self._UpdateSessionIfRequired(headers, result, last_response_headers)
        if response_hook:
            response_hook(last_response_headers, None)

    async def __Delete(
        self,
        path: str,
        request_params: _request_object.RequestObject,
        req_headers: Dict[str, Any],
        **kwargs: Any
    ) -> Tuple[None, Dict[str, Any]]:
        """Azure Cosmos 'DELETE' async http request.

        :param str path: the url to be used for the request.
        :param ~azure.cosmos._request_object.RequestObject request_params: the request parameters.
        :param Dict[str, Any] req_headers: the request headers.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
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

    async def Batch(
        self,
        collection_link: str,
        batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ...]], Tuple[str, Tuple[Any, ...], Dict[str, Any]]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Executes the given operations in transactional batch.

        :param str collection_link: The link to the collection
        :param list batch_operations: The batch of operations for the batch request.
        :param dict options: The request options for the request.

        :return:
            The result of the batch operation.
        :rtype:
            list

        """
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link, "docs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        formatted_operations = base._format_batch_operations(batch_operations)

        results, last_response_headers = await self._Batch(
            formatted_operations,
            path,
            collection_id,
            options,
            **kwargs)
        self.last_response_headers = last_response_headers

        final_responses = []
        is_error = False
        error_status = 0
        error_index = 0
        for i, result in enumerate(results):
            final_responses.append(result)
            status_code = int(result["statusCode"])
            if status_code >= 400:
                is_error = True
                if status_code != 424:  # Find the operation that had the error
                    error_status = status_code
                    error_index = i
        if is_error:
            raise exceptions.CosmosBatchOperationError(
                error_index=error_index,
                headers=self.last_response_headers,
                status_code=error_status,
                message="There was an error in the transactional batch on" +
                        " index {}. Error message: {}".format(
                            str(error_index),
                            Constants.ERROR_TRANSLATIONS.get(error_status)
                ),
                operation_responses=final_responses
            )
        if response_hook:
            response_hook(last_response_headers, final_responses)
        return final_responses

    async def _Batch(
        self,
        batch_operations: List[Dict[str, Any]],
        path: str,
        collection_id: Optional[str],
        options: Mapping[str, Any],
        **kwargs: Any
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        initial_headers = self.default_headers.copy()
        base._populate_batch_headers(initial_headers)
        headers = base.GetHeaders(self, initial_headers, "post", path, collection_id, "docs", options)
        request_params = _request_object.RequestObject("docs", documents._OperationType.Batch)
        result = await self.__Post(path, request_params, batch_operations, headers, **kwargs)
        return cast(Tuple[List[Dict[str, Any]], Dict[str, Any]], result)

    def _ReadPartitionKeyRanges(
        self,
        collection_link: str,
        feed_options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self._QueryPartitionKeyRanges(collection_link, None, feed_options, **kwargs)

    def _QueryPartitionKeyRanges(
        self,
        collection_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(collection_link, "pkranges")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "pkranges", collection_id, lambda r: r["PartitionKeyRanges"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadDatabases(
        self,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self.QueryDatabases(None, options, **kwargs)

    def QueryDatabases(
        self,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    "/dbs", "dbs", "", lambda r: r["Databases"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadContainers(
        self,
        database_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self.QueryContainers(database_link, None, options, **kwargs)

    def QueryContainers(
        self,
        database_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(database_link, "colls")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "colls", database_id, lambda r: r["DocumentCollections"],
                    lambda _, body: body, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadItems(
        self,
        collection_link: str,
        feed_options: Optional[Mapping[str, Any]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Reads all documents in a collection.

        :param str collection_link: The link to the document collection.
        :param dict feed_options: The additional options for the operation.
        :param response_hook: A callable invoked with the response metadata.
        :type response_hook: Callable[[Dict[str, str], Dict[str, Any]]
        :return: Query Iterable of Documents.
        :rtype: query_iterable.QueryIterable

        """
        if feed_options is None:
            feed_options = {}

        return self.QueryItems(collection_link, None, feed_options, response_hook=response_hook, **kwargs)

    def QueryItems(
        self,
        database_or_container_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        partition_key: Optional[PartitionKeyType] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Queries documents in a collection.

        :param str database_or_container_link:
            The link to the database when using partitioning, otherwise link to the document collection.
        :param (str or dict) query: the query to be used
        :param dict options: The request options for the request.
        :param str partition_key: Partition key for the query(default value None)
        :param response_hook: A callable invoked with the response metadata.
        :type response_hook: Callable[[Dict[str, str], Dict[str, Any]]
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

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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

    def QueryItemsChangeFeed(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Queries documents change feed in a collection.

        :param str collection_link: The link to the document collection.
        :param dict options: The request options for the request.
        :param response_hook: A callable invoked with the response metadata.
        :type response_hook: Callable[[Dict[str, str], Dict[str, Any]]
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
            self,
            collection_link: str,
            resource_type: str,
            options: Optional[Mapping[str, Any]] = None,
            partition_key_range_id: Optional[str] = None,
            response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Queries change feed of a resource in a collection.

        :param str collection_link: The link to the document collection.
        :param str resource_type: The type of the resource.
        :param dict options: The request options for the request.
        :param str partition_key_range_id: Specifies partition key range id.
        :param response_hook: A callable invoked with the response metadata
        :type response_hook: Callable[[Dict[str, str], Dict[str, Any]]
        :return:
            Query Iterable of Documents.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}
        else:
            options = dict(options)
        options["changeFeed"] = True

        resource_key_map = {"Documents": "docs"}

        # For now, change feed only supports Documents and Partition Key Range resource type
        if resource_type not in resource_key_map:
            raise NotImplementedError(resource_type + " change feed query is not supported.")

        resource_key = resource_key_map[resource_type]
        path = base.GetPathFromLink(collection_link, resource_key)
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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

    def QueryOffers(
        self,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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

    def ReadUsers(
        self,
        database_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Reads all users in a database.

        :param str database_link:
            The link to the database.
        :param dict[str, Any] options:
            The request options for the request.
        :return:
            Query iterable of Users.
        :rtype:
            query_iterable.QueryIterable

        """
        if options is None:
            options = {}

        return self.QueryUsers(database_link, None, options, **kwargs)

    def QueryUsers(
        self,
        database_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(database_link, "users")
        database_id = base.GetResourceIdOrFullNameFromLink(database_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "users", database_id, lambda r: r["Users"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadPermissions(
        self,
        user_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self.QueryPermissions(user_link, None, options, **kwargs)

    def QueryPermissions(
        self,
        user_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(user_link, "permissions")
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "permissions", user_id, lambda r: r["Permissions"], lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadStoredProcedures(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self.QueryStoredProcedures(collection_link, None, options, **kwargs)

    def QueryStoredProcedures(
        self,
        collection_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(collection_link, "sprocs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "sprocs", collection_id, lambda r: r["StoredProcedures"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadTriggers(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        return self.QueryTriggers(collection_link, None, options, **kwargs)

    def QueryTriggers(
        self,
        collection_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        path = base.GetPathFromLink(collection_link, "triggers")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "triggers", collection_id, lambda r: r["Triggers"], lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadUserDefinedFunctions(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Reads all user-defined functions in a collection.

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

        return self.QueryUserDefinedFunctions(collection_link, None, options, **kwargs)

    def QueryUserDefinedFunctions(
        self,
        collection_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Queries user-defined functions in a collection.

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

        path = base.GetPathFromLink(collection_link, "udfs")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            return (
                await self.__QueryFeed(
                    path, "udfs", collection_id, lambda r: r["UserDefinedFunctions"],
                    lambda _, b: b, query, options, **kwargs
                ),
                self.last_response_headers,
            )

        return AsyncItemPaged(
            self, query, options, fetch_function=fetch_fn, page_iterator_class=query_iterable.QueryIterable
        )

    def ReadConflicts(
        self,
        collection_link: str,
        feed_options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

    def QueryConflicts(
        self,
        collection_link: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
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

        async def fetch_fn(options: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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

    async def QueryFeed(
        self,
        path: str,
        collection_id: str,
        query: Optional[Union[str, Dict[str, Any]]],
        options: Mapping[str, Any],
        partition_key_range_id: Optional[str] = None,
        **kwargs: Any
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Query Feed for Document Collection resource.

        :param str path: Path to the document collection.
        :param str collection_id: Id of the document collection.
        :param (str or dict) query:
        :param dict options: The request options for the request.
        :param str partition_key_range_id: Partition key range id.
        :return: Tuple of (result, headers).
        :rtype: tuple of (dict, dict)
        """
        return (
            await self.__QueryFeed(
                path,
                "docs",
                collection_id,
                lambda r: r["Documents"],
                lambda _, b: b,
                query,
                options,
                partition_key_range_id,
                **kwargs
            ),
            self.last_response_headers,
        )

    async def __QueryFeed(  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self,
        path: str,
        typ: str,
        id_: Optional[str],
        result_fn: Callable[[Dict[str, Any]], List[Dict[str, Any]]],
        create_fn: Optional[Callable[['CosmosClientConnection', Dict[str, Any]], Dict[str, Any]]],
        query: Optional[Union[str, Dict[str, Any]]],
        options: Optional[Mapping[str, Any]] = None,
        partition_key_range_id: Optional[str] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        is_query_plan: bool = False,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
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
            Specifies if the call is to fetch query plan
        :returns: A list of the queried resources.
        :rtype: list
        :raises SystemError: If the query compatibility mode is undefined.
        """
        if options is None:
            options = {}

        if query:
            __GetBodiesFromQueryResult = result_fn
        else:

            def __GetBodiesFromQueryResult(result: Dict[str, Any]) -> List[Dict[str, Any]]:
                if create_fn and result is not None:
                    return [create_fn(self, body) for body in result_fn(result)]
                # If there is no change feed, the result data is empty and result is None.
                # This case should be interpreted as an empty array.
                return []

        initial_headers = self.default_headers.copy()
        # Copy to make sure that default_headers won't be changed.
        if query is None:
            # Query operations will use ReadEndpoint even though it uses GET(for feed requests)
            request_params = _request_object.RequestObject(
                typ,
                documents._OperationType.QueryPlan if is_query_plan else documents._OperationType.ReadFeed
            )
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
                self._query_compatibility_mode in (CosmosClientConnection._QueryCompatibilityMode.Default,
                                                   CosmosClientConnection._QueryCompatibilityMode.Query)):
            initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.QueryJson
        elif self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.SqlQuery:
            initial_headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.SQL
        else:
            raise SystemError("Unexpected query compatibility mode.")

        # Query operations will use ReadEndpoint even though it uses POST(for regular query operations)
        request_params = _request_object.RequestObject(typ, documents._OperationType.SqlQuery)
        req_headers = base.GetHeaders(self, initial_headers, "post", path, id_, typ, options, partition_key_range_id)

        # check if query has prefix partition key
        cont_prop = kwargs.pop("containerProperties", None)
        partition_key = options.get("partitionKey", None)
        isPrefixPartitionQuery = False
        partition_key_definition = None
        if cont_prop:
            cont_prop = await cont_prop()
            pk_properties = cont_prop["partitionKey"]
            partition_key_definition = PartitionKey(path=pk_properties["paths"], kind=pk_properties["kind"])
            if partition_key_definition.kind == "MultiHash" and \
                    (isinstance(partition_key, List) and \
                     len(partition_key_definition['paths']) != len(partition_key)):
                isPrefixPartitionQuery = True

        if isPrefixPartitionQuery and partition_key_definition:
            # here get the overlapping ranges
            req_headers.pop(http_constants.HttpHeaders.PartitionKey, None)
            feedrangeEPK = partition_key_definition._get_epk_range_for_prefix_partition_key(
                partition_key)  # cspell:disable-line
            over_lapping_ranges = await self._routing_map_provider.get_overlapping_ranges(id_, [feedrangeEPK])
            results: Dict[str, Any] = {}
            # For each over lapping range we will take a sub range of the feed range EPK that overlaps with the over
            # lapping physical partition. The EPK sub range will be one of four:
            # 1) Will have a range min equal to the feed range EPK min, and a range max equal to the over lapping
            # partition
            # 2) Will have a range min equal to the over lapping partition range min, and a range max equal to the
            # feed range EPK range max.
            # 3) will match exactly with the current over lapping physical partition, so we just return the over lapping
            # physical partition's partition key id.
            # 4) Will equal the feed range EPK since it is a sub range of a single physical partition
            for over_lapping_range in over_lapping_ranges:
                single_range = routing_range.Range.PartitionKeyRangeToRange(over_lapping_range)
                # Since the range min and max are all Upper Cased string Hex Values,
                # we can compare the values lexicographically
                EPK_sub_range = routing_range.Range(range_min=max(single_range.min, feedrangeEPK.min),
                                                    range_max=min(single_range.max, feedrangeEPK.max),
                                                    isMinInclusive=True, isMaxInclusive=False)
                if single_range.min == EPK_sub_range.min and EPK_sub_range.max == single_range.max:
                    # The Epk Sub Range spans exactly one physical partition
                    # In this case we can route to the physical pk range id
                    req_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_range["id"]
                else:
                    # The Epk Sub Range spans less than a single physical partition
                    # In this case we route to the physical partition and
                    # pass the epk sub range to the headers to filter within partition
                    req_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_range["id"]
                    req_headers[http_constants.HttpHeaders.StartEpkString] = EPK_sub_range.min
                    req_headers[http_constants.HttpHeaders.EndEpkString] = EPK_sub_range.max
                req_headers[http_constants.HttpHeaders.ReadFeedKeyType] = "EffectivePartitionKeyRange"
                partial_result, self.last_response_headers = await self.__Post(
                    path,
                    request_params,
                    query,
                    req_headers,
                    **kwargs
                )
                if results:
                    # add up all the query results from all over lapping ranges
                    results["Documents"].extend(partial_result["Documents"])
                else:
                    results = partial_result
                if response_hook:
                    response_hook(self.last_response_headers, partial_result)
            # if the prefix partition query has results lets return it
            if results:
                return __GetBodiesFromQueryResult(results)

        result, self.last_response_headers = await self.__Post(path, request_params, query, req_headers, **kwargs)
        if self.last_response_headers.get(http_constants.HttpHeaders.IndexUtilization) is not None:
            INDEX_METRICS_HEADER = http_constants.HttpHeaders.IndexUtilization
            index_metrics_raw = self.last_response_headers[INDEX_METRICS_HEADER]
            self.last_response_headers[INDEX_METRICS_HEADER] = _utils.get_index_metrics_info(index_metrics_raw)
        if response_hook:
            response_hook(self.last_response_headers, result)

        return __GetBodiesFromQueryResult(result)

    def __CheckAndUnifyQueryFormat(
        self,
        query_body: Union[str, Dict[str, Any]]
    ) -> Union[str, Dict[str, Any]]:
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
                self._query_compatibility_mode in (CosmosClientConnection._QueryCompatibilityMode.Default,
                                                   CosmosClientConnection._QueryCompatibilityMode.Query)):
            if not isinstance(query_body, dict) and not isinstance(query_body, str):
                raise TypeError("query body must be a dict or string.")
            if isinstance(query_body, dict) and not query_body.get("query"):
                raise ValueError('query body must have valid query text with key "query".')
            if isinstance(query_body, str):
                return {"query": query_body}
        elif (
                self._query_compatibility_mode == CosmosClientConnection._QueryCompatibilityMode.SqlQuery
                and not isinstance(query_body, str)
        ):
            raise TypeError("query body must be a string.")
        else:
            raise SystemError("Unexpected query compatibility mode.")
        return query_body

    def _UpdateSessionIfRequired(
        self,
        request_headers: Mapping[str, Any],
        response_result: Optional[Mapping[str, Any]],
        response_headers: Optional[Mapping[str, Any]]
    ) -> None:
        """
        Updates session if necessary.

        :param dict request_headers: The request headers.
        :param dict response_result: The response result.
        :param dict response_headers: The response headers.
        """

        # if this request was made with consistency level as session, then update the session
        if response_result is None or response_headers is None:
            return

        is_session_consistency = False
        if http_constants.HttpHeaders.ConsistencyLevel in request_headers:
            if documents.ConsistencyLevel.Session == request_headers[http_constants.HttpHeaders.ConsistencyLevel]:
                is_session_consistency = True

        if is_session_consistency and self.session:
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

        base._validate_resource(document)
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

    def _GetUserIdWithPathForPermission(self, permission, user_link):
        base._validate_resource(permission)
        path = base.GetPathFromLink(user_link, "permissions")
        user_id = base.GetResourceIdOrFullNameFromLink(user_link)
        return path, user_id

    def RegisterPartitionResolver(
        self,
        database_link: str,
        partition_resolver: RangePartitionResolver
    ) -> None:
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

    def GetPartitionResolver(self, database_link: str) -> Optional[RangePartitionResolver]:
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
            # If the user has passed in the partitionKey in options use that else extract it from the document
            if "partitionKey" not in options:
                partitionKeyValue = self._ExtractPartitionKey(partitionKeyDefinition, document)
                options["partitionKey"] = partitionKeyValue

        return options

    # Extracts the partition key from the document using the partitionKey definition
    def _ExtractPartitionKey(self, partitionKeyDefinition, document):
        if partitionKeyDefinition["kind"] == "MultiHash":
            ret = []
            for partition_key_level in partitionKeyDefinition.get("paths"):
                # Parses the paths into a list of token each representing a property
                partition_key_parts = base.ParsePaths([partition_key_level])
                # Check if the partitionKey is system generated or not
                is_system_key = partitionKeyDefinition["systemKey"] if "systemKey" in partitionKeyDefinition else False

                # Navigates the document to retrieve the partitionKey specified in the paths
                val = self._retrieve_partition_key(partition_key_parts, document, is_system_key)
                if isinstance(val, _Undefined):
                    break
                ret.append(val)
            return ret

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
                return _return_undefined_or_empty_partition_key(is_system_key)

            partitionKey = partitionKey.get(part)
            matchCount += 1
            # Once we reach the "leaf" value(not a dict), we break from loop
            if not isinstance(partitionKey, dict):
                break

        # Match the count of hops we did to get the partitionKey with the length of
        # partition key parts and validate that it's not a dict at that level
        if (matchCount != expected_matchCount) or isinstance(partitionKey, dict):
            return _return_undefined_or_empty_partition_key(is_system_key)

        return partitionKey

    def refresh_routing_map_provider(self) -> None:
        # re-initializes the routing map provider, effectively refreshing the current partition key range cache
        self._routing_map_provider = SmartRoutingMapProvider(self)

    async def _GetQueryPlanThroughGateway(self, query: str, resource_link: str, **kwargs) -> List[Dict[str, Any]]:
        supported_query_features = (documents._QueryFeature.Aggregate + "," +
                                    documents._QueryFeature.CompositeAggregate + "," +
                                    documents._QueryFeature.Distinct + "," +
                                    documents._QueryFeature.MultipleOrderBy + "," +
                                    documents._QueryFeature.OffsetAndLimit + "," +
                                    documents._QueryFeature.OrderBy + "," +
                                    documents._QueryFeature.Top + "," +
                                    documents._QueryFeature.NonStreamingOrderBy)
        if os.environ.get('AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY', False):
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

        return await self.__QueryFeed(
            path,
            "docs",
            resource_id,
            lambda r: cast(List[Dict[str, Any]], r),
            None,
            query,
            options,
            is_query_plan=True,
            **kwargs
        )

    async def DeleteAllItemsByPartitionKey(
        self,
        collection_link: str,
        options: Optional[Mapping[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Exposes an API to delete all items with a single partition key without the user having
         to explicitly call delete on each record in the partition key.

        :param str collection_link:
            The link to the document collection.
        :param dict options:
            The request options for the request.

        :return:
            None
        :rtype:
            None

        """
        response_hook = kwargs.pop("response_hook", None)
        if options is None:
            options = {}

        path = base.GetPathFromLink(collection_link)
        # Specified url to perform background operation to delete all items by partition key
        path = '{}{}/{}'.format(path, "operations", "partitionkeydelete")
        collection_id = base.GetResourceIdOrFullNameFromLink(collection_link)
        initial_headers = dict(self.default_headers)
        headers = base.GetHeaders(self, initial_headers, "post", path, collection_id, "partitionkey", options)
        request_params = _request_object.RequestObject("partitionkey", documents._OperationType.Delete)
        _, last_response_headers = await self.__Post(path=path, request_params=request_params,
                                                        req_headers=headers, body=None, **kwargs)
        self.last_response_headers = last_response_headers
        if response_hook:
            response_hook(last_response_headers, None)
