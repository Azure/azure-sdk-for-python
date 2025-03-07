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

from typing import Any, Dict, List, Union, Optional, Mapping, Callable

import warnings
from azure.core import MatchConditions
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
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self.id = id
        self.database_link: str = "dbs/{}".format(self.id)
        self._properties: Optional[Dict[str, Any]] = properties

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

    def _get_properties(self) -> Dict[str, Any]:
        if self._properties is None:
            self._properties = self.read()
        return self._properties

    @distributed_trace
    def read(  # pylint:disable=docstring-missing-param
        self,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read the database properties.

        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the database properties.
        :rtype: Dict[Str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        database_link = _get_database_link(self)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._properties = self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )
        return self._properties

    @distributed_trace
    def create_container(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        partition_key: PartitionKey,
        indexing_policy: Optional[Dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        unique_key_policy: Optional[Dict[str, Any]] = None,
        conflict_resolution_policy: Optional[Dict[str, Any]] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        computed_properties: Optional[List[Dict[str, str]]] = None,
        vector_embedding_policy: Optional[Dict[str, Any]] = None,
        change_feed_policy: Optional[Dict[str, Any]] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param Dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param Dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param Dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword List[Dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Dict[str, Any] vector_embedding_policy: The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function.
        :keyword Dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :returns: A `ContainerProxy` instance representing the new container.
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
        definition: Dict[str, Any] = {"id": id}
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

        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        request_options = build_options(kwargs)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        _set_throughput_options(offer=offer_throughput, request_options=request_options)
        result = self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )

        return ContainerProxy(self.client_connection, self.database_link, result["id"], properties=result)

    @distributed_trace
    def create_container_if_not_exists(  # pylint:disable=docstring-missing-param
        self,
        id: str,
        partition_key: PartitionKey,
        indexing_policy: Optional[Dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        unique_key_policy: Optional[Dict[str, Any]] = None,
        conflict_resolution_policy: Optional[Dict[str, Any]] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        computed_properties: Optional[List[Dict[str, str]]] = None,
        vector_embedding_policy: Optional[Dict[str, Any]] = None,
        change_feed_policy: Optional[Dict[str, Any]] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param str id: ID (name) of container to create.
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param Dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container. If unused, items do not expire.
        :param offer_throughput: The provisioned throughput for this offer.
        :type offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :param Dict[str, Any] unique_key_policy: The unique key policy to apply to the container.
        :param Dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword List[Dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Dict[str, Any] vector_embedding_policy: The vector embedding policy for the container. Each vector
            embedding possesses a predetermined number of dimensions, is associated with an underlying data type, and
            is generated for a particular distance function.
        :keyword Dict[str, Any] change_feed_policy: The change feed policy to apply 'retentionDuration' to
            the container.
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :returns: A `ContainerProxy` instance representing the container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy
        """
        try:
            container_proxy = self.get_container_client(id)
            container_proxy.read(
                populate_query_metrics=populate_query_metrics,
                session_token=session_token,
                initial_headers=initial_headers,
                **kwargs
            )
            return container_proxy
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
                etag=etag,
                match_condition=match_condition,
                session_token=session_token,
                initial_headers=initial_headers,
                vector_embedding_policy=vector_embedding_policy,
                change_feed_policy=change_feed_policy,
                full_text_policy=full_text_policy,
                **kwargs
            )

    @distributed_trace
    def delete_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        """Delete a container.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`~azure.cosmos.ContainerProxy` instance or
            a dict representing the properties of the container.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, Dict[str, Any]]
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the container couldn't be deleted.
        :rtype: None
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        request_options = build_options(kwargs)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)

    def get_container_client(self, container: Union[str, ContainerProxy, Mapping[str, Any]]) -> ContainerProxy:
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`~azure.cosmos.ContainerProxy` instance,
            or a dict representing the properties of the container to be retrieved.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, Dict[str, Any]]
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
        return ContainerProxy(self.client_connection, self.database_link, id_value)

    @distributed_trace
    def list_containers(  # pylint:disable=docstring-missing-param
        self,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List the containers in the database.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[Dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            feed_options["populateQueryMetrics"] = populate_query_metrics

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
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List the properties for containers in the current database.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, Any]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            feed_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.QueryContainers(
            database_link=self.database_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def replace_container(  # pylint:disable=docstring-missing-param
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        partition_key: PartitionKey,
        indexing_policy: Optional[Dict[str, Any]] = None,
        default_ttl: Optional[int] = None,
        conflict_resolution_policy: Optional[Dict[str, Any]] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        computed_properties: Optional[List[Dict[str, str]]] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`~azure.cosmos.ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, ~azure.cosmos.ContainerProxy, Dict[str, Any]]
        :param ~azure.cosmos.PartitionKey partition_key: The partition key to use for the container.
        :param Dict[str, Any] indexing_policy: The indexing policy to apply to the container.
        :param int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :param Dict[str, Any] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword List[Dict[str, str]] computed_properties: Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :returns: A `ContainerProxy` instance representing the container after replace completed.
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
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        request_options = build_options(kwargs)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

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
            }.items()
            if value is not None
        }

        container_properties = self.client_connection.ReplaceContainer(
            container_link, collection=parameters, options=request_options, **kwargs)

        return ContainerProxy(
            self.client_connection, self.database_link, container_properties["id"], properties=container_properties)

    @distributed_trace
    def list_users(
            self,
            max_item_count: Optional[int] = None,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List all the users in the container.

        :param int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[Dict[str, Any]]
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
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return all users matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, Any]]
        :param int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[Dict[str, Any]]], None]
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[Dict[str, Any]]
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
        :type user: Union[str, ~azure.cosmos.UserProxy, Dict[str, Any]]
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
    def create_user(self, body: Dict[str, Any], **kwargs: Any) -> UserProxy:
        """Create a new user in the container.

        To update or replace an existing user, use the
        :func:`ContainerProxy.upsert_user` method.

        :param Dict[str, Any] body: A dict-like object with an `id` key and value representing the user to be created.
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
    def upsert_user(self, body: Dict[str, Any], **kwargs: Any) -> UserProxy:
        """Insert or update the specified user.

        If the user already exists in the container, it is replaced. If the user
        does not already exist, it is inserted.

        :param Dict[str, Any] body: A dict-like object representing the user to update or insert.
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
            body: Dict[str, Any],
            **kwargs: Any
    ) -> UserProxy:
        """Replaces the specified user if it exists in the container.

        :param user: The ID (name), dict representing the properties or :class:`~azure.cosmos.UserProxy`
            instance of the user to be replaced.
        :type user: Union[str, ~azure.cosmos.UserProxy, Dict[str, Any]]
        :param Dict[str, Any] body: A dict-like object representing the user to replace.
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
        :type user: Union[str, ~azure.cosmos.UserProxy, Dict[str, Any]]
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
            response_hook: Optional[Callable[[Mapping[str, Any], List[Dict[str, Any]]], None]] = None,
            **kwargs: Any) -> ThroughputProperties:
        """Get the ThroughputProperties object for this database.

        If no ThroughputProperties already exist for the database, an exception is raised.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], List[Dict[str, Any]]], None]
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
