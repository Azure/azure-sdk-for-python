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

"""Provide DatabaseProxy, the Python wrapper object for one database.

The customer app obtains this object through
client.get_database_client("sales"). Here, proxy means a Python object
representing a service resource, not a network proxy.

The object lets the customer app select containers and perform database
operations. For example::

    database = client.get_database_client("sales")
    orders = database.get_container_client("orders")

These calls create local Python objects without reading, creating, or
checking the resources in the service backend. The returned objects
retain the existing client context for later operations.

An operation such as database.read() requests the database's properties
from the service backend; obtaining the DatabaseProxy does not.
"""

from typing import TYPE_CHECKING, Any, Union, Optional, Mapping, Callable, overload, Literal

import time
import warnings
import azure
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged

from ._backend.capabilities import OperationRouting
from ._telemetry import BindingAlternatives, delegate_operation, trace_operation
from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options, _set_throughput_options, _build_properties_cache
from .container import ContainerProxy
from .offer import ThroughputProperties
from .exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
from .documents import IndexingMode
from ._cosmos_responses import CosmosDict
from ._operation_deadline import remaining_timeout
from ._helpers._item_arguments import get_selected_backend
from ._helpers._list_containers import list_containers as _list_containers, query_containers as _query_containers
from ._helpers._container_operations import ContainerHelper, container_creation_retry_delay
from ._helpers._response_parse import (
    validate_response_hook_is_synchronous,
    with_response_header_snapshot,
)
from ._helpers._request_container import (
    container_creation_read_options,
    parse_container_create_args,
    preflight_create_container,
    prepare_container_get_or_create_read,
    validate_container_create_kwargs,
    validate_container_retry_write_kwargs,
)
from ._helpers._request_settings import validate_operation_timeout
from ._helpers._database_operations import DatabaseHelper
from ._helpers._request_database import (
    validate_database_read_kwargs,
    validate_obsolete_resource_options,
)
from ._helpers._database_throughput import (
    get_database_throughput,
    replace_database_throughput,
)
from ._global_secondary_index import GlobalSecondaryIndexDefinition, _normalize_gsi_container_properties
from ._backend.capabilities import prepare_operation_kwargs

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._backend.cosmos_backend import CosmosBackend
    from ._helpers._client_context import CosmosClientContext
    from ._inference_client import InferenceClient
    from ._inference_service import _InferenceService

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
    :func:`~azure.cosmos.CosmosClient.get_database_client` method to obtain a local
    database proxy, or :func:`~azure.cosmos.CosmosClient.create_database` to create
    a new database.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    :ivar id: The ID (name) of the database.

    An Azure Cosmos DB SQL API database has the following system-generated
    properties. These properties are read-only:

    * `_rid`:   The resource ID.
    * `_ts`:    When the resource was last updated. The value is a timestamp.
    * `_self`:	The unique addressable URI for the resource.
    * `_etag`:	The resource etag required for optimistic concurrency control.
    * `_colls`:	The addressable path of the collections resource.
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        id: str,
        properties: Optional[dict[str, Any]] = None,
        *,
        _client_context: "Optional[CosmosClientContext[CosmosBackend]]" = None,
        _inference_client: "Optional[InferenceClient[TokenCredential, _InferenceService]]" = None,
    ) -> None:
        """
        :param client_connection: Connection owned by the client creating this proxy.
        :type client_connection: ~azure.cosmos._cosmos_client_connection.CosmosClientConnection
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self._client_context = _client_context
        self._inference_client = _inference_client
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

    def _get_properties(self, *, deadline: Optional[float] = None) -> dict[str, Any]:
        if self._properties is None:
            if deadline is None:
                self._properties = self.read()
            else:
                self._properties = DatabaseHelper(
                    self.client_connection, get_selected_backend(self.client_connection),
                ).read_database(self.id, {}, deadline=deadline)
        return self._properties

    @trace_operation(binding_operation="read_database")
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
        :raises TypeError: An obsolete or unsupported argument or header override was supplied.
        :raises ValueError: The operation timeout is not a supported numeric duration.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        prepare_operation_kwargs(self, kwargs, headers=initial_headers)
        validate_database_read_kwargs(kwargs)

        # build_options mutates its options dictionary; keep caller inputs reusable.
        for name in ("request_options", "feed_options"):
            if isinstance(kwargs.get(name), Mapping):
                kwargs[name] = dict(kwargs[name])
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        response_hook = kwargs.pop("response_hook", None)
        request_options = build_options(kwargs)
        # A wildcard match condition does not need an etag, so one may be left
        # over in kwargs after the options are built. Drop it.
        kwargs.pop("etag", None)
        self._properties = DatabaseHelper(
            self.client_connection,
            get_selected_backend(self.client_connection),
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
            partition_key: "azure.cosmos.PartitionKey",
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, "azure.cosmos.ThroughputProperties"]] = None,
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
    ) -> "azure.cosmos.ContainerProxy":
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
            partition_key: "azure.cosmos.PartitionKey",
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, "azure.cosmos.ThroughputProperties"]] = None,
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
    ) -> tuple["azure.cosmos.ContainerProxy", CosmosDict]:
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

    @trace_operation(binding_operation="create_container")
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
            a deep copy of the created container properties. Hook edits do not change
            the returned properties or cached partition key. The callback must be
            synchronous; invalid callbacks are rejected before creation or a GSI source lookup.
        :paramtype response_hook: Callable[[Mapping[str, Any], CosmosDict], None]
        :keyword float timeout: Operation timeout in seconds. Rust supports finite,
            non-boolean numeric durations of at least one second within its duration
            range; ``None`` leaves the override unset. GSI source lookup, creation,
            and any required properties read share the same timeout budget.
        :raises TypeError: An obsolete or unsupported setting, header override,
            invalid response hook, or extra positional setting was supplied.
            Unsupported calls do not fall back to legacy Python.
        :raises ValueError: The operation timeout is invalid.
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
            A successful empty creation response returns a proxy using the requested ID.
            If properties were requested, an additional read retrieves current properties
            within the remaining timeout. Its failure propagates without repeating creation.
            The response hook observes only the original creation response.
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
        started = time.monotonic()
        deadline = kwargs.pop("_item_operation_deadline", None)
        prepare_operation_kwargs(self, kwargs)
        id, partition_key = parse_container_create_args(args, kwargs)
        validate_obsolete_resource_options(kwargs, "create_container")
        response_hook = kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_container response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "create_container")
        if get_selected_backend(self.client_connection).name == "rust":
            timeout = kwargs.get("timeout")
            validate_operation_timeout(timeout)
            if deadline is None and timeout is not None:
                deadline = started + float(timeout)
        remaining_timeout(deadline)
        indexing_policy = kwargs.pop('indexing_policy', None)
        offer_throughput = kwargs.pop('offer_throughput', None)
        properties = {
            wire_name: kwargs.pop(option, None)
            for option, wire_name in (
                ("default_ttl", "defaultTtl"),
                ("unique_key_policy", "uniqueKeyPolicy"),
                ("conflict_resolution_policy", "conflictResolutionPolicy"),
                ("analytical_storage_ttl", "analyticalStorageTtl"),
                ("computed_properties", "computedProperties"),
                ("vector_embedding_policy", "vectorEmbeddingPolicy"),
                ("change_feed_policy", "changeFeedPolicy"),
                ("full_text_policy", "fullTextPolicy"),
            )
        }
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
        definition.update({name: value for name, value in properties.items() if value is not None})
        for name in ("request_options", "feed_options"):
            if name in kwargs:
                kwargs[name] = dict(kwargs[name])
        request_options = build_options(kwargs)
        # A wildcard match condition does not need an etag, so one may be left
        # over in kwargs after the options are built. Drop it.
        kwargs.pop("etag", None)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)
        prepared = None
        if global_secondary_index is not None:
            if get_selected_backend(self.client_connection).name == "rust":
                prepared = preflight_create_container(self.database_link, definition, request_options, kwargs)
            gsi_dict = self._resolve_gsi_definition(global_secondary_index, deadline=deadline)
            definition["globalSecondaryIndexDefinition"] = gsi_dict
            definition["materializedViewDefinition"] = gsi_dict
        result = ContainerHelper(
            self.client_connection,
            get_selected_backend(self.client_connection),
        ).create_container(
            self.database_link,
            definition,
            request_options,
            response_hook=response_hook,
            kwargs=kwargs,
            deadline=deadline,
            prepared=prepared,
        )
        _normalize_gsi_container_properties(result)

        container = ContainerProxy(
            self.client_connection,
            self.database_link,
            result["id"] if result else id,
            properties=result,
            _client_context=self._client_context,
            _inference_client=self._inference_client,
        )
        if not return_properties:
            return container
        if not result:
            remaining_timeout(deadline)
            result = container.read(
                request_options=container_creation_read_options(request_options),
                _item_operation_deadline=deadline,
                **kwargs,
            )
        return container, result

    @overload
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        partition_key: "azure.cosmos.PartitionKey",
        *,
        indexing_policy: Optional[dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        offer_throughput: Optional[Union[int, "azure.cosmos.ThroughputProperties"]] = None,
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
        **kwargs: Any,
    ) -> "azure.cosmos.ContainerProxy":
        """Create a container if it does not exist already.

        Existing container settings and throughput are neither checked nor updated.
        For example, requesting ``orders`` with ``default_ttl=86400`` leaves an
        existing default item lifetime of 3600 seconds unchanged.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``, including their ``sessionToken`` and ``populateQueryMetrics``
        entries in ``request_options`` or ``feed_options``.
        On the Rust-backed SDK, non-``None`` ``retry_write`` values, including
        ``0`` and ``False``, raise ``TypeError`` before the first read, whether
        top-level or nested in either options dictionary. Omit it or use ``None``.
        Unsupported options raise ``TypeError`` before the first request rather
        than falling back to legacy Python.
        A supported ``timeout`` is shared across reads, creation, and any GSI
        source-container read. For example, a three-second read with ``timeout=10``
        leaves at most seven seconds. A timeout does not undo creation already
        performed by the service backend.
        The response hook receives copied headers and a deep copy of properties
        from the successful step; its exceptions propagate without triggering
        creation or another create attempt.
        If creation conflicts with another caller, read the container using the
        remaining timeout. A 404/1013 response means creation is still in progress;
        only that response permits up to nine additional reads, with waits of
        100 ms growing to one second within the same timeout. Other read failures
        propagate without another create. Conditional headers are forwarded;
        the workflow is not atomic.
        A 304 existence read returns empty properties without fetching them again.
        For a successful creation response without properties, the hook receives
        empty properties and creation headers, not any later properties read.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A synchronous callable invoked once with response headers and properties,
            or None. Non-callable values and declared async hooks raise TypeError before any request.
        :keyword float timeout: Shared operation budget in seconds, or None for no per-call override.
            Must be finite, non-boolean, at least one, and less than 2**64.
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
            or a tuple of a ContainerProxy and the container properties. If creation returns no properties,
            False needs no extra read; True reads properties with the remaining timeout, without the create condition.
            Those properties describe the later read, not a guaranteed creation-time snapshot.
            A failed properties read propagates without another create attempt.
        :returns: A `ContainerProxy` instance representing the existing or newly created container.
        :raises TypeError: Required arguments, options, or the response hook are unsupported.
        :raises ValueError: The timeout value is invalid.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: The shared operation timeout expired.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy
        """
        ...

    @overload
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
            self,
            id: str,
            partition_key: "azure.cosmos.PartitionKey",
            *,
            indexing_policy: Optional[dict[str, Any]] = None,
            default_ttl: Optional[int] = None,
            offer_throughput: Optional[Union[int, "azure.cosmos.ThroughputProperties"]] = None,
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
    ) -> tuple["azure.cosmos.ContainerProxy", CosmosDict]:
        """Create a container if it does not exist already.

        Existing container settings and throughput are neither checked nor updated.
        For example, requesting ``orders`` with ``default_ttl=86400`` leaves an
        existing default item lifetime of 3600 seconds unchanged.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``, including their ``sessionToken`` and ``populateQueryMetrics``
        entries in ``request_options`` or ``feed_options``.
        On the Rust-backed SDK, non-``None`` ``retry_write`` values, including
        ``0`` and ``False``, raise ``TypeError`` before the first read, whether
        top-level or nested in either options dictionary. Omit it or use ``None``.
        Unsupported options raise ``TypeError`` before the first request rather
        than falling back to legacy Python.
        A supported ``timeout`` is shared across reads, creation, and any GSI
        source-container read. For example, a three-second read with ``timeout=10``
        leaves at most seven seconds. A timeout does not undo creation already
        performed by the service backend.
        The response hook receives copied headers and a deep copy of properties
        from the successful step; its exceptions propagate without triggering
        creation or another create attempt.
        If creation conflicts with another caller, read the container using the
        remaining timeout. A 404/1013 response means creation is still in progress;
        only that response permits up to nine additional reads, with waits of
        100 ms growing to one second within the same timeout. Other read failures
        propagate without another create. Conditional headers are forwarded;
        the workflow is not atomic.
        A 304 existence read returns empty properties without fetching them again.
        For a successful creation response without properties, the hook receives
        empty properties and creation headers, not any later properties read.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :keyword dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A synchronous callable invoked once with response headers and properties,
            or None. Non-callable values and declared async hooks raise TypeError before any request.
        :keyword float timeout: Shared operation budget in seconds, or None for no per-call override.
            Must be finite, non-boolean, at least one, and less than 2**64.
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
            or a tuple of a ContainerProxy and the container properties. If creation returns no properties,
            False needs no extra read; True reads properties with the remaining timeout, without the create condition.
            Those properties describe the later read, not a guaranteed creation-time snapshot.
            A failed properties read propagates without another create attempt.
        :returns: A tuple of the `ContainerProxy` and CosmosDict with properties of the existing
            or newly created container.
        :raises TypeError: Required arguments, options, or the response hook are unsupported.
        :raises ValueError: The timeout value is invalid.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: The shared operation timeout expired.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]
        """
        ...

    @trace_operation(binding_operation=("read_container", "create_container", "read_container"))
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param, docstring-should-be-keyword
        self,
        *args: Any,
        **kwargs: Any
    ) -> Union[ContainerProxy, tuple[ContainerProxy, CosmosDict]]:
        """Create a container if it does not exist already.

        Existing container settings and throughput are neither checked nor updated.
        For example, requesting ``orders`` with ``default_ttl=86400`` leaves an
        existing default item lifetime of 3600 seconds unchanged.
        Only ``id`` and ``partition_key`` may be positional. Missing or duplicate
        required arguments raise ``TypeError`` before sending a request.
        ``session_token`` and ``populate_query_metrics`` are rejected even when
        ``None``, including their ``sessionToken`` and ``populateQueryMetrics``
        entries in ``request_options`` or ``feed_options``.
        On the Rust-backed SDK, non-``None`` ``retry_write`` values, including
        ``0`` and ``False``, raise ``TypeError`` before the first read, whether
        top-level or nested in either options dictionary. Omit it or use ``None``.
        Unsupported options raise ``TypeError`` before the first request rather
        than falling back to legacy Python.
        A supported ``timeout`` is shared across reads, creation, and any GSI
        source-container read. For example, a three-second read with ``timeout=10``
        leaves at most seven seconds. A timeout does not undo creation already
        performed by the service backend.
        The response hook receives copied headers and a deep copy of properties
        from the successful step; its exceptions propagate without triggering
        creation or another create attempt.
        If creation conflicts with another caller, read the container using the
        remaining timeout. A 404/1013 response means creation is still in progress;
        only that response permits up to nine additional reads, with waits of
        100 ms growing to one second within the same timeout. Other read failures
        propagate without another create. Conditional headers are forwarded;
        the workflow is not atomic.
        A 304 existence read returns empty properties without fetching them again.
        For a successful creation response without properties, the hook receives
        empty properties and creation headers, not any later properties read.

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
        :keyword Callable response_hook: A synchronous callable invoked once with response headers and properties,
            or None. Non-callable values and declared async hooks raise TypeError before any request.
        :keyword float timeout: Shared operation budget in seconds, or None for no per-call override.
            Must be finite, non-boolean, at least one, and less than 2**64.
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
            or a tuple of a ContainerProxy and the container properties. If creation returns no properties,
            False needs no extra read; True reads properties with the remaining timeout, without the create condition.
            Those properties describe the later read, not a guaranteed creation-time snapshot.
            A failed properties read propagates without another create attempt.
        :returns: A `ContainerProxy` for the existing or newly created container, or a tuple of that client
            and a CosmosDict with the container properties.
        :raises TypeError: Required arguments, options, or the response hook are unsupported.
        :raises ValueError: The timeout value is invalid.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: The shared operation timeout expired.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy or tuple[ ~azure.cosmos.ContainerProxy,  ~azure.cosmos.CosmosDict]
        """
        prepare_operation_kwargs(self, kwargs)

        id, partition_key = parse_container_create_args(
            args, kwargs, method_name="create_container_if_not_exists"
        )
        validate_obsolete_resource_options(kwargs, "create_container_if_not_exists")
        if get_selected_backend(self.client_connection).name == "rust":
            validate_container_retry_write_kwargs(kwargs, "create_container_if_not_exists")
        create_options = {
            option: kwargs.pop(option, None)
            for option in (
                "indexing_policy", "default_ttl", "unique_key_policy", "conflict_resolution_policy",
                "analytical_storage_ttl", "computed_properties", "vector_embedding_policy",
                "change_feed_policy", "full_text_policy", "global_secondary_index",
            )
        }
        offer_throughput = kwargs.pop('offer_throughput', None)
        initial_headers = kwargs.pop('initial_headers', None)
        return_properties = kwargs.pop('return_properties', False)

        response_hook = kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_container_if_not_exists response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "create_container_if_not_exists")
        if initial_headers is not None:
            kwargs["initial_headers"] = initial_headers
        read_options, read_kwargs, rust_eligible, deadline = prepare_container_get_or_create_read(
            kwargs, initial_headers=initial_headers, offer_throughput=offer_throughput
        )
        container_proxy = self.get_container_client(id)

        def read_container() -> CosmosDict:
            return ContainerHelper(
                self.client_connection, get_selected_backend(self.client_connection)
            ).read_container(
                container_proxy.container_link,
                read_options,
                kwargs=read_kwargs,
                routing=OperationRouting(
                    "read_container",
                    rust_eligible,
                    capability="create_container_if_not_exists",
                ),
                deadline=deadline,
            )

        try:
            properties = read_container()
        except CosmosResourceNotFoundError:
            remaining_timeout(deadline)
            create_succeeded = False

            def on_created(headers: Mapping[str, Any], body: CosmosDict) -> None:
                nonlocal create_succeeded
                create_succeeded = True
                if response_hook is not None:
                    response_hook(headers, body)

            try:
                with delegate_operation(self, "create_container"):
                    return self.create_container(
                        id=id,
                        partition_key=partition_key,
                        offer_throughput=offer_throughput,
                        return_properties=return_properties,
                        response_hook=on_created,
                        _item_operation_deadline=deadline,
                        **create_options,
                        **kwargs
                    )
            except CosmosResourceExistsError:
                # A conflict raised by the customer's success hook is not a service race.
                if create_succeeded:
                    raise
                retry_count = 0
                while True:
                    try:
                        properties = read_container()
                        break
                    except CosmosResourceNotFoundError as error:
                        delay = container_creation_retry_delay(error, retry_count, deadline)
                        if delay is None:
                            raise
                        time.sleep(delay)
                        retry_count += 1
        _normalize_gsi_container_properties(properties)
        on_response = with_response_header_snapshot(response_hook, copy_body=True)
        if on_response is not None:
            on_response(properties.get_response_headers(), properties)
        self.client_connection._set_container_properties_cache(
            container_proxy.container_link, _build_properties_cache(properties, container_proxy.container_link)
        )
        if not return_properties:
            return container_proxy
        return container_proxy, properties

    @trace_operation(binding_operation="delete_container")
    def delete_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        *,
        initial_headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """Delete a container and its contents, returning ``None`` on success.

        A missing container raises ``CosmosResourceNotFoundError``. Only the
        container may be positional. ``session_token`` and ``populate_query_metrics``
        are rejected, including their ``sessionToken`` and ``populateQueryMetrics``
        entries in ``request_options`` or ``feed_options``.
        Unsupported Rust settings raise ``TypeError`` without legacy fallback.
        On Rust, omit ``retry_write`` or pass ``None``; other values are rejected
        at the top level and in either options dictionary because this API
        cannot override the SDK's write-retry behavior.

        Non-callable and declared async response hooks are rejected before a
        request. A valid hook runs once after success with copied headers and
        ``None`` as the body. Its exceptions propagate without repeating deletion.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`~azure.cosmos.ContainerProxy` instance or
            a mapping of container properties containing ``id``.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, Mapping[str, Any]]
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword float timeout: Operation timeout in seconds. On Rust, one budget covers any
            required container lookup and deletion. Accepts None or finite, non-boolean numeric
            seconds greater than or equal to one and less than 2**64. Expiry does not undo deletion.
        :keyword response_hook: A synchronous callable invoked with copied response headers and None.
        :paramtype response_hook: Callable[[Mapping[str, str], None], None]
        :raises TypeError: An argument or response hook is unsupported.
        :raises ValueError: The timeout or ETag condition is invalid.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: The operation's timeout expires.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the container couldn't be deleted.
        :rtype: None
        """
        prepare_operation_kwargs(self, kwargs, headers=initial_headers)
        validate_obsolete_resource_options(kwargs, "delete_container")
        if get_selected_backend(self.client_connection).name == "rust":
            validate_container_retry_write_kwargs(kwargs, "delete_container")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        response_hook = kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("delete_container response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "delete_container")
        request_options = build_options(kwargs)
        kwargs.pop("etag", None)
        collection_link = self._get_container_link(container)
        ContainerHelper(self.client_connection, get_selected_backend(self.client_connection)).delete_container(
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
        return ContainerProxy(
            self.client_connection, self.database_link, id_value,
            _client_context=self._client_context, _inference_client=self._inference_client,
        )

    def _resolve_gsi_definition(
        self,
        global_secondary_index: Union["GlobalSecondaryIndexDefinition", dict[str, Any]],
        *,
        deadline: Optional[float] = None,
    ) -> dict[str, Any]:
        """Serialize a GSI definition and populate the source container's resource id (_rid).

        The service resolves the source container by its resource id (``sourceCollectionRid``).
        When the caller only provides the source container id, read the source container to
        obtain its ``_rid`` and populate ``sourceCollectionRid`` on the wire payload.

        :param global_secondary_index: The GSI definition object or raw dict.
        :type global_secondary_index:
            ~azure.cosmos.GlobalSecondaryIndexDefinition or dict[str, Any]
        :keyword float deadline: Shared operation deadline, if any.
        :returns: The serialized GSI definition including ``sourceCollectionRid``.
        :rtype: dict[str, Any]
        """
        gsi_dict = (global_secondary_index._to_dict()  # pylint: disable=protected-access
                    if hasattr(global_secondary_index, '_to_dict')
                    else dict(global_secondary_index))
        if not gsi_dict.get("sourceCollectionRid"):
            source_container_id = gsi_dict.get("sourceCollectionId")
            if source_container_id:
                source = self.get_container_client(source_container_id)
                source_properties = (
                    source.read() if deadline is None else source.read(_item_operation_deadline=deadline)
                )
                gsi_dict["sourceCollectionRid"] = source_properties["_rid"]
        return gsi_dict

    @distributed_trace
    def list_containers(  # pylint:disable=docstring-missing-param
        self,
        *,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List the containers in the database.

        :keyword int max_item_count: Maximum number of containers requested per page, not a total result limit.
        :keyword float timeout: Timeout budget in seconds per page fetch by default, not for draining
            the whole iterator. Rust supports finite numeric durations of at least one second
            within its duration range; ``None`` leaves the override unset.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A synchronous callable invoked after each successfully fetched page,
            with that page's response headers and the same results iterator returned by this method.
            It is not called before iteration. Consume results outside the hook; the iterator is
            already being advanced when the hook runs.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]

        All settings are keyword-only. ``session_token``, ``populate_query_metrics``,
        and ``availability_strategy`` are rejected, including explicit ``None`` or ``False``.
        Supplying these options inside ``request_options`` or ``feed_options`` also raises
        ``TypeError`` when constructing the pager, whether using the names above or their
        aliases ``sessionToken``, ``populateQueryMetrics``, and ``availabilityStrategy``.
        For example, remove ``request_options={"sessionToken": None}`` rather than
        passing an unset session token.
        When constructing the pager, invalid page sizes or timeouts raise ``ValueError``,
        and non-callable or asynchronous hooks raise ``TypeError``. Use a synchronous
        ``def`` function for the hook. Page size must be ``None``, ``-1``, or a positive
        integer below ``2**63``; booleans are not accepted.
        Unsupported Rust page options raise during iteration instead of using legacy Python.

        Each page iterator owns its continuation token. Another operation, including
        one called by the response hook, cannot change that bookmark. A final empty
        page clears it. Empty service pages share the current page-fetch deadline.
        After a failed fetch or hook, resume a new pager from the last fully processed
        page's bookmark. Hook iteration-stop exceptions become ``RuntimeError``;
        other hook failures propagate without replaying the request.

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
        """
        prepare_operation_kwargs(self, kwargs, headers=initial_headers)
        for option in ("session_token", "populate_query_metrics", "availability_strategy"):
            if option in kwargs:
                raise TypeError(f"list_containers() does not support the '{option}' keyword argument")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if max_item_count is not None:
            kwargs["max_item_count"] = max_item_count
        kwargs["response_hook"] = response_hook
        return _list_containers(self, kwargs)

    @distributed_trace
    def query_containers(   # pylint:disable=docstring-missing-param
        self,
        query: Optional[Union[str, dict[str, Any]]],
        *,
        parameters: Optional[list[dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[Any]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[Any]:
        """Query container properties in the current database, not the items inside them.

        ``SELECT * FROM c`` returns container property dictionaries.
        ``SELECT VALUE c.id FROM c`` returns ID strings such as ``"orders"``.

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
            with that page's response headers and the same results iterator returned by this method.
            It is not called before iteration. Consume results outside the hook; the iterator is
            already being advanced when the hook runs.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[Any]], None]
        :returns: A paged iterable of values selected by the query, including dictionaries or scalars.
        :rtype: ItemPaged[Any]

        ``query`` is required; all other settings are keyword-only. Use ``list_containers()``
        for an unfiltered inventory. ``session_token``, ``populate_query_metrics``,
        ``availability_strategy``, and ``enable_cross_partition_query`` raise ``TypeError``
        when constructing the pager, including explicit ``None`` or ``False``.
        The same rejection applies inside ``request_options`` and ``feed_options``,
        including the aliases ``sessionToken``, ``populateQueryMetrics``,
        ``availabilityStrategy``, and ``enableCrossPartitionQuery``. Both dictionaries
        are checked even when one overrides the other. For example,
        ``request_options={"sessionToken": None}`` is rejected before any request.
        A ``connection_timeout`` or reserved-header override raises ``TypeError``
        during iteration, before sending a request. The SDK never switches to legacy Python.

        Settings are copied at construction, but query dictionaries and parameters remain
        live until each page fetch. For example, changing a parameter from ``"orders"`` to
        ``"receipts"`` before iteration queries ``"receipts"``. Later edits are validated
        before sending the next page request. At construction, empty query text, malformed
        parameters, invalid page sizes, and invalid timeouts raise ``ValueError``;
        non-callable hooks, coroutine hooks, and async-generator hooks raise ``TypeError``.
        Page size must be ``None``,
        ``-1``, or a positive integer below ``2**63``; booleans are not accepted.
        Requests still begin only when the results are consumed. Each page iterator owns
        its bookmark; other operations cannot overwrite it. A final empty page clears
        the bookmark. After a failed fetch or hook, resume a new pager from the last
        fully processed page's bookmark. Hook iteration-stop exceptions become
        ``RuntimeError``; other hook failures propagate without replaying the request.
        """
        prepare_operation_kwargs(self, kwargs, headers=initial_headers)
        for option in ("session_token", "populate_query_metrics", "availability_strategy",
                       "enable_cross_partition_query"):
            if option in kwargs:
                raise TypeError(f"query_containers() does not support the '{option}' keyword argument")
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if max_item_count is not None:
            kwargs["max_item_count"] = max_item_count
        kwargs["response_hook"] = response_hook
        return _query_containers(self, query, parameters, kwargs)

    @overload
    def replace_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, "azure.cosmos.ContainerProxy", Mapping[str, Any]],
        partition_key: "azure.cosmos.PartitionKey",
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
    ) -> "azure.cosmos.ContainerProxy":
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

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
            container: Union[str, "azure.cosmos.ContainerProxy", Mapping[str, Any]],
            partition_key: "azure.cosmos.PartitionKey",
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
    ) -> tuple["azure.cosmos.ContainerProxy", CosmosDict]:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

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

    @trace_operation(binding_operation="replace_container")
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
        are rejected even when set to ``None`` or ``False``.
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
        prepare_operation_kwargs(self, kwargs)

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
            self.client_connection, get_selected_backend(self.client_connection),
        ).replace_container(
            container_link, parameters, request_options, response_hook=response_hook, kwargs=kwargs,
        )
        _normalize_gsi_container_properties(container_properties)

        if not return_properties:
            return ContainerProxy(
                self.client_connection,
                self.database_link, container_properties["id"],
                properties=container_properties, _client_context=self._client_context,
                _inference_client=self._inference_client)
        return ContainerProxy(
            self.client_connection,
            self.database_link, container_properties["id"],
            properties=container_properties, _client_context=self._client_context,
            _inference_client=self._inference_client), container_properties

    @trace_operation(binding_operation=BindingAlternatives((("read_database", "get_throughput"), ("get_throughput",))))
    def get_throughput(
            self,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = None,
            **kwargs: Any) -> ThroughputProperties:
        """Read the manual or autoscale throughput shared by this database.

        The Rust path does not fall back to legacy Python. A single timeout
        budget covers uncached database properties and the complete offer query.

        :keyword response_hook: Called once after success with copied response
            headers and a list of offer dictionaries. Mutations do not change the result.
        :paramtype response_hook: Callable[[Mapping[str, Any], list[dict[str, Any]]], None]
        :keyword float timeout: Overall operation budget in seconds, including
            metadata and all offer pages. None inherits the client default.
            Rust requires a finite duration of at least one second.
        :returns: The database's configured manual or autoscale throughput.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError:
            The database does not exist or has no shared throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The throughput could not be retrieved.
        :raises NotImplementedError: An input cannot be honored on the Rust path.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        prepare_operation_kwargs(self, kwargs)

        def get_properties(*, deadline: Optional[float] = None) -> dict[str, Any]:
            with delegate_operation(self, "read"):
                return self._get_properties() if deadline is None else self._get_properties(deadline=deadline)

        return get_database_throughput(
            client_connection=self.client_connection,
            database_link=self.database_link,
            get_properties=get_properties,
            not_found_message="Could not find ThroughputProperties for database " + self.database_link,
            response_hook=response_hook,
            kwargs=kwargs,
        )

    @trace_operation(
        binding_operation=BindingAlternatives(
            (
                ("read_database", "get_throughput", "replace_throughput"),
                ("get_throughput", "replace_throughput"),
            )
        )
    )
    def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the manual or autoscale throughput shared by this database.

        One operation budget covers metadata, offer lookup and replacement.

        :param throughput: Manual RU/s as an integer, or manual/autoscale settings.
        :type throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the database, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If no throughput properties exists for the database or if the throughput properties could not be updated.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        prepare_operation_kwargs(self, kwargs)

        def get_properties(*, deadline: Optional[float] = None) -> dict[str, Any]:
            with delegate_operation(self, "read"):
                return self._get_properties() if deadline is None else self._get_properties(deadline=deadline)

        return replace_database_throughput(
            client_connection=self.client_connection,
            database_link=self.database_link,
            get_properties=get_properties,
            throughput=throughput,
            not_found_message="Could not find ThroughputProperties for database " + self.database_link,
            response_hook=kwargs.pop("response_hook", None),
            kwargs=kwargs,
        )
