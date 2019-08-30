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

"""Create, read, update and delete containers in the Azure Cosmos DB SQL API service.
"""

from typing import Any, List, Dict, Mapping, Union, cast

import six
from azure.core.tracing.decorator import distributed_trace

from ._cosmos_client_connection import CosmosClientConnection
from .container_client import ContainerClient
from .offer import Offer
from .http_constants import StatusCodes
from .errors import CosmosResourceNotFoundError
from .user_client import UserClient
from ._query_iterable import QueryIterable

__all__ = ("DatabaseClient",)

# pylint: disable=protected-access


class DatabaseClient(object):
    """ Represents an Azure Cosmos DB SQL API database.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    A database can also have associated users, each of which configured with
    a set of permissions for accessing certain containers, stored procedures,
    triggers, user defined functions, or items.

    :ivar id: The ID (name) of the database.

    An Azure Cosmos DB SQL API database has the following system-generated properties; these properties are read-only:

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

    @staticmethod
    def _get_container_id(container_or_id):
        # type: (Union[str, ContainerClient, Dict[str, Any]]) -> str
        if isinstance(container_or_id, six.string_types):
            return container_or_id
        try:
            return cast("ContainerClient", container_or_id).id
        except AttributeError:
            pass
        return cast("Dict[str, str]", container_or_id)["id"]

    def _get_container_link(self, container_or_id):
        # type: (Union[str, ContainerClient, Dict[str, Any]]) -> str
        return u"{}/colls/{}".format(self.database_link, self._get_container_id(container_or_id))

    def _get_user_link(self, user_or_id):
        # type: (Union[UserClient, str, Dict[str, Any]]) -> str
        if isinstance(user_or_id, six.string_types):
            return u"{}/users/{}".format(self.database_link, user_or_id)
        try:
            return cast("UserClient", user_or_id).user_link
        except AttributeError:
            pass
        return u"{}/users/{}".format(self.database_link, cast("Dict[str, str]", user_or_id)["id"])

    def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self.read()
        return self._properties

    @distributed_trace
    def read(
        self,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        request_options=None,
        response_hook=None,
        **kwargs
    ):
        # type: (str, Dict[str, str], bool, Dict[str, Any], Optional[Callable]) -> Dict[str, Any]
        """
        Read the database properties

        :param database: The ID (name), dict representing the properties or :class:`DatabaseClient`
            instance of the database to read.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: Dict[Str, Any]
        :raise `CosmosHttpResponseError`: If the given database couldn't be retrieved.

        """
        # TODO this helper function should be extracted from CosmosClient
        from .cosmos_client import CosmosClient

        database_link = CosmosClient._get_database_link(self)
        if not request_options:
            request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._properties = self.client_connection.ReadDatabase(database_link, options=request_options, **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return self._properties

    @distributed_trace
    def create_container(
        self,
        id,  # type: str  # pylint: disable=redefined-builtin
        partition_key,  # type: PartitionKey
        indexing_policy=None,  # type: Dict[str, Any]
        default_ttl=None,  # type: int
        session_token=None,  # type: str
        initial_headers=None,  # type:  Dict[str, str]
        access_condition=None,  # type: Dict[str, str]
        populate_query_metrics=None,  # type: bool
        offer_throughput=None,  # type: int
        unique_key_policy=None,  # type: Dict[str, Any]
        conflict_resolution_policy=None,  # type: Dict[str, Any]
        request_options=None,  # type: Dict[str, Any]
        response_hook=None,  # type: Optional[Callable]
        **kwargs
    ):
        # type: (...) -> ContainerClient
        """
        Create a new container with the given ID (name).

        If a container with the given ID already exists, a CosmosResourceExistsError is raised.

        :param id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.
        :param unique_key_policy: The unique key policy to apply to the container.
        :param conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: A :class:`ContainerClient` instance representing the new container.
        :raise CosmosHttpResponseError: The container creation failed.


        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_container]
            :end-before: [END create_container]
            :language: python
            :dedent: 0
            :caption: Create a container with default settings:
            :name: create_container

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_container_with_settings]
            :end-before: [END create_container_with_settings]
            :language: python
            :dedent: 0
            :caption: Create a container with specific settings; in this case, a custom partition key:
            :name: create_container_with_settings

        """
        definition = dict(id=id)  # type: Dict[str, Any]
        if partition_key:
            definition["partitionKey"] = partition_key
        if indexing_policy:
            definition["indexingPolicy"] = indexing_policy
        if default_ttl:
            definition["defaultTtl"] = default_ttl
        if unique_key_policy:
            definition["uniqueKeyPolicy"] = unique_key_policy
        if conflict_resolution_policy:
            definition["conflictResolutionPolicy"] = conflict_resolution_policy

        if not request_options:
            request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if offer_throughput is not None:
            request_options["offerThroughput"] = offer_throughput

        data = self.client_connection.CreateContainer(
            database_link=self.database_link, collection=definition, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)

        return ContainerClient(self.client_connection, self.database_link, data["id"], properties=data)

    @distributed_trace
    def delete_container(
        self,
        container,  # type: Union[str, ContainerClient, Dict[str, Any]]
        session_token=None,  # type: str
        initial_headers=None,  # type: Dict[str, str]
        access_condition=None,  # type: Dict[str, str]
        populate_query_metrics=None,  # type: bool
        request_options=None,  # type: Dict[str, Any]
        response_hook=None,  # type: Optional[Callable]
        **kwargs
    ):
        # type: (...) -> None
        """ Delete the container

        :param container: The ID (name) of the container to delete. You can either
            pass in the ID of the container to delete, a :class:`ContainerClient` instance or
            a dict representing the properties of the container.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :raise CosmosHttpResponseError: If the container couldn't be deleted.

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        result = self.client_connection.DeleteContainer(collection_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    def get_container_client(self, container):
        # type: (Union[str, ContainerClient, Dict[str, Any]]) -> ContainerClient
        """ Get the specified `ContainerClient`, or a container with specified ID (name).

        :param container: The ID (name) of the container, a :class:`ContainerClient` instance,
            or a dict representing the properties of the container to be retrieved.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START get_container]
            :end-before: [END get_container]
            :language: python
            :dedent: 0
            :caption: Get an existing container, handling a failure if encountered:
            :name: get_container

        """
        if isinstance(container, ContainerClient):
            id_value = container.id
        elif isinstance(container, Mapping):
            id_value = container["id"]
        else:
            id_value = container

        return ContainerClient(self.client_connection, self.database_link, id_value)

    @distributed_trace
    def read_all_containers(
        self,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        feed_options=None,
        response_hook=None,
        **kwargs
    ):
        # type: (int, str, Dict[str, str], bool, Dict[str, Any], Optional[Callable]) -> QueryIterable
        """ List the containers in the database.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: An Iterable of container properties (dicts).

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START list_containers]
            :end-before: [END list_containers]
            :language: python
            :dedent: 0
            :caption: List all containers in the database:
            :name: list_containers

        """
        if not feed_options:
            feed_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if session_token:
            feed_options["sessionToken"] = session_token
        if initial_headers:
            feed_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
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
        query=None,
        parameters=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        feed_options=None,
        response_hook=None,
        **kwargs
    ):
        # type: (str, List, int, str, Dict[str, str], bool, Dict[str, Any], Optional[Callable]) -> QueryIterable
        """List properties for containers in the current database

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: An Iterable of container properties (dicts).

        """
        if not feed_options:
            feed_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if session_token:
            feed_options["sessionToken"] = session_token
        if initial_headers:
            feed_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
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
        container,  # type: Union[str, ContainerClient, Dict[str, Any]]
        partition_key,  # type: PartitionKey
        indexing_policy=None,  # type: Dict[str, Any]
        default_ttl=None,  # type: int
        conflict_resolution_policy=None,  # type: Dict[str, Any]
        session_token=None,  # type: str
        initial_headers=None,  # type: Dict[str, str]
        access_condition=None,  # type:  Dict[str, str]
        populate_query_metrics=None,  # type: bool
        request_options=None,  # type: Dict[str, Any]
        response_hook=None,  # type: Optional[Callable]
        **kwargs
    ):
        # type: (...) -> ContainerClient
        """ Reset the properties of the container. Property changes are persisted immediately.

        Any properties not specified will be reset to their default values.

        :param container: The ID (name), dict representing the properties or
            :class:`ContainerClient` instance of the container to be replaced.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param conflict_resolution_policy: The conflict resolution policy to apply to the container.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :raise `CosmosHttpResponseError`: Raised if the container couldn't be replaced. This includes
            if the container with given id does not exist.
        :returns: :class:`ContainerClient` instance representing the container after replace completed.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START reset_container_properties]
            :end-before: [END reset_container_properties]
            :language: python
            :dedent: 0
            :caption: Reset the TTL property on a container, and display the updated properties:
            :name: reset_container_properties

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
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

        return ContainerClient(
            self.client_connection, self.database_link, container_properties["id"], properties=container_properties
        )

    @distributed_trace
    def read_all_users(self, max_item_count=None, feed_options=None, response_hook=None, **kwargs):
        # type: (int, Dict[str, Any], Optional[Callable]) -> QueryIterable
        """ List all users in the container.

        :param max_item_count: Max number of users to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: An Iterable of user properties (dicts).

        """
        if not feed_options:
            feed_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadUsers(
            database_link=self.database_link, options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_users(self, query, parameters=None, max_item_count=None, feed_options=None, response_hook=None, **kwargs):
        # type: (str, List, int, Dict[str, Any], Optional[Callable]) -> QueryIterable
        """Return all users matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of users to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: An Iterable of user properties (dicts).

        """
        if not feed_options:
            feed_options = {}  # type: Dict[str, Any]
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
        # type: (Union[str, UserClient, Dict[str, Any]]) -> UserClient
        """
        Get the user identified by `id`.

        :param user: The ID (name), dict representing the properties or :class:`UserClient`
            instance of the user to be retrieved.
        :returns: A :class:`UserClient` instance representing the retrieved user.
        :raise `CosmosHttpResponseError`: If the given user couldn't be retrieved.

        """
        if isinstance(user, UserClient):
            id_value = user.id
        elif isinstance(user, Mapping):
            id_value = user["id"]
        else:
            id_value = user

        return UserClient(client_connection=self.client_connection, id=id_value, database_link=self.database_link)

    @distributed_trace
    def create_user(self, body, request_options=None, response_hook=None, **kwargs):
        # type: (Dict[str, Any], Dict[str, Any], Optional[Callable]) -> UserClient
        """ Create a user in the container.

        :param body: A dict-like object with an `id` key and value representing the user to be created.
        The user ID must be unique within the database, and consist of no more than 255 characters.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: A :class:`UserClient` instance representing the new user.
        :raise `CosmosHttpResponseError`: If the given user couldn't be created.

        To update or replace an existing user, use the :func:`ContainerClient.upsert_user` method.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_user]
            :end-before: [END create_user]
            :language: python
            :dedent: 0
            :caption: Create a database user:
            :name: create_user

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]

        user = self.client_connection.CreateUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, user)

        return UserClient(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def upsert_user(self, body, request_options=None, response_hook=None, **kwargs):
        # type: (Dict[str, Any], Dict[str, Any], Optional[Callable]) -> UserClient
        """ Insert or update the specified user.

        :param body: A dict-like object representing the user to update or insert.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: A :class:`UserClient` instance representing the upserted user.
        :raise `CosmosHttpResponseError`: If the given user could not be upserted.

        If the user already exists in the container, it is replaced. If it does not, it is inserted.

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]

        user = self.client_connection.UpsertUser(
            database_link=self.database_link, user=body, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, user)

        return UserClient(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def replace_user(self, user, body, request_options=None, response_hook=None, **kwargs):
        # type: (Union[str, UserClient, Dict[str, Any]], Dict[str, Any], Dict[str, Any], Optional[Callable]) -> UserClient
        """ Replaces the specified user if it exists in the container.

        :param user: The ID (name), dict representing the properties or :class:`UserClient`
            instance of the user to be replaced.
        :param body: A dict-like object representing the user to replace.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :returns: A :class:`UserClient` instance representing the user after replace went through.
        :raise `CosmosHttpResponseError`: If the replace failed or the user with given id does not exist.

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]

        user = self.client_connection.ReplaceUser(
            user_link=self._get_user_link(user), user=body, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, user)

        return UserClient(
            client_connection=self.client_connection, id=user["id"], database_link=self.database_link, properties=user
        )

    @distributed_trace
    def delete_user(self, user, request_options=None, response_hook=None, **kwargs):
        # type: (Union[str, UserClient, Dict[str, Any]], Dict[str, Any], Optional[Callable]) -> None
        """ Delete the specified user from the container.

        :param user: The ID (name), dict representing the properties or :class:`UserClient`
            instance of the user to be deleted.
        :param request_options: Dictionary of additional properties to be used for the request.
        :param response_hook: a callable invoked with the response metadata
        :raises `CosmosHttpResponseError`: The user wasn't deleted successfully. If the user does not
            exist in the container, a `404` error is returned.

        """
        if not request_options:
            request_options = {}  # type: Dict[str, Any]

        result = self.client_connection.DeleteUser(
            user_link=self._get_user_link(user), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    @distributed_trace
    def read_offer(self, response_hook=None, **kwargs):
        # type: (Optional[Callable]) -> Offer
        """ Read the Offer object for this database.

        :param response_hook: a callable invoked with the response metadata
        :returns: Offer for the database.
        :raise CosmosHttpResponseError: If no offer exists for the database or if the offer could not be retrieved.

        """
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        offers = list(self.client_connection.QueryOffers(query_spec, **kwargs))
        if not offers:
            raise CosmosResourceNotFoundError(
                status=StatusCodes.NOT_FOUND,
                message="Could not find Offer for database " + self.database_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, offers)

        return Offer(offer_throughput=offers[0]["content"]["offerThroughput"], properties=offers[0])

    @distributed_trace
    def replace_throughput(self, throughput, response_hook=None, **kwargs):
        # type: (int, Optional[Callable]) -> Offer
        """ Replace the database level throughput.

        :param throughput: The throughput to be set (an integer).
        :param response_hook: a callable invoked with the response metadata
        :returns: Offer for the database, updated with new throughput.
        :raise CosmosHttpResponseError: If no offer exists for the database or if the offer could not be updated.

        """
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        offers = list(self.client_connection.QueryOffers(query_spec))
        if not offers:
            raise CosmosResourceNotFoundError(
                status=StatusCodes.NOT_FOUND,
                message="Could not find Offer for collection " + self.database_link)
        new_offer = offers[0].copy()
        new_offer["content"]["offerThroughput"] = throughput
        data = self.client_connection.ReplaceOffer(offer_link=offers[0]["_self"], offer=offers[0], **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)
        return Offer(offer_throughput=data["content"]["offerThroughput"], properties=data)
