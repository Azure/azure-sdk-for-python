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

import six
from .cosmos_client_connection import CosmosClientConnection
from .database import Database
from .documents import ConnectionPolicy, DatabaseAccount
from .query_iterable import QueryIterable
from typing import (
    Any,
    Dict,
    Mapping,
    Union,
    cast
)


class CosmosClient:
    """
    Provides a client-side logical representation of an Azure Cosmos DB account.
    Use this client to configure and execute requests to the Azure Cosmos DB service.
    """

    def __init__(self, url, auth, consistency_level="Session", connection_policy=None):
        # type: (str, Dict[str, str], str, ConnectionPolicy) -> None
        """ Instantiate a new CosmosClient.

        :param url: The URL of the Cosmos DB account.
        :param auth:
            Contains 'masterKey' or 'resourceTokens', where
            auth['masterKey'] is the default authorization key to use to
            create the client, and auth['resourceTokens'] is the alternative
            authorization key.
        :param consistency_level: Consistency level to use for the session.
        :param connection_policy: Connection policy to use for the session.

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

    @staticmethod
    def _get_database_link(database_or_id):
        # type: (str) -> str
        if isinstance(database_or_id, six.string_types):
            return "dbs/{}".format(database_or_id)
        try:
            return cast("Database", database_or_id).database_link
        except AttributeError:
            pass
        database_id = cast("Dict[str, str]", database_or_id)["id"]
        return "dbs/{}".format(database_id)

    def create_database(
        self,
        id,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        offer_throughput=None,
        request_options=None
    ):
        # type: (str, str, Dict[str, str], Dict[str, str], bool, int, Dict[str, Any]) -> Database
        """Create a new database with the given ID (name).

        :param id: ID (name) of the database to create.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param offer_throughput: The provisioned throughput for this offer.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`Database` instance representing the new database.
        :raises `HTTPFailure`: If database with the given ID already exists.

        .. literalinclude:: ../../examples/examples.py
            :start-after: [START create_database]
            :end-before: [END create_database]
            :language: python
            :dedent: 0
            :caption: Create a database in the Cosmos DB account:
            :name: create_database

        """

        if not request_options:
            request_options = {} # type: Dict[str, Any]
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
        database
    ):
        # type: (Union[str, Database, Dict[str, Any]]) -> Database
        """
        Retrieve an existing database with the ID (name) `id`.

        :param database: The ID (name), dict representing the properties or :class:`Database` instance of the database to read.
        :returns: A :class:`Database` instance representing the retrieved database.

        """
        if isinstance(database, Database):
            id_value = database.id
        elif isinstance(database, Mapping):
            id_value = database['id']
        else:
            id_value = database

        return Database(
            self.client_connection,
            id_value
        )

    def get_all_databases(
        self,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        feed_options=None
    ):
        # type: (int, str, Dict[str, str], bool, Dict[str, Any]) -> QueryIterable
        """
        List the databases in a Cosmos DB SQL database account.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of database properties (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if session_token:
            feed_options["sessionToken"] = session_token
        if initial_headers:
            feed_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.ReadDatabases(
            options=feed_options
        )

    def query_databases(
        self,
        query=None,
        parameters=None,
        enable_cross_partition_query=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
        feed_options=None
    ):
        # type: (str, List[str], bool, int, str, Dict[str,str], bool, Dict[str, Any]) -> QueryIterable

        """
        Query the databases in a Cosmos DB SQL database account.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of database properties (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if session_token:
            feed_options["sessionToken"] = session_token
        if initial_headers:
            feed_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics

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
                options=feed_options
            )
        else:
            return self.client_connection.ReadDatabases(options=feed_options)

    def delete_database(
        self,
        database,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        request_options=None
    ):
        # type: (Union[str, Database, Dict[str, Any]], str, Dict[str, str], Dict[str, str], bool, Dict[str, Any]) -> None
        """
        Delete the database with the given ID (name).

        :param database: The ID (name), dict representing the properties or :class:`Database` instance of the database to delete.
        :param session_token: Token for use with Session consistency.
        :param initial_headers: Initial headers to be sent as part of the request.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param request_options: Dictionary of additional properties to be used for the request.
        :raise HTTPFailure: If the database couldn't be deleted.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        database_link = self._get_database_link(database)
        self.client_connection.DeleteDatabase(database_link, options=request_options)

    def get_database_account(self):
        # type: () -> DatabaseAccount
        """
        Retrieve the database account information.

        :returns: A :class:`DatabaseAccount` instance representing the Cosmos DB Database Account.

        """
        return self.client_connection.GetDatabaseAccount()
