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

"""Create, read, update and delete items in the Azure Cosmos DB SQL API service.
"""


from typing import Any, Dict, List, Optional, Union, Iterable, cast, overload  # pylint: disable=unused-import

import warnings
from azure.core.tracing.decorator import distributed_trace  # type: ignore

from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options, validate_cache_staleness_value
from .exceptions import CosmosResourceNotFoundError
from .http_constants import StatusCodes
from .offer import ThroughputProperties
from .scripts import ScriptsProxy
from .partition_key import NonePartitionKeyValue

__all__ = ("ContainerProxy",)

# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs


class ContainerProxy(object):
    """An interface to interact with a specific DB Container.

    This class should not be instantiated directly. Instead, use the
    :func:`~azure.cosmos.database.DatabaseProxy.get_container_client` method to get an existing
    container, or the :func:`~azure.cosmos.database.DatabaseProxy.create_container` method to create a
    new container.

    A container in an Azure Cosmos DB SQL API database is a collection of
    documents, each of which is represented as an Item.

    :ivar str id: ID (name) of the container
    :ivar str session_token: The session token for the container.
    """

    def __init__(self, client_connection, database_link, id, properties=None):  # pylint: disable=redefined-builtin
        # type: (CosmosClientConnection, str, str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.id = id
        self._properties = properties
        self.container_link = u"{}/colls/{}".format(database_link, self.id)
        self._is_system_key = None
        self._scripts = None  # type: Optional[ScriptsProxy]

    def __repr__(self):
        # type () -> str
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self._properties = self.read()
        return self._properties

    @property
    def is_system_key(self):
        # type: () -> bool
        if self._is_system_key is None:
            properties = self._get_properties()
            self._is_system_key = (
                properties["partitionKey"]["systemKey"] if "systemKey" in properties["partitionKey"] else False
            )
        return cast('bool', self._is_system_key)

    @property
    def scripts(self):
        # type: () -> ScriptsProxy
        if self._scripts is None:
            self._scripts = ScriptsProxy(self.client_connection, self.container_link, self.is_system_key)
        return cast('ScriptsProxy', self._scripts)

    def _get_document_link(self, item_or_link):
        # type: (Union[Dict[str, Any], str]) -> str
        if isinstance(item_or_link, str):
            return u"{}/docs/{}".format(self.container_link, item_or_link)
        return item_or_link["_self"]

    def _get_conflict_link(self, conflict_or_link):
        # type: (Union[Dict[str, Any], str]) -> str
        if isinstance(conflict_or_link, str):
            return u"{}/conflicts/{}".format(self.container_link, conflict_or_link)
        return conflict_or_link["_self"]

    def _set_partition_key(self, partition_key):
        if partition_key == NonePartitionKeyValue:
            return CosmosClientConnection._return_undefined_or_empty_partition_key(self.is_system_key)
        return partition_key

    @overload
    def read(
        self,
        *,
        populate_partition_key_range_statistics: Optional[bool] = None,
        populate_quota_info: Optional[bool] = None,
        **kwargs
    ):
        ...


    @distributed_trace
    def read(
        self,
        *args,
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Read the container properties.

        :keyword bool populate_partition_key_range_statistics: Enable returning partition key
            range statistics in response headers.
        :keyword bool populate_quota_info: Enable returning collection storage quota information in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        populate_query_metrics = args[0] if args else kwargs.pop('populate_query_metrics', None)
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
        populate_partition_key_range_statistics = args[1] if args and len(args) > 0 else kwargs.pop(
            "populate_partition_key_range_statistics", None)
        populate_quota_info = args[2] if args and len(args) > 1 else kwargs.pop("populate_quota_info", None)
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info

        collection_link = self.container_link
        self._properties = self.client_connection.ReadContainer(
            collection_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    @distributed_trace
    def read_item(
        self,
        item,  # type: Union[str, Dict[str, Any]]
        partition_key,  # type: Any
        populate_query_metrics=None,  # type: Optional[bool]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :param partition_key: Partition key for the item to retrieve.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms:
        The max cache staleness for the integrated cache in milliseconds.
            For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :returns: Dict representing the item to be retrieved.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item couldn't be retrieved.
        :rtype: dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START update_item]
                :end-before: [END update_item]
                :language: python
                :dedent: 0
                :caption: Get an item from the database and update one of its properties:
                :name: update_item
        """
        doc_link = self._get_document_link(item)
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        max_integrated_cache_staleness_in_ms = kwargs.pop('max_integrated_cache_staleness_in_ms', None)
        if max_integrated_cache_staleness_in_ms is not None:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            request_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        result = self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def read_all_items(
        self,
        max_item_count=None,  # type: Optional[int]
        populate_query_metrics=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable[Dict[str, Any]]
        """List all the items in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms:
        The max cache staleness for the integrated cache in milliseconds.
            For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :returns: An Iterable of items (dicts).
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
        max_integrated_cache_staleness_in_ms = kwargs.pop('max_integrated_cache_staleness_in_ms', None)
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        if hasattr(response_hook, "clear"):
            response_hook.clear()

        items = self.client_connection.ReadItems(
            collection_link=self.container_link, feed_options=feed_options, response_hook=response_hook, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, items)
        return items

    @distributed_trace
    def query_items_change_feed(
        self,
        partition_key_range_id=None,  # type: Optional[str]
        is_start_from_beginning=False,  # type: bool
        continuation=None,  # type: Optional[str]
        max_item_count=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable[Dict[str, Any]]
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :param partition_key_range_id: ChangeFeed requests can be executed against specific partition key ranges.
            This is used to process the change feed in parallel across multiple consumers.
        :param partition_key: partition key at which ChangeFeed requests are targetted.
        :param is_start_from_beginning: Get whether change feed should start from
            beginning (true) or from current (false). By default it's start from current (false).
        :param continuation: e_tag value to be used as continuation for reading change feed.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key_range_id is not None:
            feed_options["partitionKeyRangeId"] = partition_key_range_id
        partition_key = kwargs.pop("partitionKey", None)
        if partition_key is not None:
            feed_options["partitionKey"] = partition_key
        if is_start_from_beginning is not None:
            feed_options["isStartFromBeginning"] = is_start_from_beginning
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if continuation is not None:
            feed_options["continuation"] = continuation

        if hasattr(response_hook, "clear"):
            response_hook.clear()

        result = self.client_connection.QueryItemsChangeFeed(
            self.container_link, options=feed_options, response_hook=response_hook, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_items(
        self,
        query,  # type: str
        parameters=None,  # type: Optional[List[Dict[str, object]]]
        partition_key=None,  # type: Optional[Any]
        enable_cross_partition_query=None,  # type: Optional[bool]
        max_item_count=None,  # type: Optional[int]
        enable_scan_in_query=None,  # type: Optional[bool]
        populate_query_metrics=None,  # type: Optional[bool]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable[Dict[str, Any]]
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :param partition_key: Specifies the partition key value for the item.
        :param enable_cross_partition_query: Allows sending of more than one request to
            execute the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :param populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms:
        The max cache staleness for the integrated cache in milliseconds.
            For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :returns: An Iterable of items (dicts).
        :rtype: ItemPaged[Dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items]
                :end-before: [END query_items]
                :language: python
                :dedent: 0
                :caption: Get all products that have not been discontinued:
                :name: query_items

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items_param]
                :end-before: [END query_items_param]
                :language: python
                :dedent: 0
                :caption: Parameterized query to get all products that have been discontinued:
                :name: query_items_param
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        if enable_scan_in_query is not None:
            feed_options["enableScanInQuery"] = enable_scan_in_query
        max_integrated_cache_staleness_in_ms = kwargs.pop('max_integrated_cache_staleness_in_ms', None)
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        if hasattr(response_hook, "clear"):
            response_hook.clear()

        items = self.client_connection.QueryItems(
            database_or_container_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            partition_key=partition_key,
            response_hook=response_hook,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, items)
        return items

    @distributed_trace
    def replace_item(
        self,
        item,  # type: Union[str, Dict[str, Any]]
        body,  # type: Dict[str, Any]
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Replaces the specified item if it exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be replaced.
        :param body: A dict-like object representing the item to replace.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the item after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The replace failed or the item with
            given id does not exist.
        :rtype: dict[str, Any]
        """
        item_link = self._get_document_link(item)
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        result = self.client_connection.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def upsert_item(
        self,
        body,  # type: Dict[str, Any]
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Insert or update the specified item.

        If the item already exists in the container, it is replaced. If the item
        does not already exist, it is inserted.

        :param body: A dict-like object representing the item to update or insert.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the upserted item.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item could not be upserted.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        result = self.client_connection.UpsertItem(
            database_or_container_link=self.container_link,
            document=body,
            options=request_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def create_item(
        self,
        body,  # type: Dict[str, Any]
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        indexing_directive=None,  # type: Optional[Any]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str, Any]
        """Create an item in the container.

        To update or replace an existing item, use the
        :func:`ContainerProxy.upsert_item` method.

        :param body: A dict-like object representing the item to create.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :param indexing_directive: Indicate whether the document should be omitted from indexing.
        :keyword bool enable_automatic_id_generation: Enable automatic id generation if no id present.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the new item.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        request_options["disableAutomaticIdGeneration"] = not kwargs.pop('enable_automatic_id_generation', False)
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive

        result = self.client_connection.CreateItem(
            database_or_container_link=self.container_link, document=body, options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def delete_item(
        self,
        item,  # type: Union[Dict[str, Any], str]
        partition_key,  # type: Any
        populate_query_metrics=None,  # type: Optional[bool]
        pre_trigger_include=None,  # type: Optional[str]
        post_trigger_include=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete the specified item from the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be deleted.
        :param partition_key: Specifies the partition key value for the item.
        :param pre_trigger_include: trigger id to be used as pre operation trigger.
        :param post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str,str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The item wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The item does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        document_link = self._get_document_link(item)
        result = self.client_connection.DeleteItem(document_link=document_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    @distributed_trace
    def read_offer(self, **kwargs):
        # type: (Any) -> Offer
        """Get the ThroughputProperties object for this container.
        If no ThroughputProperties already exist for the container, an exception is raised.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: Throughput for the container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        warnings.warn(
            "read_offer is a deprecated method name, use get_throughput instead",
            DeprecationWarning
        )
        return self.get_throughput(**kwargs)

    @distributed_trace
    def get_throughput(self, **kwargs):
        # type: (Any) -> ThroughputProperties
        """Get the ThroughputProperties object for this container.

        If no ThroughputProperties already exist for the container, an exception is raised.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: Throughput for the container.
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
                message="Could not find ThroughputProperties for container " + self.container_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return ThroughputProperties(offer_throughput=throughput_properties[0]["content"]["offerThroughput"],
                                    properties=throughput_properties[0])

    @distributed_trace
    def replace_throughput(self, throughput, **kwargs):
        # type: (int, Any) -> ThroughputProperties
        """Replace the container's throughput.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :param throughput: The throughput to be set (an integer).
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the container, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be updated.
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
                message="Could not find Offer for container " + self.container_link)
        new_throughput_properties = throughput_properties[0].copy()
        new_throughput_properties["content"]["offerThroughput"] = throughput
        data = self.client_connection.ReplaceOffer(
            offer_link=throughput_properties[0]["_self"], offer=throughput_properties[0], **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)

    @distributed_trace
    def list_conflicts(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
        """List all the conflicts in the container.

        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of conflicts (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadConflicts(
            collection_link=self.container_link, feed_options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_conflicts(
        self,
        query,  # type: str
        parameters=None,  # type: Optional[List[str]]
        enable_cross_partition_query=None,  # type: Optional[bool]
        partition_key=None,  # type: Optional[Any]
        max_item_count=None,  # type: Optional[int]
        **kwargs  # type: Any
    ):
        # type: (...) -> Iterable[Dict[str, Any]]
        """Return all conflicts matching a given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param enable_cross_partition_query: Allows sending of more than one request to execute
            the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param partition_key: Specifies the partition key value for the item.
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of conflicts (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)

        result = self.client_connection.QueryConflicts(
            collection_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def get_conflict(self, conflict, partition_key, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any, Any) -> Dict[str, Any]
        """Get the conflict identified by `conflict`.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :param partition_key: Partition key for the conflict to retrieve.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the retrieved conflict.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given conflict couldn't be retrieved.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)

        result = self.client_connection.ReadConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def delete_conflict(self, conflict, partition_key, **kwargs):
        # type: (Union[str, Dict[str, Any]], Any, Any) -> None
        """Delete a specified conflict from the container.

        If the conflict does not already exist in the container, an exception is raised.

        :param conflict: The ID (name) or dict representing the conflict to be deleted.
        :param partition_key: Partition key for the conflict to delete.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The conflict wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The conflict does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)

        result = self.client_connection.DeleteConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
