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
from azure.core.tracing.decorator import distributed_trace  # type: ignore

from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options, _stringify_auto_scale
from .container import ContainerProxy
from .offer import ThroughputProperties
from .http_constants import StatusCodes
from .exceptions import CosmosResourceNotFoundError
from .user import UserProxy
from .documents import IndexingMode

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
        if isinstance(container_or_id, str):
            return container_or_id
        try:
            return cast("ContainerProxy", container_or_id).id
        except AttributeError:
            pass
        return cast("Dict[str, str]", container_or_id)["id"]

    def _get_container_link(self, container_or_id):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> str
        return u"{}/colls/{}".format(self.database_link, self._get_container_id(container_or_id))

    def _get_user_link(self, user_or_id):
        # type: (Union[UserProxy, str, Dict[str, Any]]) -> str
        if isinstance(user_or_id, str):
            return u"{}/users/{}".format(self.database_link, user_or_id)
        try:
            return cast("UserProxy", user_or_id).user_link
        except AttributeError:
            pass
        return u"{}/users/{}".format(self.database_link, cast("Dict[str, str]", user_or_id)["id"])

    def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self._properties = self.read()
        return self._properties

    @distributed_trace
    def read(self, populate_query_metrics=None, **kwargs):
        # type: (Optional[bool], Any) -> Dict[str, Any]
        """Read the database properties.

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
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._properties = self.client_connection.ReadDatabase(
            database_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    @distributed_trace
    def create_container(
        self,
        id,  # type: str  # pylint: disable=redefined-builtin
        partition_key,  # type: Any
        indexing_policy=None,  # type: Optional[Dict[str, Any]]
        default_ttl=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        offer_throughput=None,  # type: Optional[Union[int, ThroughputProperties]]
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
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if offer_throughput is not None:
            try:
                if offer_throughput.auto_scale_max_throughput:
                    request_options['autoUpgradePolicy'] = _stringify_auto_scale(offer=offer_throughput)
                elif offer_throughput.auto_scale_increment_percent:
                    raise ValueError("auto_scale_max_throughput must be supplied in "
                                     "conjunction with auto_scale_increment_percent")
                elif offer_throughput.offer_throughput:
                    request_options["offerThroughput"] = offer_throughput.offer_throughput

            except AttributeError:
                if isinstance(offer_throughput, int):
                    request_options["offerThroughput"] = offer_throughput

        data = self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)

        return ContainerProxy(self.client_connection, self.database_link, data["id"], properties=data)

    @distributed_trace
    def create_container_if_not_exists(
        self,
        id,  # type: str  # pylint: disable=redefined-builtin
        partition_key,  # type: Any
        indexing_policy=None,  # type: Optional[Dict[str, Any]]
        default_ttl=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        offer_throughput=None,  # type: Optional[Union[int, ThroughputProperties]]
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
            container_proxy.read(
                populate_query_metrics=populate_query_metrics,
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
            )

    @distributed_trace
    def delete_container(
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
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        result = self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    def get_container_client(self, container):
        # type: (Union[str, ContainerProxy, Dict[str, Any]]) -> ContainerProxy
        """Get a `ContainerProxy` for a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`ContainerProxy` instance,
            or a dict representing the properties of the container to be retrieved.
        :returns: A `ContainerProxy` instance representing the retrieved database.
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

    @distributed_trace
    def list_containers(self, max_item_count=None, populate_query_metrics=None, **kwargs):
        # type: (Optional[int], Optional[bool], Any) -> Iterable[Dict[str, Any]]
        """List the containers in the database.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START list_containers]
                :end-before: [END list_containers]
                :language: python
                :dedent: 0
                :caption: List all containers in the database:
                :name: list_containers
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
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
    def query_containers(
        self,
        query=None,  # type: Optional[str]
        parameters=None,  # type: Optional[List[str]]
        max_item_count=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable[Dict[str, Any]]
        """List the properties for containers in the current database.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of container properties (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
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
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def replace_container(
        self,
        container,  # type: Union[str, ContainerProxy, Dict[str, Any]]
        partition_key,  # type: Any
        indexing_policy=None,  # type: Optional[Dict[str, Any]]
        default_ttl=None,  # type: Optional[int]
        conflict_resolution_policy=None,  # type: Optional[Dict[str, Any]]
        populate_query_metrics=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> ContainerProxy
        """Reset the properties of the container.

        Property changes are persisted immediately. Any properties not specified
        will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`ContainerProxy` instance of the container to be replaced.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container.
            If unspecified, items do not expire.
        :param conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be replaced.
            This includes if the container with given id does not exist.
        :returns: A `ContainerProxy` instance representing the container after replace completed.
        :rtype: ~azure.cosmos.ContainerProxy

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START reset_container_properties]
                :end-before: [END reset_container_properties]
                :language: python
                :dedent: 0
                :caption: Reset the TTL property on a container, and display the updated properties:
                :name: reset_container_properties
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
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
            }.items()
            if value is not None
        }

        container_properties = self.client_connection.ReplaceContainer(
            container_link, collection=parameters, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, container_properties)

        return ContainerProxy(
            self.client_connection, self.database_link, container_properties["id"], properties=container_properties
        )

    @distributed_trace
    def list_users(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
        """List all the users in the container.

        :param max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
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
    def query_users(self, query, parameters=None, max_item_count=None, **kwargs):
        # type: (str, Optional[List[str]], Optional[int], Any) -> Iterable[Dict[str, Any]]
        """Return all users matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of users to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of user properties (dicts).
        :rtype: Iterable[str, Any]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryUsers(
            database_link=self.database_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    def get_user_client(self, user):
        # type: (Union[str, UserProxy, Dict[str, Any]]) -> UserProxy
        """Get a `UserProxy` for a user with specified ID.

        :param user: The ID (name), dict representing the properties or :class:`UserProxy`
            instance of the user to be retrieved.
        :returns: A `UserProxy` instance representing the retrieved user.
        :rtype: ~azure.cosmos.UserProxy
        """
        if isinstance(user, UserProxy):
            id_value = user.id
        else:
            try:
                id_value = user["id"]
            except TypeError:
                id_value = user

        return UserProxy(client_connection=self.client_connection, id=id_value, database_link=self.database_link)

    @distributed_trace
    def create_user(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> UserProxy
        """Create a new user in the container.

        To update or replace an existing user, use the
        :func:`ContainerProxy.upsert_user` method.

        :param body: A dict-like object with an `id` key and value representing the user to be created.
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
                :name: create_user
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        user = self.client_connection.CreateUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, user)

        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def upsert_user(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> UserProxy
        """Insert or update the specified user.

        If the user already exists in the container, it is replaced. If the user
        does not already exist, it is inserted.

        :param body: A dict-like object representing the user to update or insert.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A `UserProxy` instance representing the upserted user.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user could not be upserted.
        :rtype: ~azure.cosmos.UserProxy
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        user = self.client_connection.UpsertUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, user)

        return UserProxy(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def replace_user(
        self,
        user,  # type: Union[str, UserProxy, Dict[str, Any]]
        body,  # type: Dict[str, Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> UserProxy
        """Replaces the specified user if it exists in the container.

        :param user: The ID (name), dict representing the properties or :class:`UserProxy`
            instance of the user to be replaced.
        :param body: A dict-like object representing the user to replace.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A `UserProxy` instance representing the user after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If the replace failed or the user with given ID does not exist.
        :rtype: ~azure.cosmos.UserProxy
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        replaced_user = self.client_connection.ReplaceUser(
            user_link=self._get_user_link(user), user=body, options=request_options, **kwargs
        )  # type: Dict[str, str]

        if response_hook:
            response_hook(self.client_connection.last_response_headers, replaced_user)

        return UserProxy(
            client_connection=self.client_connection,
            id=replaced_user["id"],
            database_link=self.database_link,
            properties=replaced_user
        )

    @distributed_trace
    def delete_user(self, user, **kwargs):
        # type: (Union[str, UserProxy, Dict[str, Any]], Any) -> None
        """Delete the specified user from the container.

        :param user: The ID (name), dict representing the properties or :class:`UserProxy`
            instance of the user to be deleted.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The user wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The user does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        result = self.client_connection.DeleteUser(
            user_link=self._get_user_link(user), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    @distributed_trace
    def read_offer(self, **kwargs):
        # type: (Any) -> ThroughputProperties
        """Get the ThroughputProperties object for this database.
        If no ThroughputProperties already exist for the database, an exception is raised.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the database.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        warnings.warn(
            "read_offer is a deprecated method name, use read_throughput instead",
            DeprecationWarning
        )
        return self.get_throughput(**kwargs)

    @distributed_trace
    def get_throughput(self, **kwargs):
        # type: (Any) -> ThroughputProperties
        """Get the ThroughputProperties object for this database.
        If no ThroughputProperties already exist for the database, an exception is raised.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the database.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        response_hook = kwargs.pop('response_hook', None)
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = list(self.client_connection.QueryOffers(query_spec, **kwargs))
        if not throughput_properties:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for database " + self.database_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return ThroughputProperties(offer_throughput=throughput_properties[0]["content"]["offerThroughput"],
                                    properties=throughput_properties[0],
                                    auto_scale_max_throughput=throughput_properties[0]['content']
                                    ['offerAutopilotSettings']['maxThroughput'],
                                    auto_scale_increment_percent=throughput_properties[0]['content']
                                    ['offerAutopilotSettings']['autoUpgradePolicy']['throughputPolicy'][
                                        'incrementPercent'])

    @distributed_trace
    def replace_throughput(self, throughput, max_throughput, increment_percent, **kwargs):
        # type: (Optional[int], Optional[int], Optional[int], Any) -> ThroughputProperties
        """Replace the database-level throughput.

        :param throughput: The throughput to be set (an integer).
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: Offer for the database, updated with new throughput.
        :returns: ThroughputProperties for the database, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError:
            If no offer exists for the database or if the offer could not be updated.
        :rtype: ~azure.cosmos.Offer
            If no throughput properties exists for the database or if the throughput properties could not be updated.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        response_hook = kwargs.pop('response_hook', None)
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = list(self.client_connection.QueryOffers(query_spec))
        if not throughput_properties:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for database " + self.database_link)
        new_offer = throughput_properties[0].copy()
        new_offer["content"]["offerThroughput"] = throughput
        data = self.client_connection.ReplaceOffer(offer_link=throughput_properties[0]["_self"],
                                                   offer=throughput_properties[0], **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)
        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data,
                                    auto_scale_max_throughput=data['content']['offerAutopilotSettings'][
                                        'maxThroughput'],
                                    auto_scale_increment_percent=data['content']['offerAutopilotSettings']
                                    ['autoUpgradePolicy']['throughputPolicy']['incrementPercent'])

