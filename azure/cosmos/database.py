#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Create, read, update and delete containers in the Azure Cosmos DB SQL API service.
"""

from .cosmos_client_connection import CosmosClientConnection
from .query_iterator import QueryResultIterator
from .container import Container
from . import ResponseMetadata
from .offer import Offer
from .http_constants import StatusCodes
from .errors import HTTPFailure
from .user import User

from typing import (
    Any,
    List,
    Iterable,
    Dict,
    Union,
    cast
)

class Database(object):
    """ Represents an Azure Cosmos DB SQL API database.

    A database contains one or more containers, each of which can contain items,
    stored procedures, triggers, and user-defined functions.

    A database can also have associated users, each of which configured with
    a set of permissions for accessing certain containers, stored procedures,
    triggers, user defined functions, or items.

    :ivar id: The ID (name) of the database.
    :ivar properties: A dictionary of system-generated properties for this database. See below for the list of keys.

    An Azure Cosmos DB SQL API database has the following system-generated properties; these properties are read-only:

    * `_rid`:   The resource ID.
    * `_ts`:    When the resource was last updated. The value is a timestamp.
    * `_self`:	The unique addressable URI for the resource.
    * `_etag`:	The resource etag required for optimistic concurrency control.
    * `_colls`:	The addressable path of the collections resource.
    * `_users`:	The addressable path of the users resource.
    """

    def __init__(self, client_connection, id, properties=None, response_metadata=None):
        # type: (CosmosClientConnection, str, Dict[str, Any], ResponseMetadata) -> None
        """
        :param ClientSession client_connection: Client from which this database was retrieved.
        :param str id: ID (name) of the database.
        """
        self.client_connection = client_connection
        self.id = id
        self.properties = properties
        self.response_metadata = response_metadata
        self.database_link = CosmosClientConnection._get_database_link(id)

    def _get_container_link(self, container_or_id):
        # type: (ContainerId) -> str
        if isinstance(container_or_id, str):
            return "{}/colls/{}".format(self.database_link, container_or_id)
        try:
            return cast("Container", container_or_id).container_link
        except AttributeError:
            pass
        container_id = cast("Dict[str, str]", container_or_id)["id"]
        return "{}/colls/{}".format(self.database_link, container_id)

    def create_container(
        self,
        id,
        partition_key,
        indexing_policy=None,
        default_ttl=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        offer_throughput=None,
    ):
        # type: (str, PartitionKey, Dict[str, Any], int, str, Dict[str, Any], AccessCondition, bool, int) -> Container
        """
        Create a new container with the given ID (name).

        If a container with the given ID already exists, an HTTPFailure with status_code 409 is raised.

        :param id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.

        :raise HTTPFailure: The container creation failed.


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
            database_link=self.database_link,
            collection=definition,
            options=request_options,
        )
        print(request_options)
        return Container(self.client_connection, self, data["id"], properties=data)

    def delete_container(
        self,
        container,
        max_degree_parallelism=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (ContainerId, int, str, Dict[str, Any], AccessCondition, bool) -> None
        """ Delete the container

        :param container: The ID (name) of the container to delete. You can either pass in the ID of the container to delete, or :class:`Container` instance.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        collection_link = self._get_container_link(container)
        self.client_connection.DeleteContainer(collection_link, options=request_options)

    def get_container(
        self,
        container,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        populate_partition_key_range_statistics=None,
        populate_quota_info=None
    ):
        # type: (ContainerId, str, Dict[str, Any], bool) -> Container
        """ Get the specified `Container`, or a container with specified ID (name).

        :param container: The ID (name) of the container, or a :class:`Container` instance.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param populate_partition_key_range_statistics: Enable returning partition key range statistics in response headers.
        :param populate_quota_info: Enable returning collection storage quota information in response headers.
        :raise `HTTPFailure`: Raised if the container couldn't be retrieved. This includes if the container does not exist.
        :returns: :class:`Container`, if present in the container.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START get_container]
            :end-before: [END get_container]
            :language: python
            :dedent: 0
            :caption: Get an existing container, handling a failure if encountered:
            :name: get_container

        """
        request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info

        collection_link = self._get_container_link(container)
        container_properties = self.client_connection.ReadContainer(
            collection_link, options=request_options
        )
        return Container(
            self.client_connection,
            self,
            container_properties["id"],
            properties=container_properties,
        )

    def list_containers(
        self,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (int, int, str, Dict[str, Any], bool) -> QueryIterable
        """ List the containers in the database.

        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START list_containers]
            :end-before: [END list_containers]
            :language: python
            :dedent: 0
            :caption: List all containers in the database:
            :name: list_containers

        """
        request_options = {}  # type: Dict[str, Any]
        if max_degree_parallelism is not None:
            request_options["maxDegreeOfParallelism"] = max_degree_parallelism
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.ReadContainers(
            database_link=self.database_link,
            options=request_options
        )

    def query_containers(
        self,
        query=None,
        parameters=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, int, int, str, Dict[str, Any], bool) -> QueryIterable
        """List properties for containers in the current database

        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.

    """
        request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.QueryContainers(
                    database_link=self.database_link,
                    query=query
                    if parameters is None
                    else dict(query=query, parameters=parameters),
                    options=request_options,
                )

    def replace_container(
        self,
        container,
        partition_key,
        indexing_policy=None,
        default_ttl=None,
        conflict_resolution_policy=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[str, Container], PartitionKey, Dict[str, Any], int, Dict[str, Any], str, Dict[str, Any], AccessCondition, bool) -> Container
        """ Reset the properties of the container. Property changes are persisted immediately.

        Any properties not specified will be reset to their default values.

        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START reset_container_properties]
            :end-before: [END reset_container_properties]
            :language: python
            :dedent: 0
            :caption: Reset the TTL property on a container, and display the updated properties:
            :name: reset_container_properties

        """
        container_id = getattr(container, "id", container)

        request_options = {}  # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

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
        collection_link = "{}/colls/{}".format(self.database_link, container_id)
        container_properties = self.client_connection.ReplaceContainer(
            collection_link, collection=parameters, options=request_options
        )

        return Container(
            self.client_connection,
            self,
            container_properties["id"],
            properties=container_properties,
        )

    def _get_user_link(self, id_or_user):
        # type: (Union[User, str]) -> str
        user_link = getattr(
            id_or_user,
            "user_link",
            "{}/users/{}".format(self.database_link, id_or_user),
        )
        return user_link

    def list_users(self, max_item_count=None):
        # type: (int) -> QueryIterable
        """ List all users in the container.

        :param max_item_count: Max number of users to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadUsers(
            database_link=self.database_link,
            options=request_options
        )

    #TODO: fix on feed options for not item queries
    def query_users(self, query, parameters=None, max_item_count=None):
        # type: (str, List, int) -> QueryIterable
        """Return all users matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of users to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryUsers(
            database_link=self.database_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_user(self, id):
        # type: (str) -> User
        """
        Get the user identified by `id`.

        :param id: ID of the user to be retrieved.
        :returns: The user as a dict, if present in the container.

        """
        user = self.client_connection.ReadUser(
            user_link=self._get_user_link(id_or_user=id)
        )
        return User(
            client_connection=self.client_connection,
            id=user['id'],
            database_link=self.database_link,
            properties=user
        )

    def create_user(self, body):
        # type: (Dict[str, Any]) -> User
        """ Create a user in the container.

        :param body: A dict-like object with an `id` key and value representing the user to be created.
        The user ID must be unique within the database, and consist of no more than 255 characters.

        :raises `HTTPFailure`:

        To update or replace an existing user, use the :func:`Container.upsert_user` method.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_user]
            :end-before: [END create_user]
            :language: python
            :dedent: 0
            :caption: Create a database user:
            :name: create_user

        """
        user = self.client_connection.CreateUser(
            database_link=self.database_link,
            user=body
        )

        return User(
            client_connection=self.client_connection,
            id=user['id'],
            database_link=self.database_link,
            properties=user
        )

    def upsert_user(self, body):
        # type: (Dict[str, Any]) -> User
        """ Insert or update the specified user.

        :param body: A dict-like object representing the user to update or insert.
        :raises `HTTPFailure`:

        If the user already exists in the container, it is replaced. If it does not, it is inserted.
        """

        user = self.client_connection.UpsertUser(
            database_link=self.database_link,
            user=body
        )

        return User(
            client_connection=self.client_connection,
            id=user['id'],
            database_link=self.database_link,
            properties=user
        )

    def replace_user(self, id, body):
        # type: (str, Dict[str, Any]) -> User
        """ Replaces the specified user if it exists in the container.

        :param id: Id of the user to be replaced.
        :param body: A dict-like object representing the user to replace.
        :raises `HTTPFailure`:

        """
        user = self.client_connection.ReplaceUser(
            user_link=self._get_user_link(id),
            user=body
        )

        return User(
            client_connection=self.client_connection,
            id=user['id'],
            database_link=self.database_link,
            properties=user
        )

    def delete_user(self, id):
        # type: (str) -> None
        """ Delete the specified user from the container.

        :param id: Id of the user to delete from the container.
        :raises `HTTPFailure`: The user wasn't deleted successfully. If the user does not exist in the container, a `404` error is returned.

        """

        self.client_connection.DeleteUser(
            user_link=self._get_user_link(id),
        )

    #TODO: add database level offer throughput tests
    def read_offer(self):
        # type: () -> Offer
        link = self.properties['_self']
        query_spec = {
                        'query': 'SELECT * FROM root r WHERE r.resource=@link',
                        'parameters': [
                            {'name': '@link', 'value': link}
                        ]
                     }
        offers = list(self.client_connection.QueryOffers(query_spec))
        if (len(offers) <= 0):
            raise HTTPFailure(StatusCodes.NOT_FOUND, "Could not find Offer for database " + self.database_link)
        data = offers[0]
        return Offer(
            offer_throughput=offers[0]['content']['offerThroughput'],
            properties=offers[0])

    def replace_throughput(self, throughput):
        # type: (int) -> Offer
        link = self.properties['_self']
        query_spec = {
                        'query': 'SELECT * FROM root r WHERE r.resource=@link',
                        'parameters': [
                            {'name': '@link', 'value': link}
                        ]
                     }
        offers = list(self.client_connection.QueryOffers(query_spec))
        if (len(offers) <= 0):
            raise HTTPFailure(StatusCodes.NOT_FOUND, "Could not find Offer for collection " + self.database_link)
        new_offer = offers[0].copy()
        new_offer['content']['offerThroughput'] = throughput
        data = self.client_connection.ReplaceOffer(
            offer_link=offers[0]['_self'],
            offer=offers[0]
        )
        return Offer(
            offer_throughput=data['content']['offerThroughput'],
            properties=data)
