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

import six
from .cosmos_client_connection import CosmosClientConnection
from .item import Item
from .errors import HTTPFailure
from .http_constants import StatusCodes
from .offer import Offer
from .scripts import Scripts
from .query_iterable import QueryIterable

from typing import (
    Any,
    List,
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
        self.id = id
        self.properties = properties
        database_link = CosmosClientConnection._get_database_link(database)
        self.container_link = u"{}/colls/{}".format(database_link, self.id)
        self.scripts = Scripts(self.client_connection, self.container_link)

    def _get_document_link(self, item_or_link):
        # type: (Union[Dict[str, Any], str, Item]) -> str
        if isinstance(item_or_link, six.string_types):
            return u"{}/docs/{}".format(self.container_link, item_or_link)
        return cast("str", cast("Item", item_or_link)["_self"])

    def _get_conflict_link(self, id):
        # type: (str) -> str
        return u"{}/conflicts/{}".format(self.container_link, id)

    def get_item(
        self,
        id,
        partition_key,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (str, str, str, Dict[str, Any], bool) -> Item
        """
        Get the item identified by `id`.

        :param id: ID of item to retrieve.
        :param partition_key: Partition key for the item to retrieve.
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
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.ReadItem(
            document_link=doc_link, options=request_options
        )
        return Item(data=result)

    def list_items(
        self,
        enable_cross_partition_query=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        populate_query_metrics=None,
    ):
        # type: (bool, int, str, Dict[str, Any], bool) -> QueryIterable
        """ List all items in the container.

        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param session_token: Token for use with Session consistency.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        """
        request_options = {}  # type: Dict[str, Any]
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

        items = self.client_connection.ReadItems(
            collection_link=self.container_link, feed_options=request_options
        )
        return items

    def query_items_change_feed(
            self,
            partition_key_range_id=None,
            is_start_from_beginning=False,
            continuation=None,
            max_item_count=None
    ):
        """ Get a sorted list of items that were changed, in the order in which they were modified.

        :param partition_key_range_id: ChangeFeed requests can be executed against specific partition key ranges.
        This is used to process the change feed in parallel across multiple consumers.
        :param is_start_from_beginning: Get whether change feed should start from beginning (true) or from current (false).
        By default it's start from current (false).
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        """
        request_options = {}  # type: Dict[str, Any]
        if partition_key_range_id is not None:
            request_options["partitionKeyRangeId"] = partition_key_range_id
        if is_start_from_beginning is not None:
            request_options["isStartFromBeginning"] = is_start_from_beginning
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if continuation is not None:
            request_options["continuation"] = continuation


        items = self.client_connection.QueryItemsChangeFeed(
            self.container_link, options=request_options
        )
        return items

    def query_items(
        self,
        query,
        parameters=None,
        partition_key=None,
        enable_cross_partition_query=None,
        max_item_count=None,
        session_token=None,
        initial_headers=None,
        enable_scan_in_query=None,
        populate_query_metrics=None
    ):
        # type: (str, List, str, bool, int, str, Dict[str, Any], bool, bool) -> QueryIterable
        """Return all results matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param partition_key: Specifies the partition key value for the item.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
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
        if partition_key is not None:
            request_options["partitionKey"] = partition_key
        if enable_scan_in_query is not None:
            request_options["enableScanInQuery"] = enable_scan_in_query

        items = self.client_connection.QueryItems(
            database_or_Container_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
            partition_key=partition_key,
        )
        return items

    def replace_item(
        self,
        item,
        body,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[Item, str], Dict[str, Any], str, Dict[str, Any], AccessCondition, bool) -> Item
        """ Replaces the specified item if it exists in the container.
        :param item: An Item object or link of the item to be replaced.
        :param body: A dict-like object representing the item to replace.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:
        """
        item_link = self._get_document_link(item)
        request_options = {}  # type: Dict[str, Any]
        request_options["disableIdGeneration"] = True
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
        return Item(data=data)

    def upsert_item(
        self,
        body,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Dict[str, Any], str, Dict[str, Any], AccessCondition, bool) -> Item
        """ Insert or update the specified item.

        :param body: A dict-like object representing the item to update or insert.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`:

        If the item already exists in the container, it is replaced. If it does not, it is inserted.
        """
        request_options = {}  # type: Dict[str, Any]
        request_options["disableIdGeneration"] = True
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics is not None:
            request_options["populateQueryMetrics"] = populate_query_metrics

        result = self.client_connection.UpsertItem(
            database_or_Container_link=self.container_link, document=body
        )
        return Item(data=result)

    def create_item(
        self,
        body,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
        pre_trigger_include=None,
        post_trigger_include=None
    ):
        # type: (Dict[str, Any], str, Dict[str, Any], AccessCondition, bool, Any, Any) -> Item
        """ Create an item in the container.

        :param body: A dict-like object representing the item to create.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :returns: The :class:`Item` inserted into the container.
        :raises `HTTPFailure`:

        To update or replace an existing item, use the :func:`Container.upsert_item` method.

        """
        request_options = {}  # type: Dict[str, Any]

        request_options["disableAutomaticIdGeneration"] = True
        if session_token:
            request_options["sessionToken"] = session_token
        if initial_headers:
            request_options["initialHeaders"] = initial_headers
        if access_condition:
            request_options["accessCondition"] = access_condition
        if populate_query_metrics:
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include:
            request_options["postTriggerInclude"] = post_trigger_include

        result = self.client_connection.CreateItem(
            database_or_Container_link=self.container_link,
            document=body,
            options=request_options,
        )
        return Item(data=result)

    def delete_item(
        self,
        item,
        partition_key,
        session_token=None,
        initial_headers=None,
        access_condition=None,
        populate_query_metrics=None,
    ):
        # type: (Union[Item, Dict[str, Any], str], str, str, Dict[str, Any], AccessCondition, bool) -> None
        """ Delete the specified item from the container.

        :param item: The :class:`Item` to delete from the container.
        :param partition_key: Specifies the partition key value for the item.
        :param session_token: Token for use with Session consistency.
        :param access_condition: Conditions Associated with the request.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :raises `HTTPFailure`: The item wasn't deleted successfully. If the item does not exist in the container, a `404` error is returned.

        """
        request_options = {}  # type: Dict[str, Any]
        if partition_key:
            request_options["partitionKey"] = partition_key
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
            raise HTTPFailure(StatusCodes.NOT_FOUND, "Could not find Offer for container " + self.container_link)
        data = offers[0]
        return Offer(
            offer_throughput=offers[0]['content']['offerThroughput'],
            properties=offers[0])

    def replace_throughput(
            self,
            throughput
    ):
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
            raise HTTPFailure(StatusCodes.NOT_FOUND, "Could not find Offer for container " + self.container_link)
        new_offer = offers[0].copy()
        new_offer['content']['offerThroughput'] = throughput
        data = self.client_connection.ReplaceOffer(
            offer_link=offers[0]['_self'],
            offer=offers[0]
        )
        return Offer(
            offer_throughput=data['content']['offerThroughput'],
            properties=data)

    def list_conflicts(
            self,
            max_item_count=None
    ):
        # type: (int) -> Dict[str, Any]
        """ List all conflicts in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadConflicts(
            collection_link=self.container_link,
            feed_options=request_options
        )

    def query_conflicts(
            self,
            query,
            parameters=None,
            enable_cross_partition_query=None,
            partition_key=None,
            max_item_count=None
    ):
        # type: (str, List, bool, bool int) -> QueryIterable
        """Return all conflicts matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param partition_key: Specifies the partition key value for the item.
        :param enable_cross_partition_query: Allow scan on the queries which couldn't be served as indexing was opted out on the requested paths.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count
        if enable_cross_partition_query is not None:
            request_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if partition_key is not None:
            request_options["partitionKey"] = partition_key

        return self.client_connection.QueryConflicts(
            collection_link=self.container_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_conflict(
            self,
            id,
            partition_key
    ):
        # type: (str, str) -> Dict[str, Any]
        """
        Get the conflict identified by `id`.

        :param id: ID of the conflict to be retrieved.
        :param partition_key: Partition key for the conflict to retrieve.
        :returns: The conflict as a dict, if present in the container.

        """
        request_options = {}  # type: Dict[str, Any]
        if partition_key:
            request_options["partitionKey"] = partition_key

        return self.client_connection.ReadConflict(
            conflict_link=self._get_conflict_link(id),
            options=request_options
        )

    def delete_conflcit(self, id, partition_key):
        # type: (str, str) -> None
        """ Delete the specified conflict from the container.

        :param id: Id of the conflict to delete from the container.
        :param partition_key: Partition key for the conflict to delete.
        :raises `HTTPFailure`: The conflict wasn't deleted successfully. If the conflict does not exist in the container, a `404` error is returned.

        """
        request_options = {}  # type: Dict[str, Any]
        if partition_key:
            request_options["partitionKey"] = partition_key

        self.client_connection.DeleteConflict(
            conflict_link=self._get_conflict_link(id),
            options=request_options
        )

