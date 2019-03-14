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

"""Create, read, update and delete items in the Azure Cosmos DB SQL API service.
"""

from .cosmos_client_connection import CosmosClientConnection
from .query_iterator import QueryResultIterator
from .item import Item
from . import ResponseMetadata
from .errors import CosmosError
from .offer import Offer

from typing import (
    Any,
    List,
    Iterable,
    Dict,
    Union,
    cast
)

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
        database_link = CosmosClientConnection._get_database_link(database)
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
        # type: (bool, bool, int, int, str, Dict[str, Any], bool) -> QueryIterable
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
        return items
        #headers = self.client_connection.last_response_headers
        #for item in [Item(headers=headers, data=item) for item in items]:
        #    yield item

    #TODO: fix feedoptions for change feed
    def query_items_change_feed(self, options=None):
        """ Get a sorted list of items that were changed, in the order in which they were modified.
        """
        items = self.client_connection.QueryItemsChangeFeed(
            self.collection_link, options=options
        )
        return items
        #headers = self.client_connection.last_response_headers
        #for item in items:
        #    yield Item(headers, item)

    #TODO: does ocntainer need osessiontoken
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
        enable_scan_in_query=None,
        populate_query_metrics=None
    ):
        # type: (str, List, str, bool, bool, int, int, str, Dict[str, Any], bool, bool) -> QueryIterable
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
        if partition_key is not None:
            request_options["partitionKey"] = partition_key
        if enable_scan_in_query is not None:
            request_options["enableScanInQuery"] = enable_scan_in_query

        items = self.client_connection.QueryItems(
            database_or_Container_link=self.collection_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
            partition_key=partition_key,
        )
        return items
        #headers = self.client_connection.last_response_headers
        #self.session_token = headers["x-ms-session-token"]
        #items_iterator = iter(items)
        #return QueryResultIterator(items_iterator, metadata=ResponseMetadata(headers))

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
        :param item: An Item object or link of the item to be replaced.
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

    def read_offer(self):
        container = self.client_connection.ReadContainer(self.collection_link)
        link = container['_self']
        query_spec = {
                        'query': 'SELECT r.content FROM root r WHERE r.resource=@link',
                        'parameters': [
                            {'name': '@link', 'value': link}
                        ]
                     }
        offers = list(self.client_connection.QueryOffers(query_spec))
        if (len(offers) <= 0):
            return None
        data = offers[0]
        return Offer(
            offer_throughput=offers[0]['content']['offerThroughput'],
            properties=offers[0])

    def replace_throughput(self, throughput):
        container = self.client_connection.ReadContainer(self.collection_link)
        link = container['_self']
        query_spec = {
                        'query': 'SELECT r.content FROM root r WHERE r.resource=@link',
                        'parameters': [
                            {'name': '@link', 'value': link}
                        ]
                     }
        offers = list(self.client_connection.QueryOffers(query_spec))
        if (len(offers) <= 0):
            return None
        new_offer = offers[0].copy()
        new_offer['content']['offerThoughput'] = throughput
        data = self.client_connection.ReplaceOffer(
            offer_link="offers/{}".format(offers[0]._self)
        )
        return Offer(
            offer_throughput=data['content']['offerThroughput'],
            properties=data)

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
