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

from typing import Any, Dict, Optional, Union, cast
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import TokenCredential

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace

from ..cosmos_client import _parse_connection_str, _build_auth
from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options as _build_options, _set_throughput_options
from ..offer import ThroughputProperties
from ._retry_utility_async import _ConnectionRetryPolicy
from ._database import DatabaseProxy
from ..documents import ConnectionPolicy, DatabaseAccount
from ..exceptions import CosmosResourceNotFoundError

__all__ = ("CosmosClient",)


def _build_connection_policy(kwargs: Dict[str, Any]) -> ConnectionPolicy:
    # pylint: disable=protected-access
    policy = kwargs.pop('connection_policy', None) or ConnectionPolicy()

    # Connection config
    policy.RequestTimeout = kwargs.pop('request_timeout', None) or \
                            kwargs.pop('connection_timeout', None) or \
                            policy.RequestTimeout
    policy.ConnectionMode = kwargs.pop('connection_mode', None) or policy.ConnectionMode
    policy.ProxyConfiguration = kwargs.pop('proxy_config', None) or policy.ProxyConfiguration
    policy.EnableEndpointDiscovery = kwargs.pop('enable_endpoint_discovery', None) or policy.EnableEndpointDiscovery
    policy.PreferredLocations = kwargs.pop('preferred_locations', None) or policy.PreferredLocations
    policy.UseMultipleWriteLocations = kwargs.pop('multiple_write_locations', None) or \
                                       policy.UseMultipleWriteLocations

    # SSL config
    verify = kwargs.pop('connection_verify', None)
    policy.DisableSSLVerification = not bool(verify if verify is not None else True)
    ssl = kwargs.pop('ssl_config', None) or policy.SSLConfiguration
    if ssl:
        ssl.SSLCertFile = kwargs.pop('connection_cert', None) or ssl.SSLCertFile
        ssl.SSLCaCerts = verify or ssl.SSLCaCerts
        policy.SSLConfiguration = ssl

    # Retry config
    retry_options = policy.RetryOptions
    total_retries = kwargs.pop('retry_total', None)
    retry_options._max_retry_attempt_count = total_retries or retry_options._max_retry_attempt_count
    retry_options._fixed_retry_interval_in_milliseconds = kwargs.pop('retry_fixed_interval', None) or \
        retry_options._fixed_retry_interval_in_milliseconds
    max_backoff = kwargs.pop('retry_backoff_max', None)
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
            retry_on_status_codes=kwargs.pop('retry_on_status_codes', []),
            retry_backoff_factor=kwargs.pop('retry_backoff_factor', 0.8),
        )
    policy.ConnectionRetryConfiguration = connection_retry

    return policy


class CosmosClient(object):  # pylint: disable=client-accepts-api-version-keyword
    """A client-side logical representation of an Azure Cosmos DB account.

    Use this client to configure and execute requests to the Azure Cosmos DB service.

    :param str url: The URL of the Cosmos DB account.
    :param credential: Can be the account key, or a dictionary of resource tokens.
    :type credential: Union[str, Dict[str, str], ~azure.core.credentials_async.AsyncTokenCredential]
    :keyword str consistency_level: Consistency level to use for the session. Default value is None (account-level).
        More on consistency levels and possible values: https://aka.ms/cosmos-consistency-levels

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
            credential: Union[str, Dict[str, str], TokenCredential],
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

    async def __aenter__(self):
        await self.client_connection.pipeline_client.__aenter__()
        await self.client_connection._setup()
        return self

    async def __aexit__(self, *args):
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

    @staticmethod
    def _get_database_link(database_or_id: Union[DatabaseProxy, str, Dict[str, str]]) -> str:
        if isinstance(database_or_id, str):
            return "dbs/{}".format(database_or_id)
        try:
            return cast("DatabaseProxy", database_or_id).database_link
        except AttributeError:
            pass
        database_id = cast("Dict[str, str]", database_or_id)["id"]
        return "dbs/{}".format(database_id)

    @distributed_trace_async
    async def create_database(  # pylint: disable=redefined-builtin
            self,
            id: str,
            **kwargs: Any
    ) -> DatabaseProxy:
        """
        Create a new database with the given ID (name).

        :param str id: ID (name) of the database to create.
        :keyword int offer_throughput: The provisioned throughput for this offer.
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

        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        offer_throughput = kwargs.pop('offer_throughput', None)
        _set_throughput_options(offer=offer_throughput, options=request_options)

        result = await self.client_connection.CreateDatabase(database=dict(id=id), options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return DatabaseProxy(self.client_connection, id=result["id"], properties=result)

    @distributed_trace_async
    async def create_database_if_not_exists(  # pylint: disable=redefined-builtin
            self,
            id: str,
            **kwargs: Any
    ) -> DatabaseProxy:
        """
        Create the database if it does not exist already.

        If the database already exists, the existing settings are returned.

        ..note::
            This function does not check or update existing database settings or
            offer throughput if they differ from what is passed in.

        :param str id: ID (name) of the database to read or create.
        :keyword int offer_throughput: The provisioned throughput for this offer.
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
        try:
            database_proxy = self.get_database_client(id)
            await database_proxy.read(**kwargs)
            return database_proxy
        except CosmosResourceNotFoundError:
            return await self.create_database(
                id,
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
        try:
            id_value = database.id
        except AttributeError:
            try:
                id_value = database['id']
            except TypeError:
                id_value = database

        return DatabaseProxy(self.client_connection, id_value)

    @distributed_trace
    def list_databases(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List the databases in a Cosmos DB SQL database account.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str]], None]
        :returns: An AsyncItemPaged of database properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, str]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadDatabases(options=feed_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace
    def query_databases(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Query the databases in a Cosmos DB SQL database account.

        :keyword Union[str, Dict[str, Any]] query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str]], None]
        :returns: An AsyncItemPaged of database properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, str]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        parameters = kwargs.pop('parameters', None)
        query = kwargs.pop('query', None)
        result = self.client_connection.QueryDatabases(
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace_async
    async def delete_database(
            self,
            database: Union[str, DatabaseProxy, Dict[str, Any]],
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
        :paramtype response_hook: Callable[[Dict[str, str]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the database couldn't be deleted.
        :rtype: None
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        database_link = self._get_database_link(database)
        await self.client_connection.DeleteDatabase(database_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)

    @distributed_trace_async
    async def _get_database_account(self, **kwargs: Any) -> DatabaseAccount:
        """Retrieve the database account information.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str]], None]
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        response_hook = kwargs.pop('response_hook', None)
        result = await self.client_connection.GetDatabaseAccount(**kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result
