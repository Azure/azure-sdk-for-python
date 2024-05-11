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
from datetime import datetime, timezone
import warnings
from typing import Any, Dict, List, Optional, Sequence, Union, Tuple, Mapping, Type, cast
from typing_extensions import Literal

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged

from ._cosmos_client_connection import CosmosClientConnection
from ._base import (
    build_options,
    validate_cache_staleness_value,
    _deserialize_throughput,
    _replace_throughput,
    GenerateGuidId,
    _set_properties_cache
)
from .exceptions import CosmosResourceNotFoundError
from .http_constants import StatusCodes
from .offer import Offer, ThroughputProperties
from .scripts import ScriptsProxy
from .partition_key import (
    NonePartitionKeyValue,
    PartitionKey,
    _Empty,
    _Undefined,
    _return_undefined_or_empty_partition_key
)

__all__ = ("ContainerProxy",)

# pylint: disable=too-many-lines
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

PartitionKeyType = Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]]  # pylint: disable=line-too-long


class ContainerProxy:  # pylint: disable=too-many-public-methods
    """An interface to interact with a specific DB Container.

    This class should not be instantiated directly. Instead, use the
    :func:`~azure.cosmos.database.DatabaseProxy.get_container_client` method to get an existing
    container, or the :func:`~azure.cosmos.database.DatabaseProxy.create_container` method to create a
    new container.

    A container in an Azure Cosmos DB SQL API database is a collection of
    documents, each of which is represented as an Item.

    :ivar str id: ID (name) of the container.
    :ivar str container_link: The URL path of the container.
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        database_link: str,
        id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        self.id = id
        self.container_link = "{}/colls/{}".format(database_link, self.id)
        self.client_connection = client_connection
        self._is_system_key: Optional[bool] = None
        self._scripts: Optional[ScriptsProxy] = None
        if properties:
            self.client_connection._set_container_properties_cache(self.container_link,
                                                                   _set_properties_cache(properties))  # pylint: disable=protected-access, line-too-long

    def __repr__(self) -> str:
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    def _get_properties(self) -> Dict[str, Any]:
        if self.container_link not in self.client_connection._container_properties_cache:  # pylint: disable=protected-access, line-too-long
            self.read()
        return self.client_connection._container_properties_cache[self.container_link]  # pylint: disable=protected-access, line-too-long

    @property
    def is_system_key(self) -> bool:
        if self._is_system_key is None:
            properties = self._get_properties()
            self._is_system_key = (
                properties["partitionKey"]["systemKey"] if "systemKey" in properties["partitionKey"] else False
            )
        return self._is_system_key

    @property
    def scripts(self) -> ScriptsProxy:
        if self._scripts is None:
            self._scripts = ScriptsProxy(self.client_connection, self.container_link, self.is_system_key)
        return self._scripts

    def _get_document_link(self, item_or_link: Union[str, Mapping[str, Any]]) -> str:
        if isinstance(item_or_link, str):
            return "{}/docs/{}".format(self.container_link, item_or_link)
        return item_or_link["_self"]

    def _get_conflict_link(self, conflict_or_link: Union[str, Mapping[str, Any]]) -> str:
        if isinstance(conflict_or_link, str):
            return "{}/conflicts/{}".format(self.container_link, conflict_or_link)
        return conflict_or_link["_self"]

    def _set_partition_key(
        self,
        partition_key: PartitionKeyType
    ) -> Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined]:
        if partition_key == NonePartitionKeyValue:
            return _return_undefined_or_empty_partition_key(self.is_system_key)
        return cast(Union[str, int, float, bool, List[Union[str, int, float, bool]]], partition_key)

    @distributed_trace
    def read(  # pylint:disable=docstring-missing-param
        self,
        populate_query_metrics: Optional[bool] = None,
        populate_partition_key_range_statistics: Optional[bool] = None,
        populate_quota_info: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Read the container properties.

        :param bool populate_partition_key_range_statistics: Enable returning partition key
            range statistics in response headers.
        :param bool populate_quota_info: Enable returning collection storage quota information in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: dict[str, Any]
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if priority is not None:
            kwargs['priority'] = priority
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        request_options = build_options(kwargs)
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info
        container = self.client_connection.ReadContainer(self.container_link, options=request_options, **kwargs)
        # Only cache Container Properties that will not change in the lifetime of the container
        self.client_connection._set_container_properties_cache(self.container_link, _set_properties_cache(container))  # pylint: disable=protected-access, line-too-long
        return container

    @distributed_trace
    def read_item(  # pylint:disable=docstring-missing-param
        self,
        item: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        populate_query_metrics: Optional[bool] = None,
        post_trigger_include: Optional[str] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the item to retrieve.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
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
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        request_options = build_options(kwargs)

        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        if max_integrated_cache_staleness_in_ms is not None:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            request_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        return self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)

    @distributed_trace
    def read_all_items(  # pylint:disable=docstring-missing-param
        self,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List all the items in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[Dict[str, Any]]
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
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
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms

        if hasattr(response_hook, "clear"):
            response_hook.clear()

        items = self.client_connection.ReadItems(
            collection_link=self.container_link, feed_options=feed_options, response_hook=response_hook, **kwargs)
        if response_hook:
            response_hook(self.client_connection.last_response_headers, items)
        return items

    @distributed_trace
    def query_items_change_feed(
        self,
        partition_key_range_id: Optional[str] = None,
        is_start_from_beginning: bool = False,
        continuation: Optional[str] = None,
        max_item_count: Optional[int] = None,
        *,
        start_time: Optional[datetime] = None,
        partition_key: Optional[PartitionKeyType] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :param str partition_key_range_id: ChangeFeed requests can be executed against specific partition key ranges.
            This is used to process the change feed in parallel across multiple consumers.
        :param bool is_start_from_beginning: Get whether change feed should start from
            beginning (true) or from current (false). By default, it's start from current (false).
        :param max_item_count: Max number of items to be returned in the enumeration operation.
        :param str continuation: e_tag value to be used as continuation for reading change feed.
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword ~datetime.datetime start_time: Specifies a point of time to start change feed. Provided value will be
            converted to UTC. This value will be ignored if `is_start_from_beginning` is set to true.
        :keyword partition_key: partition key at which ChangeFeed requests are targeted.
        :paramtype partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        if priority is not None:
            kwargs['priority'] = priority
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if partition_key_range_id is not None:
            feed_options["partitionKeyRangeId"] = partition_key_range_id
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
        if is_start_from_beginning is not None:
            feed_options["isStartFromBeginning"] = is_start_from_beginning
        if start_time is not None and is_start_from_beginning is False:
            feed_options["startTime"] = start_time.astimezone(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
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
    def query_items(  # pylint:disable=docstring-missing-param
        self,
        query: str,
        parameters: Optional[List[Dict[str, object]]] = None,
        partition_key: Optional[PartitionKeyType] = None,
        enable_cross_partition_query: Optional[bool] = None,
        max_item_count: Optional[int] = None,
        enable_scan_in_query: Optional[bool] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        populate_index_metrics: Optional[bool] = None,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        continuation_token_limit: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :type parameters: [List[Dict[str, object]]]
        :param partition_key: partition key at which the query request is targeted.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :param bool enable_cross_partition_query: Allows sending of more than one request to
            execute the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :param bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :param bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword int continuation_token_limit: The size limit in kb of the response continuation token in the query
            response. Valid values are positive integers.
            A value of 0 is the same as not passing a value (default no limit).
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool populate_index_metrics: Used to obtain the index metrics to understand how the query engine used
            existing indexes and how it could use potential new indexes. Please note that this options will incur
            overhead, so it should be enabled only when debugging slow queries.
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
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            feed_options["populateQueryMetrics"] = populate_query_metrics
        if populate_index_metrics is not None:
            feed_options["populateIndexMetrics"] = populate_index_metrics
        if partition_key is not None:
            if self.__is_prefix_partitionkey(partition_key):
                kwargs["isPrefixPartitionQuery"] = True
                properties = self._get_properties()
                kwargs["partitionKeyDefinition"] = properties["partitionKey"]
                kwargs["partitionKeyDefinition"]["partition_key"] = partition_key
            else:
                feed_options["partitionKey"] = self._set_partition_key(partition_key)
        if enable_scan_in_query is not None:
            feed_options["enableScanInQuery"] = enable_scan_in_query
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        correlated_activity_id = GenerateGuidId()
        feed_options["correlatedActivityId"] = correlated_activity_id
        if continuation_token_limit is not None:
            feed_options["responseContinuationTokenLimitInKb"] = continuation_token_limit
        if hasattr(response_hook, "clear"):
            response_hook.clear()

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

    def __is_prefix_partitionkey(
        self, partition_key: PartitionKeyType
    ) -> bool:
        properties = self._get_properties()
        pk_properties = properties["partitionKey"]
        partition_key_definition = PartitionKey(path=pk_properties["paths"], kind=pk_properties["kind"])
        if partition_key_definition.kind != "MultiHash":
            return False
        if isinstance(partition_key, list) and len(partition_key_definition['paths']) == len(partition_key):
            return False
        return True

    @distributed_trace
    def replace_item(  # pylint:disable=docstring-missing-param
        self,
        item: Union[str, Mapping[str, Any]],
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Replaces the specified item if it exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be replaced.
        :type item: Union[str, Dict[str, Any]]
        :param body: A dict representing the item to replace.
        :type body: Dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: A dict representing the item after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The replace operation failed or the item with
            given id does not exist.
        :rtype: Dict[str, Any]
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
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.ReplaceItem(
            document_link=item_link, new_document=body, options=request_options, **kwargs
        )

    @distributed_trace
    def upsert_item(  # pylint:disable=docstring-missing-param
        self,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool]=None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Insert or update the specified item.

        If the item already exists in the container, it is replaced. If the item
        does not already exist, it is inserted.

        :param body: A dict-like object representing the item to update or insert.
        :type body: Dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: A dict representing the upserted item.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item could not be upserted.
        :rtype: Dict[str, Any]
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
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        return self.client_connection.UpsertItem(
            database_or_container_link=self.container_link,
            document=body,
            options=request_options,
            **kwargs
        )

    @distributed_trace
    def create_item(  # pylint:disable=docstring-missing-param
        self,
        body: Dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        indexing_directive: Optional[int] = None,
        *,
        enable_automatic_id_generation: bool = False,
        session_token: Optional[str] = None,
        initial_headers: Optional[Dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Create an item in the container.

        To update or replace an existing item, use the
        :func:`ContainerProxy.upsert_item` method.

        :param body: A dict-like object representing the item to create.
        :type body: Dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :param indexing_directive: Enumerates the possible values to indicate whether the document should
            be omitted from indexing. Possible values include: 0 for Default, 1 for Exclude, or 2 for Include.
        :type indexing_directive: Union[int, ~azure.cosmos.documents.IndexingDirective]
        :keyword bool enable_automatic_id_generation: Enable automatic id generation if no id present.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :returns: A dict representing the new item.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :rtype: Dict[str, Any]
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
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                UserWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive

        return self.client_connection.CreateItem(
            database_or_container_link=self.container_link, document=body, options=request_options, **kwargs)

    @distributed_trace
    def patch_item(
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
        **kwargs: Any
    ) -> Dict[str, Any]:
        """ Patches the specified item with the provided operations if it
         exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be patched.
        :type item: Union[str, Dict[str, Any]]
        :param partition_key: The partition key of the object to patch.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
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
        :returns: A dict representing the item after the patch operations went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The patch operations failed or the item with
            given id does not exist.
        :rtype: dict[str, Any]
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
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if filter_predicate is not None:
            request_options["filterPredicate"] = filter_predicate

        item_link = self._get_document_link(item)
        return self.client_connection.PatchItem(
            document_link=item_link, operations=patch_operations, options=request_options, **kwargs)

    @distributed_trace
    def execute_item_batch(
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
    ) -> List[Dict[str, Any]]:
        """ Executes the transactional batch for the specified partition key.

        :param batch_operations: The batch of operations to be executed.
        :type batch_operations: List[Tuple[Any]]
        :param partition_key: The partition key value of the batch operations.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
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
        :returns: A list representing the item after the batch operations went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The batch failed to execute.
        :raises ~azure.cosmos.exceptions.CosmosBatchOperationError: A transactional batch operation failed in the batch.
        :rtype: List[Dict[str, Any]]
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
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        request_options["disableAutomaticIdGeneration"] = True

        return self.client_connection.Batch(
            collection_link=self.container_link, batch_operations=batch_operations, options=request_options, **kwargs)

    @distributed_trace
    def delete_item(  # pylint:disable=docstring-missing-param
        self,
        item: Union[Mapping[str, Any], str],
        partition_key: PartitionKeyType,
        populate_query_metrics: Optional[bool] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        *,
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
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The item wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The item does not exist in the container.
        :rtype: None
        """
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
        request_options = build_options(kwargs)
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
        self.client_connection.DeleteItem(document_link=document_link, options=request_options, **kwargs)

    @distributed_trace
    def read_offer(self, **kwargs: Any) -> Offer:
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
    def get_throughput(self, **kwargs: Any) -> ThroughputProperties:
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

        return _deserialize_throughput(throughput=throughput_properties)

    @distributed_trace
    def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the container's throughput.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :param throughput: The throughput to be set.
        :type throughput: Union[int, ThroughputProperties]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: ThroughputProperties for the container, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be updated.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
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
        _replace_throughput(throughput=throughput, new_throughput_properties=new_throughput_properties)
        data = self.client_connection.ReplaceOffer(
            offer_link=throughput_properties[0]["_self"], offer=throughput_properties[0], **kwargs)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)

    @distributed_trace
    def list_conflicts(
        self,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """List all the conflicts in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
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
        query: str,
        parameters: Optional[List[Dict[str, object]]] = None,
        enable_cross_partition_query: Optional[bool] = None,
        partition_key: Optional[PartitionKeyType] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[Dict[str, Any]]:
        """Return all conflicts matching a given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: List[Dict[str, object]]
        :param bool enable_cross_partition_query: Allows sending of more than one request to execute
            the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param partition_key: Specifies the partition key value for the item.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of conflicts (dicts).
        :rtype: Iterable[Dict[str, Any]]
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
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )
        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
        return result

    @distributed_trace
    def get_conflict(
        self,
        conflict: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get the conflict identified by `conflict`.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the retrieved conflict.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given conflict couldn't be retrieved.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)

        return self.client_connection.ReadConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )

    @distributed_trace
    def delete_conflict(
        self,
        conflict: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        **kwargs: Any
    ) -> None:
        """Delete a specified conflict from the container.

        If the conflict does not already exist in the container, an exception is raised.

        :param conflict: The ID (name) or dict representing the conflict to be deleted.
        :type conflict: Union[str, Dict[str, Any]]
        :param partition_key: Partition key for the conflict to delete.
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The conflict wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The conflict does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        if partition_key is not None:
            request_options["partitionKey"] = self._set_partition_key(partition_key)

        self.client_connection.DeleteConflict(
            conflict_link=self._get_conflict_link(conflict), options=request_options, **kwargs
        )

    @distributed_trace
    def delete_all_items_by_partition_key(
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
        :type partition_key: Union[str, int, float, bool, List[Union[str, int, float, bool]]]
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
        request_options = build_options(kwargs)
        # regardless if partition key is valid we set it as invalid partition keys are set to a default empty value
        request_options["partitionKey"] = self._set_partition_key(partition_key)

        self.client_connection.DeleteAllItemsByPartitionKey(
            collection_link=self.container_link, options=request_options, **kwargs)
