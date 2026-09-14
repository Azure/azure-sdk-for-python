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
from ._base import build_options, _set_throughput_options, _build_properties_cache
from .container import ContainerProxy
from .offer import Offer, ThroughputProperties
from .exceptions import CosmosResourceNotFoundError
from .user import UserProxy
from .documents import IndexingMode
from ._cosmos_responses import CosmosDict
from ._helpers._item_dispatch import pick_backend
from ._helpers._page_response_hook import wrap_page_response_hook
from ._helpers.container_helper import ContainerHelper
from ._helpers._request_container import (
    RUST_GET_OR_CREATE_CONTAINER_UNSUPPORTED_MESSAGE,
    parse_container_create_args,
    prepare_container_get_or_create_read,
    validate_container_create_kwargs,
)
from ._helpers.database_helper import DatabaseHelper
from ._helpers.database_throughput_helper import (
    get_database_throughput,
    replace_database_throughput,
)
from ._global_secondary_index import GlobalSecondaryIndexDefinition, _normalize_gsi_container_properties

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
        *,
        _item_context: Any = None,
    ) -> None:
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self._item_context = _item_context
        self.id = id
        self.database_link: str = "dbs/{}".format(self.id)
        self._properties: Optional[dict[str, Any]] = properties

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
        *,
        initial_headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Fetch the database properties and refresh this proxy's stored properties.

        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: Called after success with a separate response-header
            snapshot and the database properties (``None`` for a 304 response).
        :paramtype response_hook: Callable[[Mapping[str, Any], Optional[dict[str, Any]]], None]
        :keyword str etag: Database ETag used with ``match_condition`` for a conditional read.
        :keyword match_condition: Condition translated to a request header. Use
            ``IfModified`` with an ETag for cache validation; a 304 returns an empty
            dict. ``If-Match`` is forwarded but is not an enforced guard on this GET.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword float timeout: Operation timeout in seconds. On Rust, must be a finite
            numeric duration of at least one second within its duration range.
            ``None`` leaves the override unset.
        :returns: A dict representing the database properties.
        :rtype: ~azure.cosmos.CosmosDict
        :raises TypeError: An obsolete option or a per-call read timeout was supplied.
        :raises NotImplementedError: A setting cannot be honored by the Rust backend.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        for option in ("session_token", "populate_query_metrics"):
            if option in kwargs:
                raise TypeError("DatabaseProxy.read() does not support the '{}' keyword argument".format(option))
        if kwargs.pop("read_timeout", None) is not None:
            raise TypeError("DatabaseProxy.read() does not support the 'read_timeout' keyword argument")

        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        response_hook = kwargs.pop("response_hook", None)
        request_options = build_options(kwargs)
        # Wildcard conditions may leave an unused ETag after validation builds the guard.
        kwargs.pop("etag", None)
        self._properties = DatabaseHelper(
            self.client_connection,
            pick_backend(self.client_connection),
        ).read_database(
            self.id,
            request_options,
            response_hook=response_hook,
            kwargs=kwargs,
        )
        return self._properties

    @overload
    def create_container(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
            return_properties: Literal[False] = False,
            **kwargs: Any
    ) -> ContainerProxy:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
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
            data type, and is generated for a particular distance function. Each vector embedding may also include an
            optional **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports
            ``sourcePaths`` (list of item paths whose values are embedded), ``deploymentName``, ``modelName``,
            ``endpoint`` (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
            return_properties: Literal[True],
            **kwargs: Any
    ) -> tuple[ContainerProxy, CosmosDict]:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
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
            data type, and is generated for a particular distance function. Each vector embedding may also include an
            optional **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports
            ``sourcePaths`` (list of item paths whose values are embedded), ``deploymentName``, ``modelName``,
            ``endpoint`` (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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

        :param Any args: Optional positional values for ``id`` and ``partition_key`` only.
        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: Called after success with a response-header copy and
            the created container properties.
        :paramtype response_hook: Callable[[Mapping[str, Any], CosmosDict], None]
        :keyword float timeout: Operation timeout in seconds. Rust supports finite,
            non-boolean numeric durations of at least one second within its duration
            range; ``None`` leaves the override unset.
        :raises TypeError: An obsolete keyword, per-call read timeout, or extra positional setting was supplied.
        :raises NotImplementedError: A setting cannot be honored by the Rust backend; no legacy fallback occurs.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword dict[str, Any] vector_embedding_policy: The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function. Each vector embedding may also include an
            optional **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports
            ``sourcePaths`` (list of item paths whose values are embedded), ``deploymentName``, ``modelName``,
            ``endpoint`` (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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
        id, partition_key = parse_container_create_args(args, kwargs)
        validate_container_create_kwargs(kwargs)
        indexing_policy = kwargs.pop('indexing_policy', None)
        default_ttl = kwargs.pop('default_ttl', None)
        offer_throughput = kwargs.pop('offer_throughput', None)
        unique_key_policy = kwargs.pop('unique_key_policy', None)
        conflict_resolution_policy = kwargs.pop('conflict_resolution_policy', None)
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)
        computed_properties = kwargs.pop('computed_properties', None)
        change_feed_policy = kwargs.pop('change_feed_policy', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        global_secondary_index = kwargs.pop('global_secondary_index', None)
        return_properties = kwargs.pop('return_properties', False)

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
        if global_secondary_index is not None:
            gsi_dict = self._resolve_gsi_definition(global_secondary_index)
            definition["globalSecondaryIndexDefinition"] = gsi_dict
            definition["materializedViewDefinition"] = gsi_dict
        response_hook = kwargs.pop("response_hook", None)
        request_options = build_options(kwargs)
        # Wildcard conditions can leave an unused ETag after validation builds the header.
        kwargs.pop("etag", None)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)
        result = ContainerHelper(
            self.client_connection,
            pick_backend(self.client_connection),
        ).create_container(
            self.database_link,
            definition,
            request_options,
            response_hook=response_hook,
            kwargs=kwargs,
        )
        _normalize_gsi_container_properties(result)

        if not return_properties:
            return ContainerProxy(self.client_connection, self.database_link, result["id"], properties=result,
                                  _item_context=self._item_context)
        return ContainerProxy(self.client_connection, self.database_link, result["id"], properties=result,
                              _item_context=self._item_context), result

    @overload
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: PartitionKey,
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
            return_properties: Literal[False] = False,
            **kwargs: Any
    ) -> ContainerProxy:
        """Create a container if it does not exist already.

        Existing container settings and throughput are neither checked nor updated.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``; non-``None`` ``read_timeout`` is also rejected.
        Unsupported Rust options fail before the first request rather than
        falling back to legacy Python. A supported ``timeout`` applies separately
        to the read and create steps, not to the combined workflow.
        The response hook receives copied headers and properties from the successful
        step; its exceptions propagate without triggering creation.
        This is not atomic: a concurrent create can cause a 409 conflict, which
        propagates without rereading. Conditional headers are forwarded, not
        interpreted as a lock spanning the two steps.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
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
            is generated for a particular distance function. Each vector embedding may also include an optional
            **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports ``sourcePaths``
            (list of item paths whose values are embedded), ``deploymentName``, ``modelName``, ``endpoint``
            (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
            unique_key_policy: Optional[dict[str, Any]] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            vector_embedding_policy: Optional[dict[str, Any]] = None,
            change_feed_policy: Optional[dict[str, Any]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
            return_properties: Literal[True],
            **kwargs: Any
    ) -> tuple[ContainerProxy, CosmosDict]:
        """Create a container if it does not exist already.

        Existing container settings and throughput are neither checked nor updated.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``; non-``None`` ``read_timeout`` is also rejected.
        Unsupported Rust options fail before the first request rather than
        falling back to legacy Python. A supported ``timeout`` applies separately
        to the read and create steps, not to the combined workflow.
        The response hook receives copied headers and properties from the successful
        step; its exceptions propagate without triggering creation.
        This is not atomic: a concurrent create can cause a 409 conflict, which
        propagates without rereading. Conditional headers are forwarded, not
        interpreted as a lock spanning the two steps.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
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
            is generated for a particular distance function. Each vector embedding may also include an optional
            **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports ``sourcePaths``
            (list of item paths whose values are embedded), ``deploymentName``, ``modelName``, ``endpoint``
            (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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

        Existing container settings and throughput are neither checked nor updated.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``; non-``None`` ``read_timeout`` is also rejected.
        Unsupported Rust options fail before the first request rather than
        falling back to legacy Python. A supported ``timeout`` applies separately
        to the read and create steps, not to the combined workflow.
        The response hook receives copied headers and properties from the successful
        step; its exceptions propagate without triggering creation.
        This is not atomic: a concurrent create can cause a 409 conflict, which
        propagates without rereading. Conditional headers are forwarded, not
        interpreted as a lock spanning the two steps.

        :param Any args: args
        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
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
            is generated for a particular distance function. Each vector embedding may also include an optional
            **provisional** ``embeddingSource`` describing how the embedding is generated by the service.
            The source object supports ``sourcePaths``
            (list of item paths whose values are embedded), ``deploymentName``, ``modelName``, ``endpoint``
            (embedding service endpoint), and ``authType`` (one of ``ApiKey`` or ``Entra``).
        :keyword dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
        :keyword bool return_properties: Specifies whether to return either a ContainerProxy
            or a Tuple of a ContainerProxy and the container properties.
        :returns: A `ContainerProxy` instance representing the new container or a tuple of the ContainerProxy
            and CosmosDict with the container properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy or tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]
        """

        id, partition_key = parse_container_create_args(
            args, kwargs, method_name="create_container_if_not_exists"
        )
        validate_container_create_kwargs(kwargs, method_name="create_container_if_not_exists")
        indexing_policy = kwargs.pop('indexing_policy', None)
        default_ttl = kwargs.pop('default_ttl', None)
        offer_throughput = kwargs.pop('offer_throughput', None)
        unique_key_policy = kwargs.pop('unique_key_policy', None)
        conflict_resolution_policy = kwargs.pop('conflict_resolution_policy', None)
        initial_headers = kwargs.pop('initial_headers', None)
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)
        computed_properties = kwargs.pop('computed_properties', None)
        change_feed_policy = kwargs.pop('change_feed_policy', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        global_secondary_index = kwargs.pop('global_secondary_index', None)
        return_properties = kwargs.pop('return_properties', False)

        response_hook = kwargs.pop("response_hook", None)
        read_options, read_kwargs, rust_eligible = prepare_container_get_or_create_read(
            kwargs, initial_headers=initial_headers, offer_throughput=offer_throughput
        )
        container_proxy = self.get_container_client(id)
        try:
            properties = ContainerHelper(
                self.client_connection, pick_backend(self.client_connection)
            ).read_container(
                container_proxy.container_link,
                read_options,
                kwargs=read_kwargs,
                rust_eligible=rust_eligible,
                allow_legacy_fallback=False,
                unsupported_message=RUST_GET_OR_CREATE_CONTAINER_UNSUPPORTED_MESSAGE,
            )
        except CosmosResourceNotFoundError:
            return self.create_container(
                id=id,
                partition_key=partition_key,
                indexing_policy=indexing_policy,
                default_ttl=default_ttl,
                offer_throughput=offer_throughput,
                unique_key_policy=unique_key_policy,
                conflict_resolution_policy=conflict_resolution_policy,
                analytical_storage_ttl=analytical_storage_ttl,
                computed_properties=computed_properties,
                initial_headers=initial_headers,
                vector_embedding_policy=vector_embedding_policy,
                change_feed_policy=change_feed_policy,
                full_text_policy=full_text_policy,
                global_secondary_index=global_secondary_index,
                return_properties=return_properties,
                response_hook=response_hook,
                **kwargs
            )
        _normalize_gsi_container_properties(properties)
        if response_hook is not None:
            response_hook(properties.get_response_headers(), properties)
        self.client_connection._set_container_properties_cache(
            container_proxy.container_link, _build_properties_cache(properties, container_proxy.container_link)
        )
        if not return_properties:
            return container_proxy
        return container_proxy, properties

    @distributed_trace
    def delete_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        *,
        initial_headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """Delete a container and its contents, returning ``None`` on success.

        A missing container raises ``CosmosResourceNotFoundError``. Only the
        container may be positional. Session/metrics keywords and non-``None``
        ``read_timeout`` are rejected. Unsupported Rust settings fail without
        legacy fallback. The response hook receives copied headers and ``None``.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`~azure.cosmos.ContainerProxy` instance or
            a dict representing the properties of the container.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword float timeout: Operation timeout in seconds. On Rust, an explicit timeout covers
            both the internal container lookup and deletion.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the container couldn't be deleted.
        :rtype: None
        """
        validate_container_create_kwargs(kwargs, method_name="delete_container")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        response_hook = kwargs.pop("response_hook", None)
        request_options = build_options(kwargs)
        kwargs.pop("etag", None)
        collection_link = self._get_container_link(container)
        ContainerHelper(self.client_connection, pick_backend(self.client_connection)).delete_container(
            collection_link, request_options, response_hook=response_hook, kwargs=kwargs,
        )

    def get_container_client(self, container: Union[str, ContainerProxy, Mapping[str, Any]]) -> ContainerProxy:
        """Create a local `ContainerProxy` without reading or creating a container.

        This method does not check whether the container exists. The target is
        always in this database. Properties mappings supply only ``id``, which
        is converted to a string; other properties are not cached.

        :param container: The ID (name) of the container, a :class:`~azure.cosmos.ContainerProxy` instance,
            or a mapping of container properties containing ``id``.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, Mapping[str, Any]]
        :returns: A new `ContainerProxy` instance representing the container.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START get_container]
                :end-before: [END get_container]
                :language: python
                :dedent: 0
                :caption: Get a container client for subsequent operations:
        """
        if isinstance(container, ContainerProxy):
            id_value = container.id
        elif isinstance(container, str):
            id_value = container
        else:
            id_value = str(container["id"])
        return ContainerProxy(self.client_connection, self.database_link, id_value, _item_context=self._item_context)

    def _resolve_gsi_definition(
        self,
        global_secondary_index: Union["GlobalSecondaryIndexDefinition", dict[str, Any]],
    ) -> dict[str, Any]:
        """Serialize a GSI definition and populate the source container's resource id (_rid).

        The service resolves the source container by its resource id (``sourceCollectionRid``).
        When the caller only provides the source container id, read the source container to
        obtain its ``_rid`` and populate ``sourceCollectionRid`` on the wire payload.

        :param global_secondary_index: The GSI definition object or raw dict.
        :type global_secondary_index:
            ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
        :returns: The serialized GSI definition including ``sourceCollectionRid``.
        :rtype: dict[str, Any]
        """
        gsi_dict = (global_secondary_index._to_dict()  # pylint: disable=protected-access
                    if hasattr(global_secondary_index, '_to_dict')
                    else dict(global_secondary_index))
        if not gsi_dict.get("sourceCollectionRid"):
            source_container_id = gsi_dict.get("sourceCollectionId")
            if source_container_id:
                source_properties = self.get_container_client(source_container_id).read()
                gsi_dict["sourceCollectionRid"] = source_properties["_rid"]
        return gsi_dict

    @distributed_trace
    def list_containers(  # pylint:disable=docstring-missing-param
        self,
        *,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List the containers in the database.

        :keyword int max_item_count: Maximum number of containers requested per page, not a total result limit.
        :keyword float timeout: Timeout budget in seconds per page fetch by default, not for draining
            the whole iterator. Rust supports finite numeric durations of at least one second
            within its duration range; ``None`` leaves the override unset.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A synchronous callable invoked after each successfully fetched page,
            with a snapshot of that page's response headers. It is not called before iteration.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]

        All settings are keyword-only. ``session_token``, ``populate_query_metrics``,
        and ``availability_strategy`` are rejected, including explicit ``None`` or ``False``.
        Per-call ``read_timeout`` is not supported; configure it on ``CosmosClient``.
        Unsupported Rust page options raise during iteration instead of using legacy Python.

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
        """
        if kwargs.pop("read_timeout", None) is not None:
            raise TypeError(
                "list_containers() does not support the 'read_timeout' keyword argument; "
                "configure it when constructing CosmosClient."
            )
        for option in ("session_token", "populate_query_metrics", "availability_strategy"):
            if option in kwargs:
                raise TypeError(f"list_containers() does not support the '{option}' keyword argument")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if response_hook is not None:
            kwargs["response_hook"] = wrap_page_response_hook(response_hook)
        return self.client_connection.ReadContainers(
            database_link=self.database_link, options=feed_options, **kwargs
        )

    @distributed_trace
    def query_containers(   # pylint:disable=docstring-missing-param
        self,
        query: Optional[Union[str, dict[str, Any]]],
        *,
        parameters: Optional[list[dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Query container properties in the current database, not the items inside them.

        :param query: SQL text or a dictionary containing query text and optional parameters.
            Explicit ``None`` without parameters retains unfiltered listing behavior.
        :type query: Union[str, dict[str, Any], None]
        :keyword parameters: Optional query parameters, each with ``name`` and ``value`` keys.
        :paramtype parameters: list[dict[str, Any]]
        :keyword int max_item_count: Maximum number of containers requested per page, not a total result limit.
        :keyword float timeout: Timeout budget in seconds per page fetch by default. Rust supports
            finite numeric durations of at least one second within its duration range;
            ``None`` leaves the override unset.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A synchronous callable invoked after each successfully fetched page,
            with an independent snapshot of that page's response headers, not before iteration.
        :paramtype response_hook: Callable[[Mapping[str, Any]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]

        ``query`` is required; all other settings are keyword-only. Use ``list_containers()``
        for an unfiltered inventory. ``session_token``, ``populate_query_metrics``,
        ``availability_strategy``, and ``enable_cross_partition_query`` are rejected,
        including explicit ``None`` or ``False``. Configure ``read_timeout`` on ``CosmosClient``,
        not on this call. Unsupported Rust options raise during iteration rather than
        switching to legacy Python.
        """
        if kwargs.pop("read_timeout", None) is not None:
            raise TypeError(
                "query_containers() does not support the 'read_timeout' keyword argument; "
                "configure it when constructing CosmosClient."
            )
        for option in ("session_token", "populate_query_metrics", "availability_strategy",
                       "enable_cross_partition_query"):
            if option in kwargs:
                raise TypeError(f"query_containers() does not support the '{option}' keyword argument")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if response_hook is not None:
            kwargs["response_hook"] = wrap_page_response_hook(response_hook)
        return self.client_connection.QueryContainers(
            database_link=self.database_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )

    @overload
    def replace_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        partition_key: PartitionKey,
        *,
        indexing_policy: Optional[dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        conflict_resolution_policy: Optional[dict[str, Any]] = None,
        initial_headers: Optional[dict[str, str]] = None,
        analytical_storage_ttl: Optional[int] = None,
        computed_properties: Optional[list[dict[str, str]]] = None,
        full_text_policy: Optional[dict[str, Any]] = None,
        global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
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
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            conflict_resolution_policy: Optional[dict[str, Any]] = None,
            initial_headers: Optional[dict[str, str]] = None,
            analytical_storage_ttl: Optional[int] = None,
            computed_properties: Optional[list[dict[str, str]]] = None,
            full_text_policy: Optional[dict[str, Any]] = None,
            global_secondary_index: Optional[Union[GlobalSecondaryIndexDefinition, dict[str, Any]]] = None,
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
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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

        Only ``container`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError``. ``session_token`` and ``populate_query_metrics``
        are rejected even when set to ``None`` or ``False``. Configure ``read_timeout``
        on ``CosmosClient``; a non-``None`` per-call value is rejected.
        Conditional ``etag`` and ``match_condition`` settings remain supported.
        Unsupported Rust options fail without legacy fallback.

        :param Any args: args
        :param container: The ID (name), dict representing the properties or
            :class:`~azure.cosmos.ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, dict[str, Any]]
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword list[dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword response_hook: A synchronous callable receiving independent snapshots of
            ``(headers, properties)`` once after a successful replacement.
        :paramtype response_hook: Callable[[Mapping[str, Any], dict[str, Any]], None]
        :keyword float timeout: Supported Rust timeout in seconds for metadata resolution and
            replacement together. A finite numeric duration of at least one second within
            Rust's duration range is supported; ``None`` leaves the override unset.
        :keyword dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :keyword global_secondary_index: **provisional** The global secondary index
            definition for the container.
            Used to create a GSI container derived from a source container via a SQL projection query.
        :paramtype global_secondary_index: ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
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

        container, partition_key = parse_container_create_args(
            args, kwargs, method_name="replace_container", target_parameter="container",
        )
        validate_container_create_kwargs(kwargs, method_name="replace_container")
        indexing_policy = kwargs.pop('indexing_policy', None)
        default_ttl = kwargs.pop('default_ttl', None)
        conflict_resolution_policy = kwargs.pop('conflict_resolution_policy', None)
        initial_headers = kwargs.pop('initial_headers', None)
        analytical_storage_ttl = kwargs.pop('analytical_storage_ttl', None)
        computed_properties = kwargs.pop('computed_properties', None)
        full_text_policy = kwargs.pop('full_text_policy', None)
        global_secondary_index = kwargs.pop('global_secondary_index', None)
        return_properties = kwargs.pop('return_properties', False)
        vector_embedding_policy = kwargs.pop('vector_embedding_policy', None)

        response_hook = kwargs.pop("response_hook", None)
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)
        kwargs.pop("etag", None)

        container_id = str(self._get_container_id(container))
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
        if global_secondary_index is not None:
            gsi_dict = self._resolve_gsi_definition(global_secondary_index)
            parameters["globalSecondaryIndexDefinition"] = gsi_dict
            parameters["materializedViewDefinition"] = gsi_dict

        container_properties = ContainerHelper(
            self.client_connection, pick_backend(self.client_connection),
        ).replace_container(
            container_link, parameters, request_options, response_hook=response_hook, kwargs=kwargs,
        )
        _normalize_gsi_container_properties(container_properties)

        if not return_properties:
            return ContainerProxy(
                self.client_connection,
                self.database_link, container_properties["id"],
                properties=container_properties, _item_context=self._item_context)
        return ContainerProxy(
            self.client_connection,
            self.database_link, container_properties["id"],
            properties=container_properties, _item_context=self._item_context), container_properties

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
        return get_database_throughput(
            client_connection=self.client_connection,
            database_link=self.database_link,
            get_properties=self._get_properties,
            not_found_message="Could not find ThroughputProperties for database " + self.database_link,
            response_hook=response_hook,
            kwargs=kwargs,
        )

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
        return replace_database_throughput(
            client_connection=self.client_connection,
            database_link=self.database_link,
            get_properties=self._get_properties,
            throughput=throughput,
            not_found_message="Could not find ThroughputProperties for database " + self.database_link,
            kwargs=kwargs,
            # The sync method has always run the offer read with no keywords, and
            # applied the caller's keywords only to the replace.
            read_kwargs={},
        )
