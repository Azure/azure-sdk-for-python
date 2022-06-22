# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

from typing import Any, Dict, Optional, Union, cast, Awaitable
from azure.core.async_paging import AsyncItemPaged

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async  # type: ignore

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options as _build_options, validate_cache_staleness_value
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes
from ..offer import ThroughputProperties
from ._scripts import ScriptsProxy
from ..partition_key import NonePartitionKeyValue

__all__ = ("ContainerProxy",)


# pylint: disable=protected-access
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

class ContainerProxy(object):
    """An interface to interact with a specific DB Container.

    This class should not be instantiated directly. Instead, use the
    :func:`~azure.cosmos.aio.database.DatabaseProxy.get_container_client` method to get an existing
    container, or the :func:`~azure.cosmos.aio.database.DatabaseProxy.create_container` method to create a
    new container.

    A container in an Azure Cosmos DB SQL API database is a collection of
    documents, each of which is represented as an Item.

    :ivar str id: ID (name) of the container
    :ivar str session_token: The session token for the container.
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        database_link: str,
        id: str,  # pylint: disable=redefined-builtin
        properties: Dict[str, Any] = None
    ) -> None:
        self.client_connection = client_connection
        self.id = id
        self._properties = properties
        self.database_link = database_link
        self.container_link = u"{}/colls/{}".format(database_link, self.id)
        self._is_system_key = None
        self._scripts: Optional[ScriptsProxy] = None

    def __repr__(self) -> str:
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    async def _get_properties(self) -> Dict[str, Any]:
        if self._properties is None:
            self._properties = await self.read()
        return self._properties

    @property
    async def is_system_key(self) -> bool:
        if self._is_system_key is None:
            properties = await self._get_properties()
            self._is_system_key = (
                properties["partitionKey"]["systemKey"] if "systemKey" in properties["partitionKey"] else False
            )
        return cast('bool', self._is_system_key)

    @property
    def scripts(self) -> ScriptsProxy:
        if self._scripts is None:
            self._scripts = ScriptsProxy(self, self.client_connection, self.container_link)
        return cast('ScriptsProxy', self._scripts)

    def _get_document_link(self, item_or_link: Union[Dict[str, Any], str]) -> str:
        if isinstance(item_or_link, str):
            return u"{}/docs/{}".format(self.container_link, item_or_link)
        return item_or_link["_self"]

    def _get_conflict_link(self, conflict_or_link: Union[Dict[str, Any], str]) -> str:
        if isinstance(conflict_or_link, str):
            return u"{}/conflicts/{}".format(self.container_link, conflict_or_link)
        return conflict_or_link["_self"]

    def _set_partition_key(self, partition_key) -> Union[str, Awaitable]:
        if partition_key == NonePartitionKeyValue:
            return CosmosClientConnection._return_undefined_or_empty_partition_key(self.is_system_key)
        return partition_key


    @distributed_trace_async
    async def read(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read the container properties.

        :keyword bool populate_partition_key_range_statistics: Enable returning partition key
            range statistics in response headers.
        :keyword bool populate_quota_info: Enable returning collection storage quota information in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: Dict[str, Any]
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        populate_partition_key_range_statistics = kwargs.pop('populate_partition_key_range_statistics', None)
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        populate_quota_info = kwargs.pop('populate_quota_info', None)
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info

        collection_link = self.container_link
        self._properties = await self.client_connection.ReadContainer(
            collection_link, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    @distributed_trace_async
    async def create_item(
        self,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Create an item in the container.

        To update or replace an existing item, use the
        :func:`ContainerProxy.upsert_item` method.

        :param dict[str, str] body: A dict-like object representing the item to create.
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword indexing_directive: Enumerates the possible values to indicate whether the document should
            be omitted from indexing. Possible values include: 0 for Default, 1 for Exclude, or 2 for Include.
        :paramtype indexing_directive: Union[int, ~azure.cosmos.documents.IndexingDirective]
        :keyword bool enable_automatic_id_generation: Enable automatic id generation if no id present.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :returns: A dict representing the new item.
        :rtype: Dict[str, Any]
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        pre_trigger_include = kwargs.pop('pre_trigger_include', None)
        post_trigger_include = kwargs.pop('post_trigger_include', None)
        indexing_directive = kwargs.pop('indexing_directive', None)

        request_options["disableAutomaticIdGeneration"] = not kwargs.pop('enable_automatic_id_generation', False)
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive

        result = await self.client_connection.CreateItem(
            database_or_container_link=self.container_link, document=body, options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def read_item(
        self,
        item: Union[str, Dict[str, Any]],
        partition_key: Union[str, int, float, bool],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the item to retrieve.
        :type partition_key: Union[str, int, float, bool]
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item couldn't be retrieved.
        :returns: Dict representing the item to be retrieved.
        :rtype: Dict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START update_item]
                :end-before: [END update_item]
                :language: python
                :dedent: 0
                :caption: Get an item from the database and update one of its properties:
                :name: update_item
        """
        doc_link = self._get_document_link(item)
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        post_trigger_include = kwargs.pop('post_trigger_include', None)
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        max_integrated_cache_staleness_in_ms = kwargs.pop('max_integrated_cache_staleness_in_ms', None)
        if max_integrated_cache_staleness_in_ms is not None:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            request_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        result = await self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def read_all_items(
        self,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List all the items in the container.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
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
    def query_items(
        self,
        query: Union[str, Dict[str, Any]],
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param Union[str, Dict[str, Any]] query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword partition_key: Specifies the partition key value for the item. If none is provided,
            a cross-partition query will be executed.
        :paramtype partition_key: Union[str, int, float, bool]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :keyword bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        **Provisional** keyword argument max_integrated_cache_staleness_in_ms
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START query_items]
                :end-before: [END query_items]
                :language: python
                :dedent: 0
                :caption: Get all products that have not been discontinued:
                :name: query_items

            .. literalinclude:: ../samples/examples_async.py
                :start-after: [START query_items_param]
                :end-before: [END query_items_param]
                :language: python
                :dedent: 0
                :caption: Parameterized query to get all products that have been discontinued:
                :name: query_items_param
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        populate_query_metrics = kwargs.pop('populate_query_metrics', None)
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics
        enable_scan_in_query = kwargs.pop('enable_scan_in_query', None)
        if enable_scan_in_query is not None:
            feed_options["enableScanInQuery"] = enable_scan_in_query
        partition_key = kwargs.pop('partition_key', None)
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        else:
            feed_options["enableCrossPartitionQuery"] = True
        max_integrated_cache_staleness_in_ms = kwargs.pop('max_integrated_cache_staleness_in_ms', None)
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        if hasattr(response_hook, "clear"):
            response_hook.clear()

        parameters = kwargs.pop('parameters', None)
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
    def query_items_change_feed(
        self,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword bool is_start_from_beginning: Get whether change feed should start from
            beginning (true) or from current (false). By default it's start from current (false).
        :keyword str partition_key_range_id: ChangeFeed requests can be executed against specific partition key
            ranges. This is used to process the change feed in parallel across multiple consumers.
        :keyword str continuation: e_tag value to be used as continuation for reading change feed.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword partition_key: partition key at which ChangeFeed requests are targeted.
        :paramtype partition_key: Union[str, int, float, bool]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        partition_key = kwargs.pop("partition_key", None)
        partition_key_range_id = kwargs.pop("partition_key_range_id", None)
        is_start_from_beginning = kwargs.pop("is_start_from_beginning", False)
        feed_options["isStartFromBeginning"] = is_start_from_beginning
        if partition_key_range_id is not None:
            feed_options["partitionKeyRangeId"] = partition_key_range_id
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        continuation = kwargs.pop('continuation', None)
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

    @distributed_trace_async
    async def upsert_item(
        self,
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Insert or update the specified item.

        If the item already exists in the container, it is replaced. If the item
        does not already exist, it is inserted.

        :param Dict[str, Any] body: A dict-like object representing the item to update or insert.
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item could not be upserted.
        :returns: A dict representing the upserted item.
        :rtype: Dict[str, Any]
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["disableAutomaticIdGeneration"] = True
        pre_trigger_include = kwargs.pop('pre_trigger_include', None)
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        post_trigger_include = kwargs.pop('post_trigger_include', None)
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        result = await self.client_connection.UpsertItem(
            database_or_container_link=self.container_link,
            document=body,
            options=request_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def replace_item(
        self,
        item: Union[str, Dict[str, Any]],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replaces the specified item if it exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be replaced.
        :type item: Union[str, Dict[str, Any]]
        :param Dict[str, Any] body: A dict-like object representing the item to replace.
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The replace failed or the item with
            given id does not exist.
        :returns: A dict representing the item after replace went through.
        :rtype: Dict[str, Any]
        """
        item_link = self._get_document_link(item)
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["disableAutomaticIdGeneration"] = True
        pre_trigger_include = kwargs.pop('pre_trigger_include', None)
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        post_trigger_include = kwargs.pop('post_trigger_include', None)
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        result = await self.client_connection.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def delete_item(
        self,
        item: Union[str, Dict[str, Any]],
        partition_key: Union[str, int, float, bool],
        **kwargs: Any
    ) -> None:
        """Delete the specified item from the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be deleted.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: Specifies the partition key value for the item.
        :type partition_key: Union[str, int, float, bool]
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The item wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The item does not exist in the container.
        :rtype: None
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        pre_trigger_include = kwargs.pop('pre_trigger_include', None)
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        post_trigger_include = kwargs.pop('post_trigger_include', None)
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include

        document_link = self._get_document_link(item)
        result = await self.client_connection.DeleteItem(document_link=document_link, options=request_options, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

    @distributed_trace_async
    async def get_throughput(self, **kwargs: Any) -> ThroughputProperties:
        """Get the ThroughputProperties object for this container.

        If no ThroughputProperties already exists for the container, an exception is raised.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], List[Dict[str, Any]]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be retrieved.
        :returns: ThroughputProperties for the container.
        :rtype: ~azure.cosmos.offer.ThroughputProperties
        """
        response_hook = kwargs.pop('response_hook', None)
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, **kwargs)]
        if len(throughput_properties) == 0:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find ThroughputProperties for container " + self.container_link)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return ThroughputProperties(offer_throughput=throughput_properties[0]["content"]["offerThroughput"],
                                    properties=throughput_properties[0])

    @distributed_trace_async
    async def replace_throughput(self, throughput: int, **kwargs: Any) -> ThroughputProperties:
        """Replace the container's throughput.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :param int throughput: The throughput to be set (an integer).
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be updated.
        :returns: ThroughputProperties for the container, updated with new throughput.
        :rtype: ~azure.cosmos.offer.ThroughputProperties
        """
        response_hook = kwargs.pop('response_hook', None)
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, **kwargs)]
        if len(throughput_properties) == 0:
            raise CosmosResourceNotFoundError(
                status_code=StatusCodes.NOT_FOUND,
                message="Could not find Offer for container " + self.container_link)

        new_offer = throughput_properties[0].copy()
        new_offer["content"]["offerThroughput"] = throughput
        data = await self.client_connection.ReplaceOffer(offer_link=throughput_properties[0]["_self"],
                                                         offer=throughput_properties[0], **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, data)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)

    @distributed_trace
    def list_conflicts(self, **kwargs: Any) -> AsyncItemPaged[Dict[str, Any]]:
        """List all the conflicts in the container.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of conflicts (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
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
            query: Union[str, Dict[str, Any]],
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all conflicts matching a given `query`.

        :param Union[str, Dict[str, Any]] query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword partition_key: Specifies the partition key value for the item. If none is passed in, a
            cross partition query will be executed.
        :paramtype partition_key: Union[str, int, float, bool]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of conflicts (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        max_item_count = kwargs.pop('max_item_count', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        partition_key = kwargs.pop("partition_key", None)
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        else:
            feed_options["enableCrossPartitionQuery"] = True

        parameters = kwargs.pop('parameters', None)
        result = self.client_connection.QueryConflicts(
            collection_link=self.container_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def get_conflict(
            self,
            conflict: Union[str, Dict[str, Any]],
            partition_key: Union[str, int, float, bool],
            **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the conflict identified by `conflict`.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve.
        :type partition_key: Union[str, int, float, bool]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given conflict couldn't be retrieved.
        :returns: A dict representing the retrieved conflict.
        :rtype: Dict[str, Any]
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        result = await self.client_connection.ReadConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def delete_conflict(
            self,
            conflict: Union[str, Dict[str, Any]],
            partition_key: Union[str, int, float, bool],
            **kwargs: Any,
    ) -> None:
        """Delete a specified conflict from the container.

        If the conflict does not already exist in the container, an exception is raised.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve.
        :type partition_key: Union[str, int, float, bool]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The conflict wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The conflict does not exist in the container.
        :rtype: None
        """
        request_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        result = await self.client_connection.DeleteConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
