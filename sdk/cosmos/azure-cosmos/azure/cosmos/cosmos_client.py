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

"""Create, read, and delete databases in the Azure Cosmos DB SQL API service.
"""

import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Iterable, Mapping, Optional, Union, cast, Callable, overload, Literal, TYPE_CHECKING

from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from azure.core.pipeline.policies import RetryMode
from azure.core.tracing.decorator import distributed_trace

from ._base import build_options, _set_throughput_options
from ._constants import _Constants as Constants
from ._cosmos_client_connection import CosmosClientConnection, CredentialDict
from ._cosmos_responses import CosmosDict
from ._retry_utility import ConnectionRetryPolicy
from .database import DatabaseProxy, _get_database_link
from .documents import ConnectionPolicy, DatabaseAccount
from .exceptions import CosmosResourceNotFoundError
from azure.cosmos._rust import CosmosClient as RustCosmosClient

if TYPE_CHECKING:
    from . import ThroughputProperties

__all__ = ("CosmosClient",)


# pylint: disable=docstring-keyword-should-match-keyword-only

CredentialType = Union[
    TokenCredential, CredentialDict, str, Mapping[str, Any], Iterable[Mapping[str, Any]]
]


def _parse_connection_str(conn_str: str, credential: Optional[Any]) -> dict[str, str]:
    conn_str = conn_str.rstrip(";")
    conn_settings = dict([s.split("=", 1) for s in conn_str.split(";")])
    if 'AccountEndpoint' not in conn_settings:
        raise ValueError("Connection string missing setting 'AccountEndpoint'.")
    if not credential and 'AccountKey' not in conn_settings:
        raise ValueError("Connection string missing setting 'AccountKey'.")
    return conn_settings


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
    elif isinstance(credential, TokenCredential):
        auth['clientSecretCredential'] = credential
    else:
        raise TypeError(
            "Unrecognized credential type. Please supply the master key as a string "
            "or a dictionary, or resource tokens, or a list of permissions, or any instance of a class implementing"
            " TokenCredential (see azure.identity module for specific implementations such as ClientSecretCredential).")
    return auth


def _build_connection_policy(kwargs: dict[str, Any]) -> ConnectionPolicy:
    # pylint: disable=protected-access
    policy = kwargs.pop('connection_policy', ConnectionPolicy())

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
    # TODO: Consider storing callback method instead, such as 'Supplier' in JAVA SDK
    excluded_locations = kwargs.pop('excluded_locations', policy.ExcludedLocations)
    if excluded_locations:
        policy.ExcludedLocations = excluded_locations
    policy.UseMultipleWriteLocations = kwargs.pop('multiple_write_locations', policy.UseMultipleWriteLocations)

    # SSL config
    verify = kwargs.pop('connection_verify', None)
    policy.DisableSSLVerification = not bool(verify if verify is not None else True)
    ssl = kwargs.pop('ssl_config', policy.SSLConfiguration)
    if ssl:
        ssl.SSLCertFile = kwargs.pop('connection_cert', ssl.SSLCertFile)
        ssl.SSLCaCerts = verify or ssl.SSLCaCerts
        policy.SSLConfiguration = ssl

    # Retry config
    retry_options = kwargs.pop('retry_options', None)
    if retry_options is not None:
        warnings.warn(
            "'retry_options' has been deprecated and will be removed from the SDK in a future release.",
            DeprecationWarning
        )
    retry_options = policy.RetryOptions
    total_retries = kwargs.pop('retry_total', None)
    total_throttle_retries = kwargs.pop('retry_throttle_total', None)
    retry_options._max_retry_attempt_count = \
        total_throttle_retries or total_retries or retry_options._max_retry_attempt_count
    retry_options._fixed_retry_interval_in_milliseconds = kwargs.pop('retry_fixed_interval', None) or \
        retry_options._fixed_retry_interval_in_milliseconds
    max_backoff = kwargs.pop('retry_backoff_max', None)
    max_throttle_backoff = kwargs.pop('retry_throttle_backoff_max', None)
    retry_options._max_wait_time_in_seconds = \
        max_throttle_backoff or max_backoff or retry_options._max_wait_time_in_seconds
    policy.RetryOptions = retry_options
    connection_retry = kwargs.pop('connection_retry_policy', None)
    if connection_retry is not None:
        warnings.warn(
            "'connection_retry_policy' has been deprecated and will be removed from the SDK in a future release.",
            DeprecationWarning
        )
    if not connection_retry:
        connection_retry = ConnectionRetryPolicy(
            retry_total=total_retries,
            retry_connect=kwargs.pop('retry_connect', None),
            retry_read=kwargs.pop('retry_read', None),
            retry_status=kwargs.pop('retry_status', None),
            retry_backoff_max=max_backoff or retry_options._max_wait_time_in_seconds,
            retry_mode=kwargs.pop('retry_mode', RetryMode.Fixed),
            retry_on_status_codes=kwargs.pop('retry_on_status_codes', []),
            retry_backoff_factor=kwargs.pop('retry_backoff_factor', 1),
        )
    policy.ConnectionRetryConfiguration = connection_retry
    policy.ResponsePayloadOnWriteDisabled = kwargs.pop('no_response_on_write', False)
    policy.RetryNonIdempotentWrites = kwargs.pop(Constants.Kwargs.RETRY_WRITE, False)
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
    :type credential: Union[str, dict[str, str], ~azure.core.credentials.TokenCredential]
    :param str consistency_level: Consistency level to use for the session. The default value is None (Account level).
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
    :keyword int retry_write: Indicates how many times the SDK should automatically retry write operations for items,
        even if the operation is not guaranteed to be idempotent. This should only be enabled if the application can
        tolerate such risks or has logic to safely detect and handle duplicate operations.
    :keyword bool enable_endpoint_discovery: Enable endpoint discovery for
        geo-replicated database accounts. (Default: True)
    :keyword list[str] preferred_locations: The preferred locations for geo-replicated database accounts.
    :keyword list[str] excluded_locations: The excluded locations to be skipped from preferred locations. The locations
        in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
        If all preferred locations were excluded, primary/hub location will be used.
    :keyword bool enable_diagnostics_logging: Enable the CosmosHttpLogging policy.
        Must be used along with a logger to work.
    :keyword ~logging.Logger logger: Logger to be used for collecting request diagnostics. Can be passed in at client
        level (to log all requests) or at a single request level. Requests will be logged at INFO level.
    :keyword bool no_response_on_write: Indicates whether service should be instructed to skip sending 
        response payloads on write operations for items.
    :keyword int throughput_bucket: The desired throughput bucket for the client
    :keyword str user_agent_suffix: Allows user agent suffix to be specified when creating client
    :keyword dict[str, Any] availability_strategy_config:
        The threshold-based availability strategy to use for this request.
    :keyword ~concurrent.futures.thread.ThreadPoolExecutor availability_strategy_executor:
        Optional ThreadPoolExecutor for handling concurrent operations.

    .. admonition:: Example:

        .. literalinclude:: ../samples/examples.py
            :start-after: [START create_client]
            :end-before: [END create_client]
            :language: python
            :dedent: 0
            :caption: Create a new instance of the Cosmos DB client:
    """

    def __init__(
        self,
        url: str,
        credential: Union[TokenCredential, str, dict[str, Any]],
        consistency_level: Optional[str] = None,
        availability_strategy_config: Optional[dict[str, Any]] = None,
        availability_strategy_executor: Optional[ThreadPoolExecutor] = None,
        **kwargs
    ) -> None:
        """Instantiate a new CosmosClient.
        """
        # KEEP: Build auth and connection policy (needed for fallback methods)
        auth = _build_auth(credential)
        connection_policy = _build_connection_policy(kwargs)

        # KEEP: Create CosmosClientConnection (needed for methods not yet in Rust)
        self.client_connection = CosmosClientConnection(
            url_connection=url,
            auth=auth,
            consistency_level=consistency_level,
            connection_policy=connection_policy,
            availability_strategy_config=availability_strategy_config,
            availability_strategy_executor=availability_strategy_executor,
            **kwargs
        )
        # Create Rust client
        self._rust_client = RustCosmosClient(url, credential, **kwargs)
        self._url = url  # Keep for backward compatibility

    def __repr__(self) -> str:
        return "<CosmosClient [{}]>".format(self.client_connection.url_connection)[:1024]

    def __enter__(self):
        self.client_connection.pipeline_client.__enter__()
        return self

    def __exit__(self, *args):
        return self.client_connection.pipeline_client.__exit__(*args)

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        credential: Optional[Union[TokenCredential, str, dict[str, Any]]] = None,
        consistency_level: Optional[str] = None,
        **kwargs
    ) -> 'CosmosClient':
        """Create a CosmosClient instance from a connection string.

        This can be retrieved from the Azure portal.For full list of optional
        keyword arguments, see the CosmosClient constructor.

        :param str conn_str: The connection string.
        :param credential: Alternative credentials to use instead of the key
            provided in the connection string.
        :type credential: Union[str, dict[str, str]]
        :param str consistency_level:
            Consistency level to use for the session. The default value is None (Account level).
        :returns: A CosmosClient instance representing the new client.
        :rtype: ~azure.cosmos.CosmosClient
        """
        settings = _parse_connection_str(conn_str, credential)
        return cls(
            url=settings['AccountEndpoint'],
            credential=credential or settings['AccountKey'],
            consistency_level=consistency_level,
            **kwargs
        )

    @overload
    def create_database(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        *,
        offer_throughput: Optional[Union[int, 'ThroughputProperties']] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        throughput_bucket: Optional[int] = None,
        return_properties: Literal[False] = False,
        **kwargs: Any
    ) -> DatabaseProxy:
        """Create a new database with the given ID (name).

        :param str id: ID (name) of the database to create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A `DatabaseProxy` instance representing the database.
        :rtype: ~azure.cosmos.DatabaseProxy
        :raises ~azure.cosmos.exceptions.CosmosResourceExistsError: Database with the given ID already exists.

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_database]
                :end-before: [END create_database]
                :language: python
                :dedent: 0
                :caption: Create a database in the Cosmos DB account:
        """
        ...

    @overload
    def create_database(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        *,
        offer_throughput: Optional[Union[int, 'ThroughputProperties']] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        throughput_bucket: Optional[int] = None,
        return_properties: Literal[True],
        **kwargs: Any
    ) -> tuple[DatabaseProxy, CosmosDict]:
        """Create a new database with the given ID (name).

        :param str id: ID (name) of the database to create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A tuple of `DatabaseProxy` and CosmosDict with the database properties.
        :rtype: tuple [~azure.cosmos.DatabaseProxy, ~azure.cosmos.CosmosDict]
        :raises ~azure.cosmos.exceptions.CosmosResourceExistsError: Database with the given ID already exists.

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_database]
                :end-before: [END create_database]
                :language: python
                :dedent: 0
                :caption: Create a database in the Cosmos DB account:
        """
        ...

    @distributed_trace
    def create_database(  # pylint:disable=docstring-missing-param, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[DatabaseProxy, tuple[DatabaseProxy, CosmosDict]]:
        """Create a new database with the given ID (name).

        :param Any args: args
        :param str id: ID (name) of the database to create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A `DatabaseProxy` instance representing the database or a tuple of `DatabaseProxy`
            and CosmosDict with the database properties.
        :rtype: ~azure.cosmos.DatabaseProxy or tuple [~azure.cosmos.DatabaseProxy, ~azure.cosmos.CosmosDict]
        :raises ~azure.cosmos.exceptions.CosmosResourceExistsError: Database with the given ID already exists.

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_database]
                :end-before: [END create_database]
                :language: python
                :dedent: 0
                :caption: Create a database in the Cosmos DB account:
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)

        id = args[0] if args else kwargs.pop("id")
        # Keep positional arguments for populate_query_metrics and offer_throughput for backwards compatibility
        populate_query_metrics = args[1] if len(args) > 1 else kwargs.pop("populate_query_metrics", None)
        offer_throughput = args[2] if len(args) > 2 else kwargs.pop("offer_throughput", None)
        if len(args) > 3:
            raise TypeError(f"Unexpected positional arguments: {args[3:]}")

        return_properties = kwargs.pop("return_properties", False)

        if populate_query_metrics is not None:
            warnings.warn(
                "The 'populate_query_metrics' flag does not apply to this method"
                " and will be removed in the future",
                UserWarning,
            )

        request_options = build_options(kwargs)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"
        response_hook = kwargs.pop("response_hook", None)

        if use_rust:
            print("[CosmosClient.create_database] Using RUST SDK")
            # RUST PATH: Call Rust SDK - no fallback, fail if Rust fails
            # Rust now returns (DatabaseClient, headers_dict) tuple
            rust_db, headers_dict = self._rust_client.create_database(id)

            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))

            # Create DatabaseProxy with Rust client
            db_proxy = DatabaseProxy(
                client_connection=self.client_connection,
                id=id,
                rust_database=rust_db
            )

            if response_hook:
                response_hook(response_headers)

            if not return_properties:
                return db_proxy

            # For return_properties=True, get properties
            # Rust read() now returns (properties, headers) tuple
            properties, props_headers = rust_db.read()
            return db_proxy, CosmosDict(dict(properties), response_headers=CaseInsensitiveDict(dict(props_headers)))

        # PYTHON PATH: Use existing Python implementation
        print("[CosmosClient.create_database] Using PURE PYTHON")
        result = self.client_connection.CreateDatabase(database={"id": id}, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)

        db_proxy = DatabaseProxy(
            client_connection=self.client_connection,
            id=id,
            properties=result
        )

        if not return_properties:
            return db_proxy
        return db_proxy, CosmosDict(result, response_headers=self.client_connection.last_response_headers)



    @overload
    def create_database_if_not_exists(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        *,
        offer_throughput: Optional[Union[int, 'ThroughputProperties']] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        throughput_bucket: Optional[int] = None,
        return_properties: Literal[False] = False,
        **kwargs: Any
    ) -> DatabaseProxy:
        """
        Create the database if it does not exist already.
        If the database already exists, the existing settings are returned.

        ..note::
            This function does not check or update existing database settings or
            offer throughput if they differ from what is passed in.

        :param str id: ID (name) of the database to read or create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A `DatabaseProxy` instance representing the database.
        :rtype: ~azure.cosmos.DatabaseProxy
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The database read or creation failed.
        """
        ...

    @overload
    def create_database_if_not_exists(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            *,
            offer_throughput: Optional[Union[int, 'ThroughputProperties']] = None,
            initial_headers: Optional[dict[str, str]] = None,
            response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
            throughput_bucket: Optional[int] = None,
            return_properties: Literal[True],
            **kwargs: Any
    ) -> tuple[DatabaseProxy, CosmosDict]:
        """
        Create the database if it does not exist already.
        If the database already exists, the existing settings are returned.

        ..note::
            This function does not check or update existing database settings or
            offer throughput if they differ from what is passed in.

        :param str id: ID (name) of the database to read or create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A tuple of `DatabaseProxy` and CosmosDict with the database properties.
        :rtype: tuple [~azure.cosmos.DatabaseProxy, ~azure.cosmos.CosmosDict]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The database read or creation failed.
        """
        ...

    @distributed_trace
    def create_database_if_not_exists(  # pylint:disable=docstring-missing-param, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[DatabaseProxy, tuple[DatabaseProxy, CosmosDict]]:
        """
        Create the database if it does not exist already.
        If the database already exists, the existing settings are returned.

        ..note::
            This function does not check or update existing database settings or
            offer throughput if they differ from what is passed in.

        :param Any args: args
        :param str id: ID (name) of the database to read or create.
        :keyword Union[int, ~azure.cosmos.ThroughputProperties] offer_throughput: The provisioned throughput
            for this database.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable[[Mapping[str, Any]], None] response_hook: A callable invoked with the response metadata.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword bool return_properties: Specifies whether to return either a DatabaseProxy
            or a Tuple containing a DatabaseProxy and the associated database properties.
        :returns: A `DatabaseProxy` instance representing the database or a tuple of `DatabaseProxy`
            and CosmosDict with the database properties.
        :rtype: ~azure.cosmos.DatabaseProxy or tuple [~azure.cosmos.DatabaseProxy, ~azure.cosmos.CosmosDict]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The database read or creation failed.
        """

        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)

        id = args[0] if args else kwargs.pop("id")
        # Keep positional arguments for populate_query_metrics and offer_throughput for backwards compatibility
        populate_query_metrics = args[1] if len(args) > 1 else kwargs.pop("populate_query_metrics", None)
        offer_throughput = args[2] if len(args) > 2 else kwargs.pop("offer_throughput", None)
        if len(args) > 3:
            raise TypeError(f"Unexpected positional arguments: {args[3:]}")

        return_properties = kwargs.pop("return_properties", False)
        try:
            database_proxy = self.get_database_client(id)
            result = database_proxy.read(
                populate_query_metrics=populate_query_metrics,
                **kwargs
            )
            if not return_properties:
                return database_proxy
            return database_proxy, result
        except CosmosResourceNotFoundError:
            return self.create_database(
                id,
                offer_throughput=offer_throughput,
                return_properties=return_properties,
                **kwargs
            )

    def get_database_client(self, database: Union[str, DatabaseProxy, Mapping[str, Any]]) -> DatabaseProxy:
        """Retrieve an existing database with the ID (name) `id`.

        :param database: The ID (name), dict representing the properties or
            `DatabaseProxy` instance of the database to read.
        :type database: str or dict(str, str) or ~azure.cosmos.DatabaseProxy
        :returns: A `DatabaseProxy` instance representing the retrieved database.
        :rtype: ~azure.cosmos.DatabaseProxy
        """
        """"""
        if isinstance(database, DatabaseProxy):
            id_value = database.id
        elif isinstance(database, str):
            id_value = database
        else:
            id_value = database["id"]

        #Get Rust database client
        rust_db = self._rust_client.get_database_client(id_value)

        # Pass Rust client to DatabaseProxy
        return DatabaseProxy(
            client_connection=self.client_connection,  # Keep for fallback methods
            id=id_value,
            rust_database=rust_db  # Pass Rust client
        )



    @distributed_trace
    def list_databases(  # pylint:disable=docstring-missing-param
        self,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        throughput_bucket: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List the databases in a Cosmos DB SQL database account.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str]], None]
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :returns: An Iterable of database properties (dicts).
        :rtype: Iterable[dict[str, str]]
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        # NOTE: list_databases Rust integration is disabled for now
        # The Rust facade's list_databases returns malformed data (debug format instead of proper dict)
        # This will be fixed later when proper serialization is implemented

        result = self.client_connection.ReadDatabases(options=feed_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace
    def query_databases(  # pylint:disable=docstring-missing-param
        self,
        query: Optional[str] = None,
        parameters: Optional[list[dict[str, Any]]] = None,
        enable_cross_partition_query: Optional[bool] = None,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        throughput_bucket: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Query the databases in a Cosmos DB SQL database account.

        :param str query: The Azure Cosmos DB SQL query to execute. If not specified, the method will get all databases.
        :param list[dict[str, Any]] parameters: Optional array of parameters to the query.
            Ignored if no query is provided.
        :param bool enable_cross_partition_query: Allow scan on the queries which couldn't be
            served as indexing was opted out on the requested paths.
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str]], None]
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :returns: An Iterable of database properties (dicts).
        :rtype: Iterable[dict[str, str]]
        """
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)

        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        if throughput_bucket is not None:
            kwargs['throughput_bucket'] = throughput_bucket
        feed_options = build_options(kwargs)
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        if query:
            result = self.client_connection.QueryDatabases(
                query=query if parameters is None else {'query': query, 'parameters': parameters},
                options=feed_options,
                **kwargs
            )
        else:
            result = self.client_connection.ReadDatabases(options=feed_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result

    @distributed_trace
    def delete_database(  # pylint:disable=docstring-missing-param
            self,
            database: Union[str, DatabaseProxy, Mapping[str, Any]],
            populate_query_metrics: Optional[bool] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
            throughput_bucket: Optional[int] = None,
            **kwargs: Any
    ) -> None:
        """Delete the database with the given ID (name).

        :param database: The ID (name), dict representing the properties or :class:`DatabaseProxy`
            instance of the database to delete.
        :type database: Union[str, dict[str, str], ~azure.cosmos.DatabaseProxy]
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str]], None]
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the database couldn't be deleted.
        :rtype: None
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                UserWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
        if throughput_bucket is not None:
            kwargs['throughput_bucket'] = throughput_bucket
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        request_options = build_options(kwargs)

        # Extract the database ID
        if isinstance(database, DatabaseProxy):
            database_id = database.id
        elif isinstance(database, str):
            database_id = database
        else:
            database_id = database["id"]

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"
        if use_rust:
            print("[CosmosClient.delete_database] Using RUST SDK")
            # RUST PATH: Call Rust SDK - no fallback, fail if Rust fails
            headers_dict = self._rust_client.delete_database(database_id)
            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))
            if response_hook:
                response_hook(response_headers)
            return

        # PYTHON PATH: Use existing Python implementation
        print("[CosmosClient.delete_database] Using PURE PYTHON")
        database_link = _get_database_link(database)
        self.client_connection.DeleteDatabase(database_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)


    @distributed_trace
    def get_database_account(
            self,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
            **kwargs) -> DatabaseAccount:
        """Retrieve the database account information.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        result = self.client_connection.GetDatabaseAccount(**kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers)
        return result
