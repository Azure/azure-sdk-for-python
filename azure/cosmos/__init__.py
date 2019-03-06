"""
Create, read, update, and delete databases, containers, and items in Azure Cosmos DB SQL API databases.
"""

__all__ = ["CosmosClient", "Database", "Container", "Item"]


from .query_iterator import QueryResultIterator
from .cosmos_client_connection import CosmosClientConnection
from .errors import HTTPFailure

from typing import (
    Any,
    List,
    Iterable,
    Iterator,
    Optional,
    Dict,
    Union,
    Tuple,
    cast,
    overload,
    Sequence,
)

DatabaseId = Union["Database", Dict[str, Any], str]
ContainerId = Union["Container", Dict[str, Any], str]


class User:
    pass


class PartitionKey(dict):
    """ Key used to partition a container into logical partitions.

    See https://docs.microsoft.com/azure/cosmos-db/partitioning-overview#choose-partitionkey for more information
    on how to choose partition keys.

    :ivar path: The path of the partition key
    :ivar kind: What kind of partition key is being defined
    """

    def __init__(self, path, kind="Hash"):
        # (str, str) -> None
        self.path = path
        self.kind = kind

    @property
    def kind(self):
        return self["kind"]

    @kind.setter
    def kind(self, value):
        self["kind"] = value

    @property
    def path(self):
        # () -> str
        return self["paths"][0]

    @path.setter
    def path(self, value):
        # (str) -> None
        self["paths"] = [value]


class AccessCondition(dict):
    pass


class ResponseMetadata(dict):
    pass


class CosmosClient:
    """
    Provides a client-side logical representation of an Azure Cosmos DB account.
    Use this client to configure and execute requests to the Azure Cosmos DB service.
    """

    def __init__(self, url, key, consistency_level="Session", connection_policy=None):
        # type: (str, str, str, Any) -> None
        """ Instantiate a new CosmosClient.

        :param url: The URL of the Cosmos DB account.
        :param consistency_level: Consistency level to use for the session.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_client]
            :end-before: [END create_client]
            :language: python
            :dedent: 0
            :caption: Create a new instance of the Cosmos DB client:
            :name: create_client

        """
        self.client_connection = CosmosClientConnection(
            url,
            dict(masterKey=key),
            consistency_level=consistency_level,
            connection_policy=connection_policy,
        )

    @staticmethod
    def _get_database_link(database_or_id):
        # type: (DatabaseId) -> str
        if isinstance(database_or_id, str):
            return "dbs/{}".format(database_or_id)
        try:
            return cast("Database", database_or_id).database_link
        except AttributeError:
            pass

        if isinstance(database_or_id, str):
            database_id = database_or_id
        else:
            database_id = cast("Dict[str, str]", database_or_id)["id"]
        return "dbs/{}".format(database_id)

    def create_database(
        self,
        id,
        consistency_level=None,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, bool, str, AccessCondition, bool, bool) -> Database
        """Create a new database with the given ID (name).

        :param id: ID (name) of the database to create.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: A :class:`Database` instance representing the new database.
        :raises `HTTPFailure`: If `fail_if_exists` is set to True and a database with the given ID already exists.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_database]
            :end-before: [END create_database]
            :language: python
            :dedent: 0
            :caption: Create a database in the Cosmos DB account:
            :name: create_database

        """
        result = self.client_connection.CreateDatabase(database=dict(id=id))
        return Database(self.client_connection, id=result["id"], properties=result)

    def get_database(
        self,
        database,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (DatabaseId, bool, str, Dict[str, Any], bool) -> Database
        """
        Retrieve an existing database with the ID (name) `id`.

        :param id: ID of the new :class:`Database`.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise `HTTPFailure`: If the given database couldn't be retrieved.
        """
        database_link = CosmosClient._get_database_link(database)
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        properties = self.client_connection.ReadDatabase(
            database_link, options=request_options
        )
        return Database(
            self.client_connection,
            properties["id"],
            properties=properties,
            response_metadata=ResponseMetadata(
                self.client_connection.last_response_headers
            ),
        )

    def list_databases(
        self,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (bool, bool, int, int, str, Dict[str, Any], bool) -> Iterable[Database]
        """
        List the databases in a Cosmos DB SQL database account.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
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

        for database in [
            Database(self.client_connection, properties["id"], properties=properties)
            for properties in self.client_connection.ReadDatabases(
                options=request_options
            )
        ]:
            yield database

    def list_database_properties(
        self,
        query=None,
        parameters=None,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, bool, bool, int, int, str, Dict[str, Any], bool) -> Iterable[Union[Dict[str, Any], Any]]
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
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

        if query:
            # This is currently eagerly evaluated in order to capture the headers
            # from the call.
            # (just returning a generator did not initiate the first network call, so
            # the headers were misleading)
            # This needs to change for "real" implementation
            results = iter(
                list(
                    self.client_connection.QueryDatabases(
                        query, options=request_options
                    )
                )
            )
        else:
            results = iter(
                list(self.client_connection.ReadDatabases(options=request_options))
            )
        self.session_token = self.client_connection.last_response_headers.get(
            "x-ms-session-token"
        )
        return QueryResultIterator(
            results,
            metadata=ResponseMetadata(self.client_connection.last_response_headers),
        )

    def delete_database(
        self,
        database,
        disable_ru_per_minute_usage=None,
        max_degree_parallelism=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (DatabaseId, bool, str, int, Dict[str, Any], AccessCondition, bool) -> None
        """
        Delete the database with the given ID (name).

        :param database: The ID (name) or :class:`Database` instance of the database to delete.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise HTTPFailure: If the database couldn't be deleted.
        """

        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
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

        database_link = CosmosClient._get_database_link(database)
        self.client_connection.DeleteDatabase(database_link, options=request_options)


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
        self.database_link = CosmosClient._get_database_link(id)

    def _get_container_link(self, container_or_id):
        # type: (ContainerId) -> str
        if isinstance(container_or_id, str):
            return "{}/colls/{}".format(self.database_link, container_or_id)
        try:
            return cast("Container", container_or_id).collection_link
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
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        offer_throughput=None,
    ):
        # type: (str, PartitionKey, Dict[str, Any], int, bool, str, Dict[str, Any], AccessCondition, bool, int) -> Container
        """
        Create a new container with the given ID (name).

        If a container with the given ID already exists, an HTTPFailure with status_code 409 is raised.

        :param id: ID (name) of container to create.
        :param partition_key: The partition key to use for the container.
        :param indexing_policy: The indexing policy to apply to the container.
        :param default_ttl: Default time to live (TTL) for items in the container. If unspecified, items do not expire.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
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
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        data = self.client_connection.CreateContainer(
            database_link=self.database_link,
            collection=definition,
            options=request_options,
        )
        return Container(self.client_connection, self, data["id"], properties=data)

    def delete_container(
        self,
        container,
        disable_ru_per_minute_usage=None,
        max_degree_parallelism=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (ContainerId, bool, int, str, Dict[str, Any], AccessCondition, bool) -> None
        """ Delete the container

        :param container: The ID (name) of the container to delete. You can either pass in the ID of the container to delete, or :class:`Container` instance.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
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
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (ContainerId, bool, str, Dict[str, Any], bool) -> Container
        """ Get the specified `Container`, or a container with specified ID (name).

        :param container: The ID (name) of the container, or a :class:`Container` instance.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
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
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

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
        disable_ru_per_minute_usage=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (bool, int, int, str, Dict[str, Any], bool) -> Iterable[Container]
        """ List the containers in the database.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
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
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
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

        for container in [
            Container(self.client_connection, self, container["id"], container)
            for container in self.client_connection.ReadContainers(
                database_link=self.database_link, options=request_options
            )
        ]:
            yield container

    def list_container_properties(
        self,
        query=None,
        parameters=None,
        disable_ru_per_minute_usage=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, bool, int, int, str, Dict[str, Any], bool) -> Iterable[Container]
        """List properties for containers in the current database

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.

    """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = iter(
            list(
                self.client_connection.QueryContainers(
                    database_link=self.database_link,
                    query=query
                    if parameters is None
                    else dict(query=query, parameters=parameters),
                    options=request_options,
                )
            )
        )

        return QueryResultIterator(
            result,
            metadata=ResponseMetadata(self.client_connection.last_response_headers),
        )

    def reset_container_properties(
        self,
        container,
        partition_key,
        indexing_policy=None,
        default_ttl=None,
        conflict_resolution_policy=None,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[str, Container], PartitionKey, str, int, str, bool, str, Dict[str, Any], AccessCondition, bool) -> None
        """ Reset the properties of the container. Property changes are persisted immediately.

        Any properties not specified will be reset to their default values.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
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
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
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
        self.client_connection.ReplaceContainer(
            collection_link, collection=parameters, options=request_options
        )

    def get_user_link(self, id_or_user):
        # type: (Union[User, str]) -> str
        user_link = getattr(
            id_or_user,
            "user_link",
            "{}/users/{}".format(self.database_link, id_or_user),
        )
        return user_link

    def create_user(self, user, options=None):
        """ Create a new user in the database.

        :param user: A dict-like object with an `id` key and value.

        The user ID must be unique within the database, and consist of no more than 255 characters.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_user]
            :end-before: [END create_user]
            :language: python
            :dedent: 0
            :caption: Create a database user:
            :name: create_user

        """
        database = cast("Database", self)
        return database.client_connection.CreateUser(
            database.database_link, user, options
        )

    def get_user(self, id):
        """ Get the specified user from the database.

        :param id: The ID of the user to retrieve.
        """
        database = cast("Database", self)
        return database.client_connection.ReadUser(self.get_user_link(id))

    def list_users(self):
        """ Get all database users.
        """
        database = cast("Database", self)
        for user in [User(user) for user in database.client_connection.ReadUsers()]:
            yield user

    def list_user_properties(self, query=None, parameters=None):
        # type: (str, Any) -> List[User]
        pass

    def delete_user(self, user):
        """ Delete the specified user from the database.
        """
        database = cast("Database", self)
        database.client_connection.DeleteUser(self.get_user_link(user))


class Item(dict):
    """ Represents a document in an Azure Cosmos DB SQL API container.

    To create, read, update, and delete Items, use the associated methods on the :class:`Container`.
    The Item must include an `id` key with a value that uniquely identifies the item within the container.
    """

    def __init__(self, headers, data):
        # type: (Dict[str, Any], Dict[str, Any]) -> None
        super().__init__()
        self.response_headers = headers
        self.update(data)


class Container:
    """ An Azure Cosmos DB container.

    A container in an Azure Cosmos DB SQL API database is a collection of documents, each of which represented as an :class:`Item`.

    :ivar str id: ID (name) of the container
    :ivar str session_token: The session token for the container.

    .. note::

        To create a new container in an existing database, use :func:`Database.create_container`.

    """

    def __init__(self, client_connection, database, id, properties=None):
        # type: (CosmosClientConnection, Union[Database, str], str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.session_token = None
        self.id = id
        self.properties = properties
        database_link = CosmosClient._get_database_link(database)
        self.collection_link = "{}/colls/{}".format(database_link, self.id)

    def _get_document_link(self, item_or_link):
        # type: (Union[Dict[str, Any], str, Item]) -> str
        if isinstance(item_or_link, str):
            return "{}/docs/{}".format(self.collection_link, item_or_link)
        return cast("str", cast("Item", item_or_link)["_self"])

    def get_item(
        self,
        id,
        partition_key,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, bool, str, Dict[str, Any], bool) -> Item
        """
        Get the item identified by `id`.

        :param id: ID of item to retrieve.
        :param partition_key: Partition key for the item to retrieve.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: :class:`Item`, if present in the container.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START update_item]
            :end-before: [END update_item]
            :language: python
            :dedent: 0
            :caption: Get an item from the database and update one of its properties:
            :name: update_item

        """
        doc_link = self._get_document_link(id)

        request_options = {}  # type: Dict[str, Any]
        if partition_key:
            request_options["partitionKey"] = partition_key
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.ReadItem(
            document_link=doc_link, options=request_options
        )
        headers = self.client_connection.last_response_headers
        self.session_token = headers.get("x-ms-session-token", self.session_token)
        return Item(headers=headers, data=result)

    def list_items(
        self,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (bool, bool, int, int, str, Dict[str, Any], bool) -> Iterable[Item]
        """ List all items in the container.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
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

        items = self.client_connection.ReadItems(
            collection_link=self.collection_link, feed_options=request_options
        )
        headers = self.client_connection.last_response_headers
        for item in [Item(headers=headers, data=item) for item in items]:
            yield item

    def query_items_change_feed(self, options=None):
        """ Get a sorted list of items that were changed, in the order in which they were modified.
        """
        items = self.client_connection.QueryItemsChangeFeed(
            self.collection_link, options=options
        )
        headers = self.client_connection.last_response_headers
        for item in items:
            yield Item(headers, item)

    def query_items(
        self,
        query,
        parameters=None,
        partition_key=None,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_degree_parallelism=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, List, str, bool, bool, int, int, str, Dict[str, Any], bool) -> QueryResultIterator
        """Return all results matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param partition_key: Specifies the partition key value for the item.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: An `Iterator` containing each result returned by the query, if any.

        You can use any value for the container name in the FROM clause, but typically the container name is used.
        In the examples below, the container name is "products," and is aliased as "p" for easier referencing
        in the WHERE clause.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START query_items]
            :end-before: [END query_items]
            :language: python
            :dedent: 0
            :caption: Get all products that have not been discontinued:
            :name: query_items

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START query_items_param]
            :end-before: [END query_items_param]
            :language: python
            :dedent: 0
            :caption: Parameterized query to get all products that have been discontinued:
            :name: query_items_param

        """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
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

        items = self.client_connection.QueryItems(
            database_or_Container_link=self.collection_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
            partition_key=partition_key,
        )
        headers = self.client_connection.last_response_headers
        self.session_token = headers["x-ms-session-token"]
        items_iterator = iter(items)
        return QueryResultIterator(items_iterator, metadata=ResponseMetadata(headers))

    def replace_item(
        self,
        item,
        body,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[Item, str], Dict[str, Any], bool, str, Dict[str, Any], AccessCondition, bool) -> Item
        """ Replaces the specified item if it exists in the container.

        :param body: A dict-like object representing the item to replace.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:
        """
        item_link = self._get_document_link(item)
        request_options = {}  # type: Dict[str, Any]
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics
        data = self.client_connection.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options
        )
        return Item(headers=self.client_connection.last_response_headers, data=data)

    def upsert_item(
        self,
        body,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Dict[str, Any], bool, str, Dict[str, Any], AccessCondition, bool) -> Item
        """ Insert or update the specified item.

        :param body: A dict-like object representing the item to update or insert.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:

        If the item already exists in the container, it is replaced. If it does not, it is inserted.
        """
        request_options = {}  # type: Dict[str, Any]
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.UpsertItem(
            database_or_Container_link=self.collection_link, document=body
        )
        return Item(headers=self.client_connection.last_response_headers, data=result)

    def create_item(
        self,
        body,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Dict[str, Any], bool, str, Dict[str, Any], AccessCondition, bool) -> Item
        """ Create an item in the container.

        :param body: A dict-like object representing the item to create.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :returns: The :class:`Item` inserted into the container.
        :raises `HTTPFailure`:

        To update or replace an existing item, use the :func:`Container.upsert_item` method.

        """
        request_options = {}  # type: Dict[str, Any]
        request_options["disableIdGeneration"] = True
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.CreateItem(
            database_or_Container_link=self.collection_link,
            document=body,
            options=request_options,
        )
        return Item(headers=self.client_connection.last_response_headers, data=result)

    def delete_item(
        self,
        item,
        partition_key,
        disable_ru_per_minute_usage=None,
        max_degree_parallelism=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[Item, Dict[str, Any], str], str, bool, int, str, Dict[str, Any], AccessCondition, bool) -> None
        """ Delete the specified item from the container.

        :param item: The :class:`Item` to delete from the container.
        :param partition_key: Specifies the partition key value for the item.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_degree_parallelism: The maximum number of concurrent operations that run client side during parallel query execution in the Azure Cosmos DB database service. Negative values make the system automatically decides the number of concurrent operations to run.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`: The item wasn't deleted successfully. If the item does not exist in the container, a `404` error is returned.

        """
        request_options = {}  # type: Dict[str, Any]
        if partition_key:
            request_options["partitionKey"] = partition_key
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
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

        document_link = self._get_document_link(item)
        self.client_connection.DeleteItem(
            document_link=document_link, options=request_options or None
        )

    def list_stored_procedures(self, query):
        pass

    def get_stored_procedure(self, id):
        pass

    def create_stored_procedure(self):
        pass

    def upsert_stored_procedure(self, trigger):
        pass

    def delete_stored_procedure(self):
        pass

    def list_triggers(self, query):
        pass

    def get_trigger(self, id):
        pass

    def create_trigger(self):
        pass

    def upsert_trigger(self, trigger):
        pass

    def delete_trigger(self):
        pass

    def list_user_defined_functions(self, query):
        pass

    def get_user_defined_function(self, id):
        pass

    def create_user_defined_function(self):
        pass

    def upsert_user_defined_function(self, trigger):
        pass

    def delete_user_defined_function(self):
        pass
