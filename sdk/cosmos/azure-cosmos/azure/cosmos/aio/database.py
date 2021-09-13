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

from typing import Any, List, Dict, Union, cast, Iterable, Optional

import warnings
import six
from azure.core.tracing.decorator_async import distributed_trace_async  # type: ignore

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options
from .container import ContainerProxy
from ..offer import Offer
from ..http_constants import StatusCodes
from ..exceptions import CosmosResourceNotFoundError
from ..user import UserProxy
from ..documents import IndexingMode

__all__ = ("DatabaseProxy",)

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

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

    def __init__(self, client_connection, id, properties=None):  # pylint: disable=redefined-builtin
        # type: (CosmosClientConnection, str, Dict[str, Any]) -> None
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self.id = id
        self.database_link = u"dbs/{}".format(self.id)
        self._properties = properties

    def __repr__(self):
        # type () -> str
        return "<DatabaseProxy [{}]>".format(self.database_link)[:1024]

    @staticmethod
    def _get_container_id(container_or_id):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> str
        if isinstance(container_or_id, six.string_types):
            return container_or_id
        try:
            return cast("ContainerProxy", container_or_id).id
        except AttributeError:
            pass
        return cast("Dict[str, str]", container_or_id)["id"]

    def _get_container_link(self, container_or_id):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> str
        return u"{}/colls/{}".format(self.database_link, self._get_container_id(container_or_id))

    @distributed_trace_async
    async def create_container(
        self,
        id,  # type: str  # pylint: disable=redefined-builtin
        partition_key,  # type: Any
        indexing_policy=None,  # type: Optional[Dict[str, Any]]
        default_ttl=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        offer_throughput=None,  # type: Optional[int]
        unique_key_policy=None,  # type: Optional[Dict[str, Any]]
        conflict_resolution_policy=None,  # type: Optional[Dict[str, Any]]
        **kwargs  # type: Any
    ):
        # type: (...) -> ContainerProxy
        """Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.
        :param unique_key_policy: The unique key policy to apply to the container.
        :param conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL. Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
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
                :name: create_container

            .. literalinclude:: ../samples/examples.py
                :start-after: [START create_container_with_settings]
                :end-before: [END create_container_with_settings]
                :language: python
                :dedent: 0
                :caption: Create a container with specific settings; in this case, a custom partition key:
                :name: create_container_with_settings
        """
        definition = dict(id=id)  # type: Dict[str, Any]
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

        analytical_storage_ttl = kwargs.pop("analytical_storage_ttl", None)
        if analytical_storage_ttl is not None:
            definition["analyticalStorageTtl"] = analytical_storage_ttl

        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if offer_throughput is not None:
            request_options["offerThroughput"] = offer_throughput

        data = await self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)

        return ContainerProxy(self.client_connection, self.database_link, data["id"], properties=data)

    @distributed_trace_async
    async def create_container_if_not_exists(
        self,
        id,  # type: str  # pylint: disable=redefined-builtin
        partition_key,  # type: Any
        indexing_policy=None,  # type: Optional[Dict[str, Any]]
        default_ttl=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        offer_throughput=None,  # type: Optional[int]
        unique_key_policy=None,  # type: Optional[Dict[str, Any]]
        conflict_resolution_policy=None,  # type: Optional[Dict[str, Any]]
        **kwargs  # type: Any
    ):
        # type: (...) -> ContainerProxy
        """Create a container if it does not exist already.

        If the container already exists, the existing settings are returned.
        Note: it does not check or update the existing container settings or offer throughput
        if they differ from what was passed into the method.

        :param id: ID (name) of container to read or create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.
        :param unique_key_policy: The unique key policy to apply to the container.
        :param conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword analytical_storage_ttl: Analytical store time to live (TTL) for items in the container.  A value of
            None leaves analytical storage off and a value of -1 turns analytical storage on with no TTL.  Please
            note that analytical storage can only be enabled on Synapse Link enabled accounts.
        :returns: A `ContainerProxy` instance representing the container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The container read or creation failed.
        :rtype: ~azure.cosmos.ContainerProxy
        """

        analytical_storage_ttl = kwargs.pop("analytical_storage_ttl", None)
        try:
            container_proxy = self.get_container_client(id)
            await container_proxy.read(
                populate_query_metrics=populate_query_metrics,
                **kwargs
            )
            return container_proxy
        except CosmosResourceNotFoundError:
            return await self.create_container(
                id=id,
                partition_key=partition_key,
                indexing_policy=indexing_policy,
                default_ttl=default_ttl,
                populate_query_metrics=populate_query_metrics,
                offer_throughput=offer_throughput,
                unique_key_policy=unique_key_policy,
                conflict_resolution_policy=conflict_resolution_policy,
                analytical_storage_ttl=analytical_storage_ttl
            )

    @distributed_trace_async
    async def read(self, populate_query_metrics=None, **kwargs):
        # type: (Optional[bool], Any) -> Dict[str, Any]
        """Read the database properties.

        :param bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :rtype: Dict[Str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given database couldn't be retrieved.
        """
        # TODO this helper function should be extracted from CosmosClient
        from .cosmos_client import CosmosClient

        database_link = CosmosClient._get_database_link(self)
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._properties = await self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    def get_container_client(self, container):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> ContainerProxy
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`ContainerProxy` instance,
            or a dict representing the properties of the container to be retrieved.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START get_container]
                :end-before: [END get_container]
                :language: python
                :dedent: 0
                :caption: Get an existing container, handling a failure if encountered:
                :name: get_container
        """
        if isinstance(container, ContainerProxy):
            id_value = container.id
        else:
            try:
                id_value = container["id"]
            except TypeError:
                id_value = container

        return ContainerProxy(self.client_connection, self.database_link, id_value)

    @distributed_trace_async
    async def delete_container(
        self,
        container,  # type: Union[str, ContainerProxy, Dict[str, Any]]
        populate_query_metrics=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a container.

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`ContainerProxy` instance or
            a dict representing the properties of the container.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the container couldn't be deleted.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        result = await self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)