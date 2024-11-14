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
import warnings
from datetime import datetime
from typing import Any, Dict, Mapping, Optional, Sequence, Type, Union, List, Tuple, cast, overload, AsyncIterable
from typing_extensions import Literal

from azure.core import MatchConditions
from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async  # type: ignore

from ._cosmos_client_connection_async import CosmosClientConnection
from ._scripts import ScriptsProxy
from .._base import (
    build_options as _build_options,
    validate_cache_staleness_value,
    _deserialize_throughput,
    _replace_throughput,
    GenerateGuidId,
    _set_properties_cache
)
from .._change_feed.feed_range_internal import FeedRangeInternalEpk
from .._cosmos_responses import CosmosDict, CosmosList
from .._routing.routing_range import Range
from .._session_token_helpers import get_latest_session_token
from ..offer import ThroughputProperties
from ..partition_key import (
    NonePartitionKeyValue,
    _return_undefined_or_empty_partition_key,
    _Empty,
    _Undefined, PartitionKey
)

__all__ = ("ContainerProxy",)

# pylint: disable=protected-access, too-many-lines
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=too-many-public-methods

PartitionKeyType = Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]]  # pylint: disable=line-too-long


class ContainerProxy:
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
        id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        self.client_connection = client_connection
        self.id = id
        self.database_link = database_link
        self.container_link = "{}/colls/{}".format(database_link, self.id)
        self._is_system_key: Optional[bool] = None
        self._scripts: Optional[ScriptsProxy] = None
        if properties:
            self.client_connection._set_container_properties_cache(self.container_link,
                                                                   _set_properties_cache(properties))

    def __repr__(self) -> str:
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    async def _get_properties(self) -> Dict[str, Any]:
        if self.container_link not in self.client_connection._container_properties_cache:
            await self.read()
        return self.client_connection._container_properties_cache[self.container_link]

    @property
    async def is_system_key(self) -> bool:
        if self._is_system_key is None:
            properties = await self._get_properties()
            self._is_system_key = (
                properties["partitionKey"]["systemKey"] if "systemKey" in properties["partitionKey"] else False
            )
        return self._is_system_key

    def __get_client_container_caches(self) -> Dict[str, Dict[str, Any]]:
        return self.client_connection._container_properties_cache

    @property
    def scripts(self) -> ScriptsProxy:
        if self._scripts is None:
            self._scripts = ScriptsProxy(self, self.client_connection, self.container_link)
        return self._scripts

    def _get_document_link(self, item_or_link: Union[str, Mapping[str, Any]]) -> str:
        if isinstance(item_or_link, str):
            return "{}/docs/{}".format(self.container_link, item_or_link)
        return item_or_link["_self"]

    def _get_conflict_link(self, conflict_or_link: Union[str, Mapping[str, Any]]) -> str:
        if isinstance(conflict_or_link, str):
            return "{}/conflicts/{}".format(self.container_link, conflict_or_link)
        return conflict_or_link["_self"]

    async def _set_partition_key(
        self,
        partition_key: PartitionKeyType
    ) -> Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined]:
        if partition_key == NonePartitionKeyValue:
            return _return_undefined_or_empty_partition_key(await self.is_system_key)
        return cast(Union[str, int, float, bool, List[Union[str, int, float, bool]]], partition_key)

    async def _get_epk_range_for_partition_key(self, partition_key_value: PartitionKeyType) -> Range:

        container_properties = await self._get_properties()
        partition_key_definition = container_properties["partitionKey"]
        partition_key = PartitionKey(path=partition_key_definition["paths"], kind=partition_key_definition["kind"])

        return partition_key._get_epk_range_for_partition_key(partition_key_value)

    @distributed_trace_async
    async def read(
        self,
        *,
        populate_partition_key_range_statistics: Optional[bool] = None,
        populate_quota_info: Optional[bool] = None,
        session_token: Optional[str] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        initial_headers: Optional[Dict[str, str]] = None,
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
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: Dict[str, Any]
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if priority is not None:
            kwargs['priority'] = priority
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = _build_options(kwargs)
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info
        container = await self.client_connection.ReadContainer(self.container_link, options=request_options, **kwargs)
        # Only cache Container Properties that will not change in the lifetime of the container
        self.client_connection._set_container_properties_cache(self.container_link, _set_properties_cache(container))  # pylint: disable=protected-access, line-too-long
        return container

    @distributed_trace_async
    async def create_item(
        self,
        body: Dict[str, Any],
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        indexing_directive: Optional[int] = None,
        enable_automatic_id_generation: bool = False,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        **kwargs: Any
    ) -> CosmosDict:
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
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip
            sending response payloads. When not specified explicitly here, the default value will be determined from
            client-level options.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :returns: A CosmosDict representing the new item. The dict will be empty if `no_response` is specified.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if no_response is not None:
            kwargs['no_response'] = no_response
        request_options = _build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = await self.client_connection.CreateItem(
            database_or_container_link=self.container_link, document=body, options=request_options, **kwargs
        )
        return result

    @distributed_trace_async
    async def read_item(
        self,
        item: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        *,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the item to retrieve.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item couldn't be retrieved.
        :returns: A CosmosDict representing the retrieved item.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]

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
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        request_options = _build_options(kwargs)

        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        if max_integrated_cache_staleness_in_ms is not None:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            request_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        return await self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)

    @distributed_trace
    def read_all_items(
        self,
        *,
        max_item_count: Optional[int] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List all the items in the container.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        response_hook = kwargs.pop('response_hook', None)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        if hasattr(response_hook, "clear"):
            response_hook.clear()
        if self.container_link in self.__get_client_container_caches():
            feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        items = self.client_connection.ReadItems(
            collection_link=self.container_link, feed_options=feed_options, response_hook=response_hook, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, items)
        return items

    @distributed_trace
    def query_items(
        self,
        query: str,
        *,
        parameters: Optional[List[Dict[str, object]]] = None,
        partition_key: Optional[PartitionKeyType] = None,
        max_item_count: Optional[int] = None,
        enable_scan_in_query: Optional[bool] = None,
        populate_query_metrics: Optional[bool] = None,
        populate_index_metrics: Optional[bool] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        continuation_token_limit: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword partition_key: Specifies the partition key value for the item. If none is provided,
            a cross-partition query will be executed.
        :paramtype partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :keyword bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword bool populate_index_metrics: Used to obtain the index metrics to understand how the query engine used
            existing indexes and how it could use potential new indexes. Please note that this options will incur
            overhead, so it should be enabled only when debugging slow queries.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :keyword int continuation_token_limit: The size limit in kb of the response continuation token in the query
            response. Valid values are positive integers.
            A value of 0 is the same as not passing a value (default no limit).
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
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
        response_hook = kwargs.pop('response_hook', None)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        feed_options = _build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics
        if populate_index_metrics is not None:
            feed_options["populateIndexMetrics"] = populate_index_metrics
        if enable_scan_in_query is not None:
            feed_options["enableScanInQuery"] = enable_scan_in_query
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
            kwargs["containerProperties"] = self._get_properties
        else:
            feed_options["enableCrossPartitionQuery"] = True
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        correlated_activity_id = GenerateGuidId()
        feed_options["correlatedActivityId"] = correlated_activity_id
        if continuation_token_limit is not None:
            feed_options["responseContinuationTokenLimitInKb"] = continuation_token_limit
        if hasattr(response_hook, "clear"):
            response_hook.clear()
        if self.container_link in self.__get_client_container_caches():
            feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        items = self.client_connection.QueryItems(
            database_or_container_link=self.container_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            partition_key=partition_key,
            response_hook=response_hook,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, items)
        return items

    @overload
    def query_items_change_feed(
            self,
            *,
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            partition_key: PartitionKeyType,
            priority: Optional[Literal["High", "Low"]] = None,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :type start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword partition_key: The partition key that is used to define the scope
            (logical partition or a subset of a container)
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            feed_range: Dict[str, Any],
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword Dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :type start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            continuation: str,
            max_item_count: Optional[int] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword str continuation: The continuation token retrieved from previous response.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        # pylint: enable=line-too-long
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed in the entire container,
         in the order in which they were modified.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :type start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        ...

    @distributed_trace
    def query_items_change_feed( # pylint: disable=unused-argument
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:

        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword str continuation: The continuation token retrieved from previous response.
        :keyword Dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword partition_key: The partition key that is used to define the scope
            (logical partition or a subset of a container)
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :type start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An AsyncItemPaged of items (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        # pylint: disable=too-many-statements
        if kwargs.get("priority") is not None:
            kwargs['priority'] = kwargs['priority']
        feed_options = _build_options(kwargs)

        change_feed_state_context = {}
        # Back compatibility with deprecation warnings for partition_key_range_id
        if kwargs.get("partition_key_range_id") is not None:
            warnings.warn(
                "partition_key_range_id is deprecated. Please pass in feed_range instead.",
                DeprecationWarning
            )

            change_feed_state_context["partitionKeyRangeId"] = kwargs.pop('partition_key_range_id')

        # Back compatibility with deprecation warnings for is_start_from_beginning
        if kwargs.get("is_start_from_beginning") is not None:
            warnings.warn(
                "is_start_from_beginning is deprecated. Please pass in start_time instead.",
                DeprecationWarning
            )

            if kwargs.get("start_time") is not None:
                raise ValueError("is_start_from_beginning and start_time are exclusive, please only set one of them")

            is_start_from_beginning = kwargs.pop('is_start_from_beginning')
            if is_start_from_beginning is True:
                change_feed_state_context["startTime"] = "Beginning"

        # parse start_time
        if kwargs.get("start_time") is not None:
            start_time = kwargs.pop('start_time')
            if not isinstance(start_time, (datetime, str)):
                raise TypeError(
                    "'start_time' must be either a datetime object, or either the values 'Now' or 'Beginning'.")
            change_feed_state_context["startTime"] = start_time

        # parse continuation token
        if feed_options.get("continuation") is not None:
            change_feed_state_context["continuation"] = feed_options.pop('continuation')

        if kwargs.get("max_item_count") is not None:
            feed_options["maxItemCount"] = kwargs.pop('max_item_count')

        if kwargs.get("partition_key") is not None:
            change_feed_state_context["partitionKey"] =\
                self._set_partition_key(cast(PartitionKeyType, kwargs.get("partition_key")))
            change_feed_state_context["partitionKeyFeedRange"] = \
                self._get_epk_range_for_partition_key(kwargs.pop('partition_key'))

        if kwargs.get("feed_range") is not None:
            change_feed_state_context["feedRange"] = kwargs.pop('feed_range')

        feed_options["containerProperties"] = self._get_properties()
        feed_options["changeFeedStateContext"] = change_feed_state_context

        response_hook = kwargs.pop('response_hook', None)
        if hasattr(response_hook, "clear"):
            response_hook.clear()

        if self.container_link in self.__get_client_container_caches():
            feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

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
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        **kwargs: Any
    ) -> CosmosDict:
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
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip
            sending response payloads. When not specified explicitly here, the default value will be determined from
            client-level options.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item could not be upserted.
        :returns: A CosmosDict representing the upserted item. The dict will be empty if
            `no_response` is specified.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if no_response is not None:
            kwargs['no_response'] = no_response
        request_options = _build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = await self.client_connection.UpsertItem(
            database_or_container_link=self.container_link,
            document=body,
            options=request_options,
            **kwargs
        )
        return result

    @distributed_trace_async
    async def replace_item(
        self,
        item: Union[str, Mapping[str, Any]],
        body: Dict[str, Any],
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Replaces the specified item if it exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be replaced.
        :type item: Union[str, Dict[str, Any]]
        :param Dict[str, Any] body: A dict representing the item to replace.
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
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip
            sending response payloads. When not specified explicitly here, the default value will be determined from
            client-level options.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The replace operation failed or the item with
            given id does not exist.
        :returns: A CosmosDict representing the item after replace went through. The dict will be empty if `no_response`
            is specified.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        item_link = self._get_document_link(item)
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if no_response is not None:
            kwargs['no_response'] = no_response
        request_options = _build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = await self.client_connection.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options, **kwargs
        )
        return result

    @distributed_trace_async
    async def patch_item(
        self,
        item: Union[str, Dict[str, Any]],
        partition_key: PartitionKeyType,
        patch_operations: List[Dict[str, Any]],
        *,
        filter_predicate: Optional[str] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """ Patches the specified item with the provided operations if it
         exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be patched.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: The partition key of the object to patch.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :param patch_operations: The list of patch operations to apply to the item.
        :type patch_operations: List[Dict[str, Any]]
        :keyword str filter_predicate: conditional filter to apply to Patch operations.
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip
            sending response payloads. When not specified explicitly here, the default value will be determined from
            client-level options.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The patch operations failed or the item with
            given id does not exist.
        :returns: A CosmosDict representing the item after the patch operations went through. The dict will be empty if
            `no_response` is specified.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if priority is not None:
            kwargs['priority'] = priority
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if no_response is not None:
            kwargs['no_response'] = no_response
        request_options = _build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        if filter_predicate is not None:
            request_options["filterPredicate"] = filter_predicate
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        item_link = self._get_document_link(item)
        result = await self.client_connection.PatchItem(
            document_link=item_link, operations=patch_operations, options=request_options, **kwargs)
        return result

    @distributed_trace_async
    async def delete_item(
        self,
        item: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> None:
        """Delete the specified item from the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be deleted.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: Specifies the partition key value for the item.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword match_condition: The match condition to use upon the etag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The item wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The item does not exist in the container.
        :rtype: None
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if priority is not None:
            kwargs['priority'] = priority
        request_options = _build_options(kwargs)
        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        document_link = self._get_document_link(item)
        await self.client_connection.DeleteItem(document_link=document_link, options=request_options, **kwargs)

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
        throughput_properties: List[Dict[str, Any]]
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        options = {"containerRID": properties["_rid"]}
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, options, **kwargs)]

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return _deserialize_throughput(throughput=throughput_properties)

    @distributed_trace_async
    async def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the container's throughput.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :param throughput: The throughput to be set.
        :type throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be updated.
        :returns: ThroughputProperties for the container, updated with new throughput.
        :rtype: ~azure.cosmos.offer.ThroughputProperties
        """
        throughput_properties: List[Dict[str, Any]]
        properties = await self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        options = {"containerRID": properties["_rid"]}
        throughput_properties = [throughput async for throughput in
                                 self.client_connection.QueryOffers(query_spec, options, **kwargs)]

        new_offer = throughput_properties[0].copy()
        _replace_throughput(throughput=throughput, new_throughput_properties=new_offer)
        data = await self.client_connection.ReplaceOffer(offer_link=throughput_properties[0]["_self"],
                                                         offer=throughput_properties[0], **kwargs)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)

    @distributed_trace
    def list_conflicts(
        self,
        *,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List all the conflicts in the container.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of conflicts (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if self.container_link in self.__get_client_container_caches():
            feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = self.client_connection.ReadConflicts(
            collection_link=self.container_link, feed_options=feed_options, **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def query_conflicts(
        self,
        query: str,
        *,
        parameters: Optional[List[Dict[str, object]]] = None,
        partition_key: Optional[PartitionKeyType] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all conflicts matching a given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :paramtype parameters: List[Dict[str, Any]]
        :keyword partition_key: Specifies the partition key value for the item. If none is passed in, a
            cross partition query will be executed.
        :paramtype partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of conflicts (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = _build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        else:
            feed_options["enableCrossPartitionQuery"] = True
        if self.container_link in self.__get_client_container_caches():
            feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = self.client_connection.QueryConflicts(
            collection_link=self.container_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace_async
    async def get_conflict(
        self,
        conflict: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the conflict identified by `conflict`.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given conflict couldn't be retrieved.
        :returns: A dict representing the retrieved conflict.
        :rtype: Dict[str, Any]
        """
        request_options = _build_options(kwargs)
        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
        result = await self.client_connection.ReadConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )
        return result

    @distributed_trace_async
    async def delete_conflict(
        self,
        conflict: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        **kwargs: Any,
    ) -> None:
        """Delete a specified conflict from the container.

        If the conflict does not already exist in the container, an exception is raised.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The conflict wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The conflict does not exist in the container.
        :rtype: None
        """
        request_options = _build_options(kwargs)
        request_options["partitionKey"] = await self._set_partition_key(partition_key)

        await self.client_connection.DeleteConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )

    @distributed_trace_async
    async def delete_all_items_by_partition_key(
        self,
        partition_key: PartitionKeyType,
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        """The delete by partition key feature is an asynchronous, background operation that allows you to delete all
        documents with the same logical partition key value, using the Cosmos SDK. The delete by partition key
        operation is constrained to consume at most 10% of the total
        available RU/s on the container each second. This helps in limiting the resources used by
        this background task.

        :param partition_key: Partition key for the items to be deleted.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :rtype: None
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        request_options = _build_options(kwargs)
        # regardless if partition key is valid we set it as invalid partition keys are set to a default empty value
        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        await self.client_connection.DeleteAllItemsByPartitionKey(collection_link=self.container_link,
                                                                  options=request_options, **kwargs)

    @distributed_trace_async
    async def execute_item_batch(
        self,
        batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ...]], Tuple[str, Tuple[Any, ...], Dict[str, Any]]]],
        partition_key: PartitionKeyType,
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> CosmosList:
        """ Executes the transactional batch for the specified partition key.

        :param batch_operations: The batch of operations to be executed.
        :type batch_operations: List[Tuple[Any]]
        :param partition_key: The partition key value of the batch operations.
        :type partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]]]
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A CosmosList representing the items after the batch operations went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The batch failed to execute.
        :raises ~azure.cosmos.exceptions.CosmosBatchOperationError: A transactional batch operation failed in the batch.
        :rtype: ~azure.cosmos.CosmosList[Dict[str, Any]]
        """
        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if etag is not None:
            kwargs['etag'] = etag
        if match_condition is not None:
            kwargs['match_condition'] = match_condition
        if priority is not None:
            kwargs['priority'] = priority
        request_options = _build_options(kwargs)
        request_options["partitionKey"] = await self._set_partition_key(partition_key)
        request_options["disableAutomaticIdGeneration"] = True
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        return await self.client_connection.Batch(
            collection_link=self.container_link, batch_operations=batch_operations, options=request_options, **kwargs)

    @distributed_trace
    def read_feed_ranges(
            self,
            *,
            force_refresh: bool = False,
            **kwargs: Any
    ) -> AsyncIterable[Dict[str, Any]]:
        """ Obtains a list of feed ranges that can be used to parallelize feed operations.

        :keyword bool force_refresh:
            Flag to indicate whether obtain the list of feed ranges directly from cache or refresh the cache.
        :returns: AsyncIterable representing the feed ranges in base64 encoded string
        :rtype: AsyncIterable[Dict[str, Any]]

        .. warning::
          The structure of the dict representation of a feed range may vary, including which keys
          are present. It therefore should only be treated as an opaque value.

        """
        if force_refresh is True:
            self.client_connection.refresh_routing_map_provider()

        async def get_next(continuation_token:str) -> List[Dict[str, Any]]: # pylint: disable=unused-argument
            partition_key_ranges = \
                await self.client_connection._routing_map_provider.get_overlapping_ranges( # pylint: disable=protected-access
                    self.container_link,
                    # default to full range
                    [Range("", "FF", True, False)],
                    **kwargs)

            feed_ranges = [FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partitionKeyRange)).to_dict()
                       for partitionKeyRange in partition_key_ranges]

            return feed_ranges

        async def extract_data(feed_ranges_response: List[Dict[str, Any]]):
            return None, AsyncList(feed_ranges_response)

        return AsyncItemPaged(
            get_next,
            extract_data
        )

    async def get_latest_session_token(
            self,
            feed_ranges_to_session_tokens: List[Tuple[Dict[str, Any], str]],
            target_feed_range: Dict[str, Any]
    ) -> str:
        """ **provisional** This method is still in preview and may be subject to breaking changes.

        Gets the the most up to date session token from the list of session token and feed
        range tuples for a specific target feed range. The feed range can be obtained from a partition key
        or by reading the container feed ranges. This should only be used if maintaining own session token or else
        the CosmosClient instance will keep track of session token. Session tokens and feed ranges are
        scoped to a container. Only input session tokens and feed ranges obtained from the same container.
        :param feed_ranges_to_session_tokens: List of feed range and session token tuples.
        :type feed_ranges_to_session_tokens: List[Tuple[Dict[str, Any], str]]
        :param target_feed_range: feed range to get most up to date session token.
        :type target_feed_range: Dict[str, Any]
        :returns: a session token
        :rtype: str
        """
        return get_latest_session_token(feed_ranges_to_session_tokens, target_feed_range)

    async def feed_range_from_partition_key(self, partition_key: PartitionKeyType) -> Dict[str, Any]:
        """ Gets the feed range for a given partition key.
        :param partition_key: partition key to get feed range.
        :type partition_key: PartitionKeyType
        :returns: a feed range
        :rtype: Dict[str, Any]

        .. warning::
          The structure of the dict representation of a feed range may vary, including which keys
          are present. It therefore should only be treated as an opaque value.

        """
        return FeedRangeInternalEpk(await self._get_epk_range_for_partition_key(partition_key)).to_dict()

    async def is_feed_range_subset(self, parent_feed_range: Dict[str, Any],
                                   child_feed_range: Dict[str, Any]) -> bool:
        """Checks if child feed range is a subset of parent feed range.
        :param parent_feed_range: left feed range
        :type parent_feed_range: Dict[str, Any]
        :param child_feed_range: right feed range
        :type child_feed_range: Dict[str, Any]
        :returns: a boolean indicating if child feed range is a subset of parent feed range
        :rtype: bool

        .. warning::
          The structure of the dict representation of a feed range may vary, including which keys
          are present. It therefore should only be treated as an opaque value.

        """
        parent_feed_range_epk = FeedRangeInternalEpk.from_json(parent_feed_range)
        child_feed_range_epk = FeedRangeInternalEpk.from_json(child_feed_range)
        return child_feed_range_epk.get_normalized_range().is_subset(
            parent_feed_range_epk.get_normalized_range())
