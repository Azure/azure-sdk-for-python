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

"""Interact with databases in the Azure Cosmos DB SQL API service.
"""

from typing import Any, Dict, List, Mapping, Optional, Union

import warnings
from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options as _build_options, _set_throughput_options, _deserialize_throughput, \
    _replace_throughput
from ._container import ContainerProxy
from ..offer import ThroughputProperties
from ..http_constants import StatusCodes
from ..exceptions import CosmosResourceNotFoundError
from ._user import UserProxy
from ..documents import IndexingMode
from ..partition_key import PartitionKey

__all__ = ("DatabaseProxy",)


# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

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
    :func:`~azure.cosmos.aio.CosmosClient.get_database_client` method to get an existing
    database, or the :func:`~azure.cosmos.aio.CosmosClient.create_database` method to create
    a new database.

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
        :param client_connection: Client from which this database was retrieved.
        :type client_connection: ~azure.cosmos.aio.CosmosClientConnection
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self.id = id
        self.database_link = "dbs/{}".format(self.id)
        self._properties = properties

    def __repr__(self) -> str:
        return "<DatabaseProxy [{}]>".format(self.database_link)[:1024]

    def _get_container_id(self, container_or_id: Union[str, ContainerProxy, Mapping[str, Any]]) -> str:
        if isinstance(container_or_id, str):
            return container_or_id
        if isinstance(container_or_id, ContainerProxy):
            return container_or_id.id
        return str(container_or_id["id"])

    def _get_container_link(self, container_or_id: Union[str, ContainerProxy, Mapping[str, Any]]) -> str:
        return "{}/colls/{}".format(self.database_link, self._get_container_id(container_or_id))

    def _get_user_link(self, user_or_id: Union[UserProxy, str, Mapping[str, Any]]) -> str:
        if isinstance(user_or_id, str):
            return "{}/users/{}".format(self.database_link, user_or_id)
        if isinstance(user_or_id, UserProxy):
            return user_or_id.user_link
        return "{}/users/{}".format(self.database_link, user_or_id["id"])

    async def _get_properties(self) -> Dict[str, Any]:
        if self._properties is None:
            self._properties = await self.read()
        return self._properties

    @distributed_trace_async
    async def read(
        self,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read the database properties.

        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        :returns: A dict representing the database properties
        :rtype: Dict[str, Any]
        """
        database_link = _get_database_link(self)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = _build_options(kwargs)

        self._properties = await self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )

        return self._properties

    @distributed_trace_async
    async def create_container(
        self,
        id: str,
        partition_key: PartitionKey,
        *,
        indexing_policy: Optional[Dict[str, str]] = None,
        default_ttl: Optional[int] = None,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        unique_key_policy: Optional[Dict[str, str]] = None,
        conflict_resolution_policy: Optional[Dict[str, str]] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        vector_embedding_policy: Optional[Dict[str, Any]] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param str id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :type partition_key: ~azure.cosmos.PartitionKey
        :keyword dict[str, str] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, str] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, str] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword List[Dict[str, str]] computed_properties: **provisional** Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword Dict[str, Any] vector_embedding_policy: The vector embedding policy for the container. Each vector
            embedding possesses a predetermined number of dimensions, is associated with an underlying data type, and
            is generated for a particular distance function.
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container creation failed.
        :returns: A `ContainerProxy` instance representing the new container.
        :rtype: ~azure.cosmos.aio.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START create_container]
                :end-before: [END create_container]
                :language: python
                :dedent: 0
                :caption: Create a container with default settings:
                :name: create_container

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START create_container_with_settings]
                :end-before: [END create_container_with_settings]
                :language: python
                :dedent: 0
                :caption: Create a container with specific settings; in this case, a custom partition key:
                :name: create_container_with_settings
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
        computed_properties = kwargs.pop('computed_properties', None)
        if computed_properties is not None:
            definition["computedProperties"] = computed_properties
        if vector_embedding_policy is not None:
            definition["vectorEmbeddingPolicy"] = vector_embedding_policy
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
        request_options = _build_options(kwargs)
        _set_throughput_options(offer=offer_throughput, request_options=request_options)

        data = await self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )
        return ContainerProxy(self.client_connection, self.database_link, data["id"], properties=data)

    @distributed_trace_async
    async def create_container_if_not_exists(
        self,
        id: str,
        partition_key: PartitionKey,
        *,
        indexing_policy: Optional[Dict[str, str]] = None,
        default_ttl: Optional[int] = None,
        offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
        unique_key_policy: Optional[Dict[str, str]] = None,
        conflict_resolution_policy: Optional[Dict[str, str]] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        vector_embedding_policy: Optional[Dict[str, Any]] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param str id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :type partition_key: ~azure.cosmos.PartitionKey
        :keyword dict[str, str] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :keyword offer_throughput: The provisioned throughput for this offer.
        :paramtype offer_throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword dict[str, str] unique_key_policy: The unique key policy to apply to the container.
        :keyword dict[str, str] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword List[Dict[str, str]] computed_properties: **provisional** Sets The computed properties for this
            container in the Azure Cosmos DB Service. For more Information on how to use computed properties visit
            `here: https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/query/computed-properties?tabs=dotnet`
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword Dict[str, Any] vector_embedding_policy: **provisional** The vector embedding policy for the container.
            Each vector embedding possesses a predetermined number of dimensions, is associated with an underlying
            data type, and is generated for a particular distance function.
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container creation failed.
        :returns: A `ContainerProxy` instance representing the new container.
        :rtype: ~azure.cosmos.aio.ContainerProxy
        """
        computed_properties = kwargs.pop("computed_properties", None)
        try:
            container_proxy = self.get_container_client(id)
            await container_proxy.read(
                session_token=session_token,
                initial_headers=initial_headers,
                **kwargs
            )
            return container_proxy
        except CosmosResourceNotFoundError:
            return await self.create_container(
                id=id,
                partition_key=partition_key,
                indexing_policy=indexing_policy,
                default_ttl=default_ttl,
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
                full_text_policy=full_text_policy,
                **kwargs
            )

    def get_container_client(self, container: Union[str, ContainerProxy, Dict[str, Any]]) -> ContainerProxy:
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name), dict representing the properties, or :class:`ContainerProxy`
            instance of the container to get.
        :type container: Union[str, Dict[str, Any], ~azure.cosmos.aio.ContainerProxy]
        :returns: A `ContainerProxy` instance representing the container.
        :rtype: ~azure.cosmos.aio.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START get_container]
                :end-before: [END get_container]
                :language: python
                :dedent: 0
                :caption: Get an existing container, handling a failure if encountered:
                :name: get_container
        """
        if isinstance(container, str):
            id_value = container
        elif isinstance(container, ContainerProxy):
            id_value = container.id
        else:
            id_value = str(container['id'])
        return ContainerProxy(self.client_connection, self.database_link, id_value)

    @distributed_trace
    def list_containers(
        self,
        *,
        session_token: Optional[str] = None,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List the containers in the database.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of container properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
                :name: list_containers
        """
        response_hook = kwargs.pop('response_hook', None)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadContainers(
            database_link=self.database_link, options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_containers(
        self,
        query: str,
        *,
        parameters: Optional[List[Dict[str, Any]]] = None,
        session_token: Optional[str] = None,
        max_item_count: Optional[int] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List the properties for containers in the current database.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
        :paramtype parameters: Optional[List[Dict[str, Any]]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of container properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        response_hook = kwargs.pop('response_hook', None)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryContainers(
            database_link=self.database_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def replace_container(
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        partition_key: PartitionKey,
        *,
        indexing_policy: Optional[Dict[str, str]] = None,
        default_ttl: Optional[int] = None,
        conflict_resolution_policy: Optional[Dict[str, str]] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        analytical_storage_ttl: Optional[int] = None,
        full_text_policy: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> ContainerProxy:
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`ContainerProxy` instance of the container to be replaced.
        :type container: Union[str, Dict[str, Any], ~azure.cosmos.aio.ContainerProxy]
        :param partition_key: The partition key to use for the container.
        :type partition_key: ~azure.cosmos.PartitionKey
        :keyword dict[str, str] indexing_policy: The indexing policy to apply to the container.
        :keyword int default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :keyword dict[str, str] conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :keyword Dict[str, Any] full_text_policy: **provisional** The full text policy for the container.
            Used to denote the default language to be used for all full text indexes, or to individually
            assign a language to each full text index path.
        :returns: A `ContainerProxy` instance representing the container after replace completed.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be replaced.
            This includes if the container with given id does not exist.
        :rtype: ~azure.cosmos.aio.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START reset_container_properties]
                :end-before: [END reset_container_properties]
                :language: python
                :dedent: 0
                :caption: Reset the TTL property on a container, and display the updated properties:
                :name: reset_container_properties
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        request_options = _build_options(kwargs)

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
                "fullTextPolicy": full_text_policy
            }.items()
            if value is not None
        }

        container_properties = await self.client_connection.ReplaceContainer(
            container_link, collection=parameters, options=request_options, **kwargs
        )
        return ContainerProxy(
            self.client_connection, self.database_link, container_properties["id"], properties=container_properties
        )

    @distributed_trace_async
    async def delete_container(
        self,
        container: Union[str, ContainerProxy, Mapping[str, Any]],
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        """Delete a container.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`ContainerProxy` instance or
            a dict representing the properties of the container.
        :type container: str or Dict[str, Any] or ~azure.cosmos.aio.ContainerProxy
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
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
        request_options = _build_options(kwargs)

        collection_link = self._get_container_link(container)
        await self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)

    @distributed_trace_async
    async def create_user(
        self,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> UserProxy:  # body should just be id?
        """Create a new user in the container.

        To update or replace an existing user, use the
        :func:`ContainerProxy.upsert_user` method.

        :param Dict[str, Any] body: A dict object with an `id` key and value representing the user to be created.
            The user ID must be unique within the database, and consist of no more than 255 characters.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user couldn't be created.
        :returns: A `UserProxy` instance representing the new user.
        :rtype: ~azure.cosmos.aio.UserProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START create_user]
                :end-before: [END create_user]
                :language: python
                :dedent: 0
                :caption: Create a database user:
                :name: create_user
        """
        request_options = _build_options(kwargs)

        user = await self.client_connection.CreateUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs)

        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    def get_user_client(
        self,
        user: Union[str, UserProxy, Mapping[str, Any]]
    ) -> UserProxy:
        """Get a `UserProxy` for a user with specified ID.

        :param user: The ID (name), dict representing the properties, or :class:`UserProxy`
            instance of the user to get.
        :type user: Union[str, Dict[str, Any], ~azure.cosmos.aio.UserProxy]
        :returns: A `UserProxy` instance representing the retrieved user.
        :rtype: ~azure.cosmos.aio.UserProxy
        """
        if isinstance(user, str):
            id_value = user
        elif isinstance(user, UserProxy):
            id_value = user.id
        else:
            id_value = str(user['id'])
        return UserProxy(client_connection=self.client_connection, id=id_value, database_link=self.database_link)

    @distributed_trace
    def list_users(
        self,
        *,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List all the users in the container.

        :keyword int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of user properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
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
        *,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all users matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :paramtype parameters: Optional[List[Dict[str, Any]]]
        :keyword int max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of user properties (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
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

    @distributed_trace_async
    async def upsert_user(
        self,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> UserProxy:
        """Insert or update the specified user.

        If the user already exists in the container, it is replaced. If the user
        does not already exist, it is inserted.

        :param Dict[str, Any] body: A dict-like object representing the user to update or insert.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user could not be upserted.
        :returns: A `UserProxy` instance representing the upserted user.
        :rtype: ~azure.cosmos.aio.UserProxy
        """
        request_options = _build_options(kwargs)

        user = await self.client_connection.UpsertUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs
        )
        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace_async
    async def replace_user(
        self,
        user: Union[str, UserProxy, Mapping[str, Any]],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> UserProxy:
        """Replaces the specified user if it exists in the container.

        :param user: The ID (name), dict representing the properties or :class:`UserProxy`
            instance of the user to be replaced.
        :type user: Union[str, Dict[str, Any], ~azure.cosmos.aio.UserProxy]
        :param Dict[str, Any] body: A dict object representing the user to replace.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If the replace operation failed or the user with given ID does not exist.
        :returns: A `UserProxy` instance representing the user after replace went through.
        :rtype: ~azure.cosmos.aio.UserProxy
        """
        request_options = _build_options(kwargs)

        replaced_user = await self.client_connection.ReplaceUser(
            user_link=self._get_user_link(user), user=body, options=request_options, **kwargs)

        return UserProxy(
            client_connection=self.client_connection,
            id=replaced_user["id"],
            database_link=self.database_link,
            properties=replaced_user
        )

    @distributed_trace_async
    async def delete_user(
        self,
        user: Union[str, UserProxy, Mapping[str, Any]],
        **kwargs: Any
    ) -> None:
        """Delete the specified user from the container.

        :param user: The ID (name), dict representing the properties or :class:`UserProxy`
            instance of the user to be deleted.
        :type user: Union[str, Dict[str, Any], ~azure.cosmos.aio.UserProxy]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The user wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The user does not exist in the container.
        :rtype: None
        """
        request_options = _build_options(kwargs)

        await self.client_connection.DeleteUser(
            user_link=self._get_user_link(user), options=request_options, **kwargs
        )

    @distributed_trace_async
    async def get_throughput(self, **kwargs: Any) -> ThroughputProperties:
        """Get the ThroughputProperties object for this database.

        If no ThroughputProperties already exists for the database, an exception is raised.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], List[Dict[str, Any]]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the database
            or the throughput properties could not be retrieved.
        :returns: ThroughputProperties for the database.
        :rtype: ~azure.cosmos.offer.ThroughputProperties
        """
        response_hook = kwargs.pop('response_hook', None)
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, **kwargs)]
        if len(throughput_properties) == 0:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for database " + self.database_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return _deserialize_throughput(throughput=throughput_properties)

    @distributed_trace_async
    async def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the database-level throughput.

        If no ThroughputProperties already exist for the database, an exception is raised.

        :param throughput: The throughput to be set.
        :type throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the database
            or the throughput properties could not be updated.
        :returns: ThroughputProperties for the database, updated with new throughput.
        :rtype: ~azure.cosmos.offer.ThroughputProperties
        """
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, **kwargs)]
        if len(throughput_properties) == 0:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find Offer for database " + self.database_link)

        new_offer = throughput_properties[0].copy()
        _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
        data = await self.client_connection.ReplaceOffer(offer_link=throughput_properties[0]["_self"],
                                                         offer=throughput_properties[0], **kwargs)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)
