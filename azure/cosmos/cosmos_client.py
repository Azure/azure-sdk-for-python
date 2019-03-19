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

"""Create, read, and delete databases in the Azure Cosmos DB SQL API service.
"""

from .cosmos_client_connection import CosmosClientConnection
from .database import Database
from .documents import ConnectionPolicy
from .query_iterable import QueryIterable
from typing import (
    Any,
    Dict
)


class CosmosClient:
    """
    Provides a client-side logical representation of an Azure Cosmos DB account.
    Use this client to configure and execute requests to the Azure Cosmos DB service.
    """

    def __init__(self, url, auth, consistency_level="Session", connection_policy=None):
        # type: (str, Dict[str, str],, str, ConnectionPolicy) -> None
        """ Instantiate a new CosmosClient.

        :param url: The URL of the Cosmos DB account.
        :param auth:
            Contains 'masterKey' or 'resourceTokens', where
            auth['masterKey'] is the default authorization key to use to
            create the client, and auth['resourceTokens'] is the alternative
            authorization key.
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
            auth,
            consistency_level=consistency_level,
            connection_policy=connection_policy,
        )

    def create_database(
        self,
        id,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        offer_throughput=None
    ):
        # type: (str, str, bool, str, AccessCondition, bool, bool) -> Database
        """Create a new database with the given ID (name).

        :param id: ID (name) of the database to create.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.
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
        if offer_throughput is not None:
            request_options["offerThroughput"] = offer_throughput

        result = self.client_connection.CreateDatabase(database=dict(id=id), options=request_options)
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
        database_link = CosmosClientConnection._get_database_link(database)
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
            properties=properties
        )

    def list_databases(
        self,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (bool, bool, int, str, Dict[str, Any], bool) -> QueryIterable
        """
        List the databases in a Cosmos DB SQL database account.

        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.ReadDatabases(
                options=request_options
            )

    def query_databases(
        self,
        query=None,
        parameters=None,
        disable_ru_per_minute_usage=None,
        enable_cross_partition_query=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, bool, bool, int, str, Dict[str, Any], bool) -> QueryIterable
        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
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
            return self.client_connection.QueryDatabases(
                query=query
                if parameters is None
                else dict(query=query, parameters=parameters),
                options=request_options
            )
        else:
            return self.client_connection.ReadDatabases(options=request_options)

    def delete_database(
        self,
        database,
        disable_ru_per_minute_usage=None,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (DatabaseId, bool, str, Dict[str, Any], AccessCondition, bool) -> None
        """
        Delete the database with the given ID (name).

        :param database: The ID (name) or :class:`Database` instance of the database to delete.
        :param disable_ru_per_minute_usage: Enable/disable Request Units(RUs)/minute capacity to serve the request if regular provisioned RUs/second is exhausted.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raise HTTPFailure: If the database couldn't be deleted.
        """

        request_options = {}  # type: Dict[str, Any]
        if disable_ru_per_minute_usage is not None:
            request_options["disableRUPerMinuteUsage"] = disable_ru_per_minute_usage
        if session_token:
            request_options["sessionToken"] = session_token
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        database_link = CosmosClientConnection._get_database_link(database)
        self.client_connection.DeleteDatabase(database_link, options=request_options)

    def get_database_account(self):
        # type: () -> DatabaseAccount
        """
        Retrieve the database account information.
        """
        return self.client_connection.GetDatabaseAccount()
