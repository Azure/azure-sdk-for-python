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

"""Interact with databases in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Union, Optional, Mapping, Callable, overload, Literal

import warnings
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.cosmos.partition_key import PartitionKey

from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options, _set_throughput_options, _deserialize_throughput, _replace_throughput
from .container import ContainerProxy
from .offer import Offer, ThroughputProperties
from .http_constants import StatusCodes as _StatusCodes
from .exceptions import CosmosResourceNotFoundError
from .user import UserProxy
from .documents import IndexingMode
from ._cosmos_responses import CosmosDict

__all__ = ("DatabaseProxy",)


# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=docstring-keyword-should-match-keyword-only

def _get_database_link(database_or_id: Union[str, 'DatabaseProxy', Mapping[str, Any]]) -> str:
    if isinstance(database_or_id, str):
        return "dbs/{}".format(database_or_id)
    if isinstance(database_or_id, DatabaseProxy):
        return database_or_id.database_link
    database_id = database_or_id["id"]
    return "dbs/{}".format(database_id)


class DatabaseProxy(object):
    """An interface to interact with a specific database.

    This class should not be instantiated directly. Instead use the
    :func:`CosmosClient.get_database_client` method.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    A database can also have associated users, each of which is configured with
    a set of permissions for accessing certain containers, stored procedures,
    triggers, user-defined functions, or items.

    :ivar id: The ID (name) of the database.

    An Azure Cosmos DB SQL API database has the following system-generated
    properties. These properties are read-only:

    * `_rid`:   The resource ID.
    * `_ts`:    When the resource was last updated. The value is a timestamp.
    * `_self`:	The unique addressable URI for the resource.
    * `_etag`:	The resource etag required for optimistic concurrency control.
    * `_colls`:	The addressable path of the collections resource.
    * `_users`:	The addressable path of the users resource.
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        id: str,
        properties: Optional[dict[str, Any]] = None,
        rust_database: Optional[Any] = None
    ) -> None:
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        :param properties: Optional pre-loaded database properties.
        :param rust_database: Optional Rust DatabaseClient for Rust SDK operations.
        """
        self.client_connection = client_connection
        self.id = id
        self.database_link: str = "dbs/{}".format(self.id)
        self._properties: Optional[dict[str, Any]] = properties
        self._rust_database = rust_database  # Store Rust client for migration

    def __repr__(self) -> str:
        return "<DatabaseProxy [{}]>".format(self.database_link)[:1024]

    def _get_container_id(self, container_or_id: Union[str, ContainerProxy, Mapping[str, Any]]) -> str:
        if isinstance(container_or_id, str):
            return container_or_id
        if isinstance(container_or_id, ContainerProxy):
            return container_or_id.id
        return container_or_id["id"]

    def _get_container_link(self, container_or_id: Union[str, ContainerProxy, Mapping[str, Any]]) -> str:
        return "{}/colls/{}".format(self.database_link, self._get_container_id(container_or_id))

    def _get_user_link(self, user_or_id: Union[UserProxy, str, Mapping[str, Any]]) -> str:
        if isinstance(user_or_id, str):
            return "{}/users/{}".format(self.database_link, user_or_id)
        if isinstance(user_or_id, UserProxy):
            return user_or_id.user_link
        return "{}/users/{}".format(self.database_link, user_or_id["id"])

    def _get_properties(self) -> dict[str, Any]:
        if self._properties is None:
            self._properties = self.read()
        return self._properties

    @distributed_trace
    def read(  # pylint:disable=docstring-missing-param
        self,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Read the database properties.

        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the database properties.
        :rtype: dict[Str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )

        database_link = _get_database_link(self)
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"
        if use_rust:
            print("[DatabaseProxy.read] Using RUST SDK")
            if self._rust_database is None:
                raise RuntimeError("COSMOS_USE_RUST_BACKEND=true but _rust_database is None. "
                                   "Database must be created/retrieved with Rust backend enabled.")
            # RUST PATH: Call Rust SDK - convert Rust exceptions to Python SDK exceptions
            try:
                result_dict, headers_dict = self._rust_database.read()
            except Exception as e:
                # Convert Rust exceptions to Python SDK exceptions
                error_msg = str(e)
                if "404" in error_msg or "NotFound" in error_msg:
                    raise CosmosResourceNotFoundError(status_code=404, message=error_msg) from e
                raise
            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))
            self._properties = CosmosDict(dict(result_dict), response_headers=response_headers)
            return self._properties

        # PYTHON PATH: Use existing Python implementation
        print("[DatabaseProxy.read] Using PURE PYTHON")
        self._properties = self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )
        return self._properties

    @overload
    def create_container(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            populate_query_metrics: Optional[bool] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            return_properties: Literal[False] = False,
            **kwargs: Any
    ) -> ContainerProxy:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container creation failed.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 0
                :caption: Create a container with default settings:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container_with_settings]
                :end-before: [END create_container_with_settings]
                :language: python
                :dedent: 0
                :caption: Create a container with specific settings; in this case, a custom partition key:
        """
        ...

    @overload
    def create_container(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            populate_query_metrics: Optional[bool] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            return_properties: Literal[True],
            **kwargs: Any
    ) -> tuple[ContainerProxy, CosmosDict]:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A tuple of the `ContainerProxy`and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container creation failed.
        :rtype: tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 0
                :caption: Create a container with default settings:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container_with_settings]
                :end-before: [END create_container_with_settings]
                :language: python
                :dedent: 0
                :caption: Create a container with specific settings; in this case, a custom partition key:
        """
        ...

    @distributed_trace
    def create_container(  # pylint:disable=docstring-missing-param, too-many-statements, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param Any args: args
        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container or a tuple of the ContainerProxy
            and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container creation failed.
        :rtype: ~azure.cosmos.ContainerProxy or tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 0
                :caption: Create a container with default settings:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container_with_settings]
                :end-before: [END create_container_with_settings]
                :language: python
                :dedent: 0
                :caption: Create a container with specific settings; in this case, a custom partition key:
        """
        id = args[0] if len(args) > 0 else kwargs.pop('id')
        partition_key = args[1] if len(args) > 1 else kwargs.pop('partition_key')
        indexing_policy = args[2] if len(args) > 2 else kwargs.pop('indexing_policy', None)
        default_ttl = args[3] if len(args) > 3 else kwargs.pop('default_ttl', None)
        populate_query_metrics = args[4] if len(args) > 4 else kwargs.pop('populate_query_metrics', None)
        offer_throughput = args[5] if len(args) > 5 else kwargs.pop('offer_throughput', None)
        unique_key_policy = args[6] if len(args) > 6 else kwargs.pop('unique_key_policy', None)
        conflict_resolution_policy = args[7] if len(args) > 7 else kwargs.pop('conflict_resolution_policy', None)
        if len(args) > 8:
            raise TypeError(f"Unexpected positional parameters: {args[8:]}")
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)
        computed_properties = kwargs.pop('computed_properties', None)
        change_feed_policy = kwargs.pop('change_feed_policy', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        return_properties = kwargs.pop('return_properties', False)

        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "The 'populate_query_metrics' flag does not apply to this method"
                " and will be removed in the future",
                DeprecationWarning,
            )

        definition: dict[str, Any] = {"id": id}
        if partition_key is not None:
            definition["partitionKey"] = partition_key
        if indexing_policy is not None:
            if indexing_policy.get("indexingMode") is IndexingMode.Lazy:
                warnings.warn(
                    "Lazy indexing mode has been deprecated. Mode will be set to consistent indexing by the backend.",
                    DeprecationWarning
                )
            definition["indexingPolicy"] = indexing_policy
        if default_ttl is not None:
            definition["defaultTtl"] = default_ttl
        if unique_key_policy is not None:
            definition["uniqueKeyPolicy"] = unique_key_policy
        if conflict_resolution_policy is not None:
            definition["conflictResolutionPolicy"] = conflict_resolution_policy
        if analytical_storage_ttl is not None:
            definition["analyticalStorageTtl"] = analytical_storage_ttl
        if computed_properties is not None:
            definition["computedProperties"] = computed_properties
        if vector_embedding_policy is not None:
            definition["vectorEmbeddingPolicy"] = vector_embedding_policy
        if change_feed_policy is not None:
            definition["changeFeedPolicy"] = change_feed_policy
        if full_text_policy is not None:
            definition["fullTextPolicy"] = full_text_policy
        request_options = build_options(kwargs)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"
        if use_rust:
            print("[DatabaseProxy.create_container] Using RUST SDK")
            # RUST PATH: Call Rust SDK - no fallback, fail if Rust fails
            # Build partition_key dict for Rust
            pk_dict = {"paths": partition_key["paths"]} if partition_key else {}
            # Rust now returns (properties_dict, headers_dict) with full response body
            properties_dict, headers_dict = self._rust_database.create_container(id, pk_dict)
            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))

            # Get container id from properties
            container_id = properties_dict.get("id", id)

            # Get rust container client for the proxy
            rust_container = self._rust_database.get_container_client(container_id)

            container_proxy = ContainerProxy(
                self.client_connection,
                self.database_link,
                container_id,
                properties=dict(properties_dict),
                rust_container=rust_container
            )

            if not return_properties:
                return container_proxy
            return container_proxy, CosmosDict(dict(properties_dict), response_headers=response_headers)

        # PYTHON PATH: Use existing Python implementation
        print("[DatabaseProxy.create_container] Using PURE PYTHON")
        result = self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )

        if not return_properties:
            return ContainerProxy(self.client_connection, self.database_link, result["id"], properties=result)
        return ContainerProxy(self.client_connection, self.database_link, result["id"], properties=result), result

    @overload
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            populate_query_metrics: Optional[bool] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            return_properties: Literal[False] = False,
            **kwargs: Any
    ) -> ContainerProxy:
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container. Each vector
            embedding possesses a predetermined number of dimensions, is associated with an underlying data type, and
            is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy
        """
        ...

    @overload
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            populate_query_metrics: Optional[bool] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            return_properties: Literal[True],
            **kwargs: Any
    ) -> tuple[ContainerProxy, CosmosDict]:
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container. Each vector
            embedding possesses a predetermined number of dimensions, is associated with an underlying data type, and
            is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A  tuple of the `ContainerProxy`and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]
        """
        ...

    @distributed_trace
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param Any args: args
        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container. Each vector
            embedding possesses a predetermined number of dimensions, is associated with an underlying data type, and
            is generated for a particular distance function.
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container or a tuple of the ContainerProxy
            and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy or tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]
        """

        id = args[0] if len(args) > 0 else kwargs.pop('id')
        partition_key = args[1] if len(args) > 1 else kwargs.pop('partition_key')
        indexing_policy = args[2] if len(args) > 2 else kwargs.pop('indexing_policy', None)
        default_ttl = args[3] if len(args) > 3 else kwargs.pop('default_ttl', None)
        populate_query_metrics = args[4] if len(args) > 4 else kwargs.pop('populate_query_metrics', None)
        offer_throughput = args[5] if len(args) > 5 else kwargs.pop('offer_throughput', None)
        unique_key_policy = args[6] if len(args) > 6 else kwargs.pop('unique_key_policy', None)
        conflict_resolution_policy = args[7] if len(args) > 7 else kwargs.pop('conflict_resolution_policy', None)
        if len(args) > 8:
            raise TypeError(f"Unexpected positional parameters: {args[8:]}")
        initial_headers = kwargs.pop('initial_headers', None)
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)
        computed_properties = kwargs.pop('computed_properties', None)
        change_feed_policy = kwargs.pop('change_feed_policy', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        return_properties = kwargs.pop('return_properties', False)

        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)

        try:
            container_proxy = self.get_container_client(id)
            properties = container_proxy.read(
                populate_query_metrics=populate_query_metrics,
                initial_headers=initial_headers,
                **kwargs
            )
            if not return_properties:
                return container_proxy
            return container_proxy, properties
        except CosmosResourceNotFoundError:
            return self.create_container(
                id=id,
                partition_key=partition_key,
                indexing_policy=indexing_policy,
                default_ttl=default_ttl,
                populate_query_metrics=populate_query_metrics,
                offer_throughput=offer_throughput,
                unique_key_policy=unique_key_policy,
                conflict_resolution_policy=conflict_resolution_policy,
                analytical_storage_ttl=analytical_storage_ttl,
                computed_properties=computed_properties,
                initial_headers=initial_headers,
                vector_embedding_policy=vector_embedding_policy,
                change_feed_policy=change_feed_policy,
                full_text_policy=full_text_policy,
                return_properties=return_properties,
                **kwargs
            )

    @distributed_trace
    def delete_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """Delete a container.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`~azure.cosmos.ContainerProxy` instance or
            a dict representing the properties of the container.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the container couldn't be deleted.
        :rtype: None
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )

        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)
        collection_link = self._get_container_link(container)

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"
        if use_rust:
            print("[DatabaseProxy.delete_container] Using RUST SDK")
            # RUST PATH: Call Rust SDK - no fallback, fail if Rust fails
            # Extract container_id
            if isinstance(container, ContainerProxy):
                container_id = container.id
            elif isinstance(container, str):
                container_id = container
            else:
                container_id = container["id"]

            headers_dict = self._rust_database.delete_container(container_id)
            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))

            response_hook = kwargs.get('response_hook')
            if response_hook:
                response_hook(response_headers)
            return

        # PYTHON PATH: Use existing Python implementation
        print("[DatabaseProxy.delete_container] Using PURE PYTHON")
        self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)

    def get_container_client(self, container: Union[str, ContainerProxy, Mapping[str, Any]]) -> ContainerProxy:
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`~azure.cosmos.ContainerProxy` instance,
            or a dict representing the properties of the container to be retrieved.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :returns: A `ContainerProxy` instance representing the retrieved database.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START get_container]
                :end-before: [END get_container]
                :language: python
                :dedent: 0
                :caption: Get an existing container, handling a failure if encountered:
        """
        if isinstance(container, ContainerProxy):
            id_value = container.id
        elif isinstance(container, str):
            id_value = container
        else:
            id_value = container["id"]

        # Get Rust container client if Rust database is available
        rust_container = None
        if self._rust_database is not None:
            try:
                rust_container = self._rust_database.get_container_client(id_value)
            except Exception:
                pass  # Fall back to Python-only mode

        return ContainerProxy(
            self.client_connection,
            self.database_link,
            id_value,
            rust_container=rust_container
        )

    @distributed_trace
    def list_containers(  # pylint:disable=docstring-missing-param
        self,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List the containers in the database.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )

        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"

        if use_rust and self._rust_database is not None:
            print("[DatabaseProxy.list_containers] Using RUST SDK")
            # RUST PATH: Call Rust SDK
            containers_list, headers_dict = self._rust_database.list_containers(**kwargs)

            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))

            if response_hook:
                response_hook(response_headers, iter(containers_list))

            # Return list wrapped in iterator
            return iter(containers_list)

        # PYTHON PATH: Use existing Python implementation
        print("[DatabaseProxy.list_containers] Using PURE PYTHON")
        result = self.client_connection.ReadContainers(
            database_link=self.database_link, options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_containers(   # pylint:disable=docstring-missing-param
        self,
        query: Optional[str] = None,
        parameters: Optional[list[dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List the properties for containers in the current database.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: list[dict[str, Any]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )

        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        # Environment variable to toggle backend (for testing/comparison purposes)
        import os
        use_rust = os.environ.get("COSMOS_USE_RUST_BACKEND", "false").lower() == "true"

        if use_rust and self._rust_database is not None and query:
            print("[DatabaseProxy.query_containers] Using RUST SDK")
            # RUST PATH: Call Rust SDK (only supports simple queries, no parameters yet)
            query_str = query if parameters is None else query
            containers_list, headers_dict = self._rust_database.query_containers(query_str, **kwargs)

            from azure.core.utils import CaseInsensitiveDict
            response_headers = CaseInsensitiveDict(dict(headers_dict))

            if response_hook:
                response_hook(response_headers, iter(containers_list))

            # Return list wrapped in iterator
            return iter(containers_list)

        # PYTHON PATH: Use existing Python implementation
        print("[DatabaseProxy.query_containers] Using PURE PYTHON")
        result = self.client_connection.QueryContainers(
            database_link=self.database_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @overload
    def replace_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        partition_key: PartitionKey,
        indexing_policy: Optional[dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        conflict_resolution_policy: Optional[dict[str, Any]] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        initial_headers: Optional[dict[str, str]] = None,
        analytical_storage_ttl: Optional[int] = None,
        computed_properties: Optional[list[dict[str, str]]] = None,
        full_text_policy: Optional[dict[str, Any]] = None,
        return_properties: Literal[False] = False,
        vector_embedding_policy: Optional[dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`~azure.cosmos.ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be replaced.
            This includes if the container with given id does not exist.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START reset_container_properties]
                :end-before: [END reset_container_properties]
                :language: python
                :dedent: 0
                :caption: Reset the TTL property on a container, and display the updated properties:
        """
        ...

    @overload
    def replace_container(  # pylint:disable=docstring-missing-param
            self,
            container: Union[str, ContainerProxy, Mapping[str, Any]],
            partition_key: PartitionKey,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            populate_query_metrics: Optional[bool] = None,
            *,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            return_properties: Literal[True],
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            **kwargs: Any
    ) -> tuple[ContainerProxy, CosmosDict]:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`~azure.cosmos.ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A tuple of the `ContainerProxy`and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be replaced.
            This includes if the container with given id does not exist.
        :rtype: tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START reset_container_properties]
                :end-before: [END reset_container_properties]
                :language: python
                :dedent: 0
                :caption: Reset the TTL property on a container, and display the updated properties:
        """
        ...

    @distributed_trace
    def replace_container(  # pylint:disable=docstring-missing-param, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param Any args: args
        :param container: The ID (name), dict representing the properties or
            :class:`~azure.cosmos.ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :param dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container or a tuple of the ContainerProxy
            and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be replaced.
            This includes if the container with given id does not exist.
        :rtype: ~azure.cosmos.ContainerProxy or tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START reset_container_properties]
                :end-before: [END reset_container_properties]
                :language: python
                :dedent: 0
                :caption: Reset the TTL property on a container, and display the updated properties:
        """

        container = args[0] if len(args) > 0 else kwargs.pop('container', None)
        partition_key = args[1] if len(args) > 1 else kwargs.pop('partition_key')
        indexing_policy = args[2] if len(args) > 2 else kwargs.pop('indexing_policy', None)
        default_ttl = args[3] if len(args) > 3 else kwargs.pop('default_ttl', None)
        conflict_resolution_policy = args[4] if len(args) > 4 else kwargs.pop('conflict_resolution_policy', None)
        populate_query_metrics = args[5] if len(args) > 5 else kwargs.pop('populate_query_metrics', None)
        if len(args) > 6:
            raise TypeError(f"Unexpected positional parameters: {args[6:]}")
        initial_headers = kwargs.pop('initial_headers', None)
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        computed_properties = kwargs.pop('computed_properties', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        return_properties = kwargs.pop('return_properties', False)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)

        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )

        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)

        container_id = self._get_container_id(container)
        container_link = self._get_container_link(container_id)
        parameters = {
            key: value
            for key, value in {
                "id": container_id,
                "partitionKey": partition_key,
                "indexingPolicy": indexing_policy,
                "defaultTtl": default_ttl,
                "conflictResolutionPolicy": conflict_resolution_policy,
                "analyticalStorageTtl": analytical_storage_ttl,
                "computedProperties": computed_properties,
                "fullTextPolicy": full_text_policy,
                "vectorEmbeddingPolicy": vector_embedding_policy
            }.items()
            if value is not None
        }

        container_properties = self.client_connection.ReplaceContainer(
            container_link, collection=parameters, options=request_options, **kwargs)

        if not return_properties:
            return ContainerProxy(
                self.client_connection,
                self.database_link, container_properties["id"],
                properties=container_properties)
        return ContainerProxy(
            self.client_connection,
            self.database_link, container_properties["id"],
            properties=container_properties), container_properties

    @distributed_trace
    def list_users(
            self,
            max_item_count: Optional[int] = None,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List all the users in the container.

        :param int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadUsers(
            database_link=self.database_link, options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_users(
        self,
        query: str,
        parameters: Optional[list[dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Return all users matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: list[dict[str, Any]]
        :param int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryUsers(
            database_link=self.database_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    def get_user_client(self, user: Union[str, UserProxy, Mapping[str, Any]]) -> UserProxy:
        """Get a `UserProxy` for a user with specified ID.

        :param user: The ID (name), dict representing the properties or :class:`~azure.cosmos.UserProxy`
            instance of the user to be retrieved.
        :type user: Union[str, ~azure.cosmos.UserProxy, dict[str, Any]]
        :returns: A `UserProxy` instance representing the retrieved user.
        :rtype: ~azure.cosmos.UserProxy
        """
        if isinstance(user, UserProxy):
            id_value = user.id
        elif isinstance(user, str):
            id_value = user
        else:
            id_value = user["id"]
        return UserProxy(client_connection=self.client_connection, id=id_value, database_link=self.database_link)

    @distributed_trace
    def create_user(self, body: dict[str, Any], **kwargs: Any) -> UserProxy:
        """Create a new user in the container.

        To update or replace an existing user, use the
        :func:`ContainerProxy.upsert_user` method.

        :param dict[str, Any] body: A dict-like object with an `id` key and value representing the user to be created.
            The user ID must be unique within the database, and consist of no more than 255 characters.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A `UserProxy` instance representing the new user.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user couldn't be created.
        :rtype: ~azure.cosmos.UserProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_user]
                :end-before: [END create_user]
                :language: python
                :dedent: 0
                :caption: Create a database user:
        """
        request_options = build_options(kwargs)

        user = self.client_connection.CreateUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs)

        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def upsert_user(self, body: dict[str, Any], **kwargs: Any) -> UserProxy:
        """Insert or update the specified user.

        If the user already exists in the container, it is replaced. If the user
        does not already exist, it is inserted.

        :param dict[str, Any] body: A dict-like object representing the user to update or insert.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A `UserProxy` instance representing the upserted user.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user could not be upserted.
        :rtype: ~azure.cosmos.UserProxy
        """
        request_options = build_options(kwargs)

        user = self.client_connection.UpsertUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs)

        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def replace_user(
            self,
            user: Union[str, UserProxy, Mapping[str, Any]],
            body: dict[str, Any],
            **kwargs: Any
    ) -> UserProxy:
        """Replaces the specified user if it exists in the container.

        :param user: The ID (name), dict representing the properties or :class:`~azure.cosmos.UserProxy`
            instance of the user to be replaced.
        :type user: Union[str, ~azure.cosmos.UserProxy, dict[str, Any]]
        :param dict[str, Any] body: A dict-like object representing the user to replace.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A `UserProxy` instance representing the user after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If the replace operation failed or the user with given ID does not exist.
        :rtype: ~azure.cosmos.UserProxy
        """
        request_options = build_options(kwargs)

        replaced_user = self.client_connection.ReplaceUser(
            user_link=self._get_user_link(user), user=body, options=request_options, **kwargs
        )

        return UserProxy(
            client_connection=self.client_connection,
            id=replaced_user["id"],
            database_link=self.database_link,
            properties=replaced_user
        )

    @distributed_trace
    def delete_user(self, user: Union[str, UserProxy, Mapping[str, Any]], **kwargs: Any) -> None:
        """Delete the specified user from the container.

        :param user: The ID (name), dict representing the properties or :class:`~azure.cosmos.UserProxy`
            instance of the user to be deleted.
        :type user: Union[str, ~azure.cosmos.UserProxy, dict[str, Any]]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The user wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The user does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)

        self.client_connection.DeleteUser(user_link=self._get_user_link(user), options=request_options, **kwargs)

    @distributed_trace
    def read_offer(self, **kwargs: Any) -> Offer:
        """Get the ThroughputProperties object for this database.

        If no ThroughputProperties already exist for the database, an exception is raised.

        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the database.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        warnings.warn(
            "read_offer is a deprecated method name, use get_throughput instead",
            DeprecationWarning
        )
        return self.get_throughput(**kwargs)

    @distributed_trace
    def get_throughput(
            self,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = None,
            **kwargs: Any) -> ThroughputProperties:
        """Get the ThroughputProperties object for this database.

        If no ThroughputProperties already exist for the database, an exception is raised.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], list[dict[str, Any]]], None]
        :returns: ThroughputProperties for the database.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = list(self.client_connection.QueryOffers(query_spec, **kwargs))
        if not throughput_properties:
            raise CosmosResourceNotFoundError(
                status_code=_StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for database " + self.database_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return _deserialize_throughput(throughput=throughput_properties)

    @distributed_trace
    def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the database-level throughput.

        :param throughput: The throughput to be set (an integer).
        :type throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the database, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If no throughput properties exists for the database or if the throughput properties could not be updated.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = list(self.client_connection.QueryOffers(query_spec))
        if not throughput_properties:
            raise CosmosResourceNotFoundError(
                status_code=_StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for database " + self.database_link)
        new_offer = throughput_properties[0].copy()
        _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
        data = self.client_connection.ReplaceOffer(
            offer_link=throughput_properties[0]["_self"],
            offer=throughput_properties[0],
            **kwargs
        )
        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)
