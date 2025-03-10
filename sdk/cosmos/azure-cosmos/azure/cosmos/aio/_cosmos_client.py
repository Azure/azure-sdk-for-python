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

"""Create, read, and delete databases in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Dict, List, Optional, Union, cast, Mapping, Iterable, Callable
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core import MatchConditions
from azure.core.pipeline.policies import RetryMode

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.cosmos.offer import ThroughputProperties

from ..cosmos_client import _parse_connection_str
from ._cosmos_client_connection_async import CosmosClientConnection, CredentialDict
from .._base import build_options as _build_options, _set_throughput_options
from ._retry_utility_async import _ConnectionRetryPolicy
from ._database import DatabaseProxy, _get_database_link
from ..documents import ConnectionPolicy, DatabaseAccount
from ..exceptions import CosmosResourceNotFoundError

# pylint: disable=docstring-keyword-should-match-keyword-only

__all__ = ("CosmosClient",)

CredentialType = Union[
    AsyncTokenCredential, CredentialDict, str, Mapping[str, Any], Iterable[Mapping[str, Any]]
]

def _build_auth(credential: CredentialType) -> CredentialDict:
    auth: CredentialDict = {}
    if isinstance(credential, str):
        auth['masterKey'] = credential
    elif isinstance(credential, Mapping):
        if any(k for k in credential.keys() if k in ['masterKey', 'resourceTokens', 'permissionFeed']):
            return cast(CredentialDict, credential)  # Backwards compatible
        auth['resourceTokens'] = credential
    elif isinstance(credential, Iterable):
        auth['permissionFeed'] = cast(Iterable[Mapping[str, Any]], credential)
    elif isinstance(credential, (TokenCredential, AsyncTokenCredential)):
        auth['clientSecretCredential'] = credential
    else:
        raise TypeError(
            "Unrecognized credential type. Please supply the master key as a string "
            "or a dictionary, or resource tokens, or a list of permissions, or any instance of a class implementing"
            " AsyncTokenCredential (see azure.identity module for specific implementations "
            "such as ClientSecretCredential).")
    return auth


def _build_connection_policy(kwargs: Dict[str, Any]) -> ConnectionPolicy:
    # pylint: disable=protected-access
    policy = kwargs.pop('connection_policy', None) or ConnectionPolicy()

    # Connection config
    # `request_timeout` is supported as a legacy parameter later replaced by `connection_timeout`
    if 'request_timeout' in kwargs:
        policy.RequestTimeout = kwargs.pop('request_timeout') / 1000.0
    else:
        policy.RequestTimeout = kwargs.pop('connection_timeout', policy.RequestTimeout)
    policy.ConnectionMode = kwargs.pop('connection_mode', policy.ConnectionMode)
    policy.ProxyConfiguration = kwargs.pop('proxy_config', policy.ProxyConfiguration)
    policy.EnableEndpointDiscovery = kwargs.pop('enable_endpoint_discovery', policy.EnableEndpointDiscovery)
    policy.PreferredLocations = kwargs.pop('preferred_locations', policy.PreferredLocations)
    policy.UseMultipleWriteLocations = kwargs.pop('multiple_write_locations', policy.UseMultipleWriteLocations)

    # SSL config
    verify = kwargs.pop('connection_verify', None)
    policy.DisableSSLVerification = not bool(verify if verify is not None else True)
    ssl = kwargs.pop('ssl_config', None) or policy.SSLConfiguration
    if ssl:
        ssl.SSLCertFile = kwargs.pop('connection_cert', ssl.SSLCertFile)
        ssl.SSLCaCerts = verify or ssl.SSLCaCerts
        policy.SSLConfiguration = ssl

    # Retry config
    retry_options = policy.RetryOptions
    total_retries = kwargs.pop('retry_total', None)
    retry_options._max_retry_attempt_count = total_retries or retry_options._max_retry_attempt_count
    retry_options._fixed_retry_interval_in_milliseconds = \
        kwargs.pop('retry_fixed_interval', retry_options._fixed_retry_interval_in_milliseconds)
    max_backoff = kwargs.pop('retry_backoff_max', policy.MaxBackoff)
    retry_options._max_wait_time_in_seconds = max_backoff or retry_options._max_wait_time_in_seconds
    policy.RetryOptions = retry_options
    connection_retry = policy.ConnectionRetryConfiguration
    if not connection_retry:
        connection_retry = _ConnectionRetryPolicy(
            retry_total=total_retries,
            retry_connect=kwargs.pop('retry_connect', None),
            retry_read=kwargs.pop('retry_read', None),
            retry_status=kwargs.pop('retry_status', None),
            retry_backoff_max=max_backoff,
            retry_mode=kwargs.pop('retry_mode', RetryMode.Fixed),
            retry_on_status_codes=kwargs.pop('retry_on_status_codes', []),
            retry_backoff_factor=kwargs.pop('retry_backoff_factor', 1),
        )
    policy.ConnectionRetryConfiguration = connection_retry
    policy.ResponsePayloadOnWriteDisabled = kwargs.pop('no_response_on_write', False)
    return policy


class CosmosClient:  # pylint: disable=client-accepts-api-version-keyword
    """A client-side logical representation of an Azure Cosmos DB account.

    Use this client to configure and execute requests to the Azure Cosmos DB service.

    It's recommended to maintain a single instance of CosmosClient per lifetime of the application which enables
        efficient connection management and performance.

    CosmosClient initialization is a heavy operation - don't use initialization CosmosClient instances as
        credentials or network connectivity validations.

    :param str url: The URL of the Cosmos DB account.
    :param credential: Can be the account key, or a dictionary of resource tokens.
    :type credential: Union[str, Dict[str, str], ~azure.core.credentials_async.AsyncTokenCredential]
    :keyword str consistency_level: Consistency level to use for the session. Default value is None (account-level).
        More on consistency levels and possible values: https://aka.ms/cosmos-consistency-levels
    :keyword int timeout: An absolute timeout in seconds, for the combined HTTP request and response processing.
    :keyword int connection_timeout: The HTTP request timeout in seconds.
    :keyword str connection_mode: The connection mode for the client - currently only supports 'Gateway'.
    :keyword proxy_config: Connection proxy configuration.
    :paramtype proxy_config: ~azure.cosmos.ProxyConfiguration
    :keyword ssl_config: Connection SSL configuration.
    :paramtype ssl_config: ~azure.cosmos.SSLConfiguration
    :keyword bool connection_verify: Whether to verify the connection, default value is True.
    :keyword str connection_cert: An alternative certificate to verify the connection.
    :keyword int retry_total: Maximum retry attempts.
    :keyword int retry_backoff_max: Maximum retry wait time in seconds.
    :keyword int retry_fixed_interval: Fixed retry interval in milliseconds.
    :keyword int retry_read: Maximum number of socket read retry attempts.
    :keyword int retry_connect: Maximum number of connection error retry attempts.
    :keyword int retry_status: Maximum number of retry attempts on error status codes.
    :keyword list[int] retry_on_status_codes: A list of specific status codes to retry on.
    :keyword float retry_backoff_factor: Factor to calculate wait time between retry attempts.
    :keyword bool enable_endpoint_discovery: Enable endpoint discovery for
        geo-replicated database accounts. (Default: True)
    :keyword list[str] preferred_locations: The preferred locations for geo-replicated database accounts.
    :keyword bool enable_diagnostics_logging: Enable the CosmosHttpLogging policy.
        Must be used along with a logger to work.
    :keyword ~logging.Logger logger: Logger to be used for collecting request diagnostics. Can be passed in at client
        level (to log all requests) or at a single request level. Requests will be logged at INFO level.
    :keyword bool no_response_on_write: Indicates whether service should be instructed to skip sending 
        response payloads for write operations on items by default unless specified differently per operation.

    .. admonition:: Example:

        .. literalinclude:: ../samples/examples_async.py
            :start-after: [START create_client]
            :end-before: [END create_client]
            :language: python
            :dedent: 0
            :caption: Create a new instance of the Cosmos DB client:
            :name: create_client
    """

    def __init__(
            self,
            url: str,
            credential: Union[str, Dict[str, str], AsyncTokenCredential],
            *,
            consistency_level: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        """Instantiate a new CosmosClient."""
        auth = _build_auth(credential)
        connection_policy = _build_connection_policy(kwargs)
        self.client_connection = CosmosClientConnection(
            url,
            auth=auth,
            consistency_level=consistency_level,
            connection_policy=connection_policy,
            **kwargs
        )

    def __repr__(self) -> str:
        return "<CosmosClient [{}]>".format(self.client_connection.url_connection)[:1024]

    async def __aenter__(self) -> "CosmosClient":
        await self.client_connection.pipeline_client.__aenter__()
        await self.client_connection._setup()
        return self

    async def __aexit__(self, *args) -> None:
        await self.client_connection._global_endpoint_manager.close() # pylint: disable=protected-access
        return await self.client_connection.pipeline_client.__aexit__(*args)

    async def close(self) -> None:
        """Close this instance of CosmosClient."""
        await self.__aexit__()

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        *,
        credential: Optional[Union[str, Dict[str, str]]] = None,
        consistency_level: Optional[str] = None,
        **kwargs: Any
    ) -> "CosmosClient":
        """Create a CosmosClient instance from a connection string.

        This can be retrieved from the Azure portal.For full list of optional
        keyword arguments, see the CosmosClient constructor.

        :param str conn_str: The connection string.
        :keyword credential: Alternative credentials to use instead of the key provided in the connection string.
        :paramtype credential: Union[str, Dict[str, str]]
        :keyword str consistency_level: Consistency level to use for the session. Default value is None (account-level).
            More on consistency levels and possible values: https://aka.ms/cosmos-consistency-levels
        :returns: a CosmosClient instance
        :rtype: ~azure.cosmos.aio.CosmosClient
        """
        settings = _parse_connection_str(conn_str, credential)
        return cls(
            url=settings['AccountEndpoint'],
            credential=settings['AccountKey'],
            consistency_level=consistency_level,
            **kwargs
        )

    @distributed_trace_async
    async def create_database(
        self,
        id: str,
        *,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> DatabaseProxy:
        """
        Create a new database with the given ID (name).

        :param str id: ID (name) of the database to create.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosResourceExistsError: Database with the given ID already exists.
        :returns: A DatabaseProxy instance representing the new database.
        :rtype: ~azure.cosmos.aio.DatabaseProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START create_database]
                :end-before: [END create_database]
                :language: python
                :dedent: 0
                :caption: Create a database in the Cosmos DB account:
                :name: create_database
        """
        if session_token is not None:
            kwargs["session_token"] = session_token
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        if etag is not None:
            kwargs["etag"] = etag
        if match_condition is not None:
            kwargs["match_condition"] = match_condition
        request_options = _build_options(kwargs)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)

        result = await self.client_connection.CreateDatabase(database={"id": id}, options=request_options, **kwargs)
        return DatabaseProxy(self.client_connection, id=result["id"], properties=result)

    @distributed_trace_async
    async def create_database_if_not_exists(  # pylint: disable=redefined-builtin
        self,
        id: str,
        *,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> DatabaseProxy:
        """
        Create the database if it does not exist already.

        If the database already exists, the existing settings are returned.

        ..note::
            This function does not check or update existing database settings or
            offer throughput if they differ from what is passed in.

        :param str id: ID (name) of the database to read or create.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The database read or creation failed.
        :returns: A DatabaseProxy instance representing the database.
        :rtype: ~azure.cosmos.DatabaseProxy
        """
        if session_token is not None:
            kwargs["session_token"] = session_token
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        if etag is not None:
            kwargs["etag"] = etag
        if match_condition is not None:
            kwargs["match_condition"] = match_condition
        try:
            database_proxy = self.get_database_client(id)
            await database_proxy.read(**kwargs)
            return database_proxy
        except CosmosResourceNotFoundError:
            return await self.create_database(
                id,
                offer_throughput=offer_throughput,
                **kwargs
            )

    def get_database_client(self, database: Union[str, DatabaseProxy, Dict[str, Any]]) -> DatabaseProxy:
        """Retrieve an existing database with the ID (name) `id`.

        :param database: The ID (name), dict representing the properties, or :class:`DatabaseProxy`
            instance of the database to get.
        :type database: Union[str, ~azure.cosmos.DatabaseProxy, Dict[str, Any]]
        :returns: A `DatabaseProxy` instance representing the retrieved database.
        :rtype: ~azure.cosmos.DatabaseProxy
        """
        if isinstance(database, str):
            id_value = database
        elif isinstance(database, DatabaseProxy):
            id_value = database.id
        else:
            id_value = str(database['id'])
        return DatabaseProxy(self.client_connection, id_value)

    @distributed_trace
    def list_databases(
        self,
        *,
        max_item_count: Optional[int] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List the databases in a Cosmos DB SQL database account.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: An AsyncItemPaged of database properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, str]]
        """
        if session_token is not None:
            kwargs["session_token"] = session_token
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadDatabases(options=feed_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace
    def query_databases(
        self,
        query: str,
        *,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Query the databases in a Cosmos DB SQL database account.

        :param Union[str, Dict[str, Any]] query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: An AsyncItemPaged of database properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, str]]
        """
        if session_token is not None:
            kwargs["session_token"] = session_token
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryDatabases(
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace_async
    async def delete_database(
        self,
        database: Union[str, DatabaseProxy, Dict[str, Any]],
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> None:
        """Delete the database with the given ID (name).

        :param database: The ID (name), dict representing the properties, or :class:`DatabaseProxy`
            instance of the database to delete.
        :type database: Union[str, ~azure.cosmos.DatabaseProxy, Dict[str, Any]]
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the database couldn't be deleted.
        :rtype: None
        """
        if session_token is not None:
            kwargs["session_token"] = session_token
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        if etag is not None:
            kwargs["etag"] = etag
        if match_condition is not None:
            kwargs["match_condition"] = match_condition
        request_options = _build_options(kwargs)

        database_link = _get_database_link(database)
        await self.client_connection.DeleteDatabase(database_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)

    @distributed_trace_async
    async def _get_database_account(
            self,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
            **kwargs: Any
    ) -> DatabaseAccount:
        """Retrieve the database account information.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        result = await self.client_connection.GetDatabaseAccount(**kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result
