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
import threading
import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Callable, cast, Iterable, Mapping, Optional, overload, Sequence, Tuple, Union
from typing_extensions import Literal

from azure.core import MatchConditions
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.cosmos._change_feed.change_feed_utils import add_args_to_kwargs, validate_kwargs

from . import _utils as utils
from ._availability_strategy_config import _validate_hedging_config
from ._base import (_build_properties_cache, _deserialize_throughput, _replace_throughput, build_options,
                    GenerateGuidId, validate_cache_staleness_value)
from ._change_feed.feed_range_internal import FeedRangeInternalEpk
from ._constants import _Constants as Constants
from ._cosmos_client_connection import CosmosClientConnection
from ._cosmos_responses import CosmosDict, CosmosList
from ._routing.routing_range import Range
from ._session_token_helpers import get_latest_session_token
from .exceptions import CosmosHttpResponseError
from .offer import Offer, ThroughputProperties
from .partition_key import (_build_partition_key_from_properties, PartitionKeyType,
                            _return_undefined_or_empty_partition_key, _SequentialPartitionKeyType,
                            NonePartitionKeyValue, NullPartitionKeyValue, PartitionKey)
from .scripts import ScriptsProxy

__all__ = ("ContainerProxy",)
_Unset: Any = object()

# pylint: disable=too-many-lines,disable=protected-access,line-too-long
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=docstring-keyword-should-match-keyword-only
# cspell:ignore rerank reranker reranking

def _get_epk_range_for_partition_key(
        container_properties: dict[str, Any],
        partition_key_value: PartitionKeyType) -> Range:
    partition_key_obj: PartitionKey = _build_partition_key_from_properties(container_properties)
    return partition_key_obj._get_epk_range_for_partition_key(partition_key_value)

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
        properties: Optional[dict[str, Any]] = None
    ) -> None:
        self.id = id
        self.container_link = "{}/colls/{}".format(database_link, self.id)
        self.client_connection = client_connection
        self.container_cache_lock = threading.Lock()
        self._is_system_key: Optional[bool] = None
        self._scripts: Optional[ScriptsProxy] = None
        if properties:
            self.client_connection._set_container_properties_cache(self.container_link,
                                                                   _build_properties_cache(properties,
                                                                                           self.container_link))

    def __repr__(self) -> str:
        return "<ContainerProxy [{}]>".format(self.container_link)[:1024]

    def _get_properties_with_options(self, options: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        kwargs = {}
        if options and "excludedLocations" in options:
            kwargs['excluded_locations'] = options['excludedLocations']
        return self._get_properties(**kwargs)

    def _get_properties(self, **kwargs: Any) -> dict[str, Any]:
        if self.container_link not in self.__get_client_container_caches():
            with self.container_cache_lock:
                if self.container_link not in self.__get_client_container_caches():
                    self.read(**kwargs)
        return self.__get_client_container_caches()[self.container_link]

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
    ) -> PartitionKeyType:
        if partition_key == NonePartitionKeyValue:
            return _return_undefined_or_empty_partition_key(self.is_system_key)
        if partition_key == NullPartitionKeyValue:
            return None
        return cast(Union[str, int, float, bool, list[Union[str, int, float, bool]]], partition_key)

    def __get_client_container_caches(self) -> dict[str, dict[str, Any]]:
        return self.client_connection._container_properties_cache

    @distributed_trace
    def read(  # pylint:disable=docstring-missing-param
        self,
        populate_query_metrics: Optional[bool] = None,
        populate_partition_key_range_statistics: Optional[bool] = None,
        populate_quota_info: Optional[bool] = None,
        *,
        priority: Optional[Literal["High", "Low"]] = None,
        initial_headers: Optional[dict[str, str]] = None,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Read the container properties.

        :param bool populate_partition_key_range_statistics: Enable returning partition key
            range statistics in response headers.
        :param bool populate_quota_info: Enable returning collection storage quota information in response headers.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Raised if the container couldn't be retrieved.
            This includes if the container does not exist.
        :returns: Dict representing the retrieved container.
        :rtype: dict[str, Any]
        """
        session_token = kwargs.get('session_token')
        if session_token is not None:
            warnings.warn(
                "The 'session_token' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        if priority is not None:
            kwargs['priority'] = priority
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
        if populate_partition_key_range_statistics is not None:
            request_options["populatePartitionKeyRangeStatistics"] = populate_partition_key_range_statistics
        if populate_quota_info is not None:
            request_options["populateQuotaInfo"] = populate_quota_info
        container = self.client_connection.ReadContainer(self.container_link, options=request_options, **kwargs)
        # Only cache Container Properties that will not change in the lifetime of the container
        self.client_connection._set_container_properties_cache(self.container_link,  # pylint: disable=protected-access
                                                               _build_properties_cache(container, self.container_link))
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
        initial_headers: Optional[dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Get the item identified by `item`.

        :param item: The ID (name) or dict representing item to retrieve.
        :type item: Union[str, dict[str, Any]]
        :param partition_key: Partition key for the item to retrieve. If the partition key is set to None, it will try
            to fetch an item with a partition key of null. To learn more about using partition keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[dict[str, str], dict[str, Any]], None]
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :returns: A CosmosDict representing the item to be retrieved.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item couldn't be retrieved.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START update_item]
                :end-before: [END update_item]
                :language: python
                :dedent: 0
                :caption: Get an item from the database and update one of its properties:
        """
        doc_link = self._get_document_link(item)
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        if max_integrated_cache_staleness_in_ms is not None:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            request_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
        return self.client_connection.ReadItem(document_link=doc_link, options=request_options, **kwargs)

    @distributed_trace
    def read_items(
            self,
            items: Sequence[Tuple[str, PartitionKeyType]],
            *,
            executor: Optional[ThreadPoolExecutor] = None,
            max_concurrency: Optional[int] = None,
            consistency_level: Optional[str] = None,
            session_token: Optional[str] = None,
            initial_headers: Optional[dict[str, str]] = None,
            excluded_locations: Optional[list[str]] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            throughput_bucket: Optional[int] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            **kwargs: Any
    ) -> CosmosList:
        """Reads multiple items from the container.

        This method is a batched point-read operation. It is more efficient than
        issuing multiple individual point reads.

        :param items: A list of tuples, where each tuple contains an item's ID and partition key.
        :type items: list[Tuple[str, PartitionKeyType]]
        :keyword executor: Optional ThreadPoolExecutor for handling concurrent operations.
                      If not provided, a new executor will be created as needed.
        :keyword int max_concurrency: The maximum number of concurrent operations for the
                      items request. This value is ignored if an executor is provided. If not specified,
                      the default max_concurrency defined by Python's ThreadPoolExecutor will be applied.
        :keyword str consistency_level: The consistency level to use for the request.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The read-many operation failed.
        :returns: A CosmosList containing the retrieved items. Items that were not found are omitted from the list.
        :rtype: ~azure.cosmos.CosmosList
        """

        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if consistency_level is not None:
            kwargs['consistencyLevel'] = consistency_level
        if excluded_locations is not None:
            kwargs['excludedLocations'] = excluded_locations
        if priority is not None:
            kwargs['priority'] = priority
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)

        kwargs['max_concurrency'] = max_concurrency
        query_options = build_options(kwargs)
        self._get_properties_with_options(query_options)
        query_options["enableCrossPartitionQuery"] = True

        item_tuples = [(item_id, self._set_partition_key(pk)) for item_id, pk in items]

        return self.client_connection.read_items(
            collection_link=self.container_link,
            items=item_tuples,
            options=query_options,
            executor=executor,
            **kwargs)



    @distributed_trace
    def read_all_items(  # pylint:disable=docstring-missing-param
        self,
        max_item_count: Optional[int] = None,
        populate_query_metrics: Optional[bool] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[dict[str, str]] = None,
        max_integrated_cache_staleness_in_ms: Optional[int] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List all the items in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        if session_token is not None:
            kwargs['session_token'] = session_token
        if initial_headers is not None:
            kwargs['initial_headers'] = initial_headers
        if priority is not None:
            kwargs['priority'] = priority
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            feed_options["populateQueryMetrics"] = populate_query_metrics
        if max_integrated_cache_staleness_in_ms:
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        if response_hook and hasattr(response_hook, "clear"):
            response_hook.clear()

        self._get_properties_with_options(feed_options)
        feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        items = self.client_connection.ReadItems(
            collection_link=self.container_link, feed_options=feed_options, response_hook=response_hook, **kwargs)
        return items

    @overload
    def query_items_change_feed(
            self,
            *,
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            partition_key: PartitionKeyType,
            priority: Optional[Literal["High", "Low"]] = None,
            mode: Optional[Literal["LatestVersion", "AllVersionsAndDeletes"]] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time:The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :paramtype start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
       :keyword partition_key: The partition key that is used to define the scope
            (logical partition or a subset of a container). If the partition key is set to None, it will try to
            fetch the changes for an item with a partition key value of null. To learn more about using partition keys,
            see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :paramtype partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :paramtype priority: Literal["High", "Low"]
        :keyword mode: The modes to query change feed. If `continuation` was passed, 'mode' argument will be ignored.
            LATEST_VERSION: Query latest items from 'start_time' or 'continuation' token.
            ALL_VERSIONS_AND_DELETES: Query all versions and deleted items from either `start_time='Now'`
            or 'continuation' token.
        :paramtype mode: Literal["LatestVersion", "AllVersionsAndDeletes"]
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            feed_range: dict[str, Any],
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            mode: Optional[Literal["LatestVersion", "AllVersionsAndDeletes"]] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:

        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :paramtype start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :paramtype priority: Literal["High", "Low"]
        :keyword mode: The modes to query change feed. If `continuation` was passed, 'mode' argument will be ignored.
            LATEST_VERSION: Query latest items from 'start_time' or 'continuation' token.
            ALL_VERSIONS_AND_DELETES: Query all versions and deleted items from either `start_time='Now'`
            or 'continuation' token.
        :paramtype mode: Literal["LatestVersion", "AllVersionsAndDeletes"]
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            continuation: str,
            max_item_count: Optional[int] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword str continuation: The continuation token retrieved from previous response. It contains chang feed mode.
        :paramtype continuation: str
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :paramtype priority: Literal["High", "Low"]
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        ...

    @overload
    def query_items_change_feed(
            self,
            *,
            max_item_count: Optional[int] = None,
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            mode: Optional[Literal["LatestVersion", "AllVersionsAndDeletes"]] = None,
            availability_strategy: Optional[dict[str, Any]] = _Unset,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Get a sorted list of items that were changed in the entire container,
         in the order in which they were modified,

        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time:The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :paramtype start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :paramtype priority: Literal["High", "Low"]
        :keyword mode: The modes to query change feed. If `continuation` was passed, 'mode' argument will be ignored.
            LATEST_VERSION: Query latest items from 'start_time' or 'continuation' token.
            ALL_VERSIONS_AND_DELETES: Query all versions and deleted items from either `start_time='Now'`
            or 'continuation' token.
        :paramtype mode: Literal["LatestVersion", "AllVersionsAndDeletes"]
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        ...

    @distributed_trace
    def query_items_change_feed(
            self,
            *args: Any,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Get a sorted list of items that were changed, in the order in which they were modified.

        :keyword str continuation: The continuation token retrieved from previous response. It contains chang feed mode.
        :keyword dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword partition_key: The partition key that is used to define the scope
            (logical partition or a subset of a container). If the partition key is set to None, it will try to
            fetch the changes for an item with a partition key value of null. To learn more about using partition keys,
            see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :paramtype partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword start_time: The start time to start processing chang feed items.
            Beginning: Processing the change feed items from the beginning of the change feed.
            Now: Processing change feed from the current time, so only events for all future changes will be retrieved.
            ~datetime.datetime: processing change feed from a point of time. Provided value will be converted to UTC.
            By default, it is start from current ("Now")
        :paramtype start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword mode: The modes to query change feed. If `continuation` was passed, 'mode' argument will be ignored.
            LATEST_VERSION: Query latest items from 'start_time' or 'continuation' token.
            ALL_VERSIONS_AND_DELETES: Query all versions and deleted items from either `start_time='Now'`
            or 'continuation' token.
        :paramtype mode: Literal["LatestVersion", "AllVersionsAndDeletes"]
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :param Any args: args
        :returns: An Iterable of items (dicts).
        :rtype: Iterable[dict[str, Any]]
        """

        # pylint: disable=too-many-statements
        add_args_to_kwargs(args, kwargs)
        validate_kwargs(kwargs)
        feed_options = build_options(kwargs)

        change_feed_state_context = {}
        if "mode" in kwargs:
            change_feed_state_context["mode"] = kwargs.pop("mode")
        if "partition_key_range_id" in kwargs:
            change_feed_state_context["partitionKeyRangeId"] = kwargs.pop("partition_key_range_id")
        if "is_start_from_beginning" in kwargs and kwargs.pop('is_start_from_beginning') is True:
            change_feed_state_context["startTime"] = "Beginning"
        elif "start_time" in kwargs:
            change_feed_state_context["startTime"] = kwargs.pop("start_time")

        container_properties = self._get_properties_with_options(feed_options)
        if "partition_key" in kwargs:
            partition_key = kwargs.pop("partition_key")
            change_feed_state_context["partitionKey"] = self._set_partition_key(cast(PartitionKeyType, partition_key))
            change_feed_state_context["partitionKeyFeedRange"] = \
                _get_epk_range_for_partition_key(container_properties, partition_key)
        if "feed_range" in kwargs:
            change_feed_state_context["feedRange"] = kwargs.pop('feed_range')
        if "continuation" in feed_options:
            change_feed_state_context["continuation"] = feed_options.pop("continuation")

        feed_options["changeFeedStateContext"] = change_feed_state_context
        feed_options["containerRID"] = container_properties["_rid"]
        if utils.valid_key_value_exist(feed_options, Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG, _Unset):
            feed_options[Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG] = \
                _validate_hedging_config(feed_options.pop(Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG))

        response_hook = kwargs.pop("response_hook", None)
        if hasattr(response_hook, "clear"):
            response_hook.clear()

        result = self.client_connection.QueryItemsChangeFeed(
            self.container_link, options=feed_options, response_hook=response_hook, **kwargs
        )
        return result

    @overload
    def query_items(
            self,
            query: str,
            parameters: Optional[list[dict[str, object]]] = None,
            partition_key: Optional[PartitionKeyType] = None,
            enable_cross_partition_query: Optional[bool] = None,
            max_item_count: Optional[int] = None,
            enable_scan_in_query: Optional[bool] = None,
            populate_query_metrics: Optional[bool] = None,
            *,
            continuation_token_limit: Optional[int] = None,
            initial_headers: Optional[dict[str, str]] = None,
            max_integrated_cache_staleness_in_ms: Optional[int] = None,
            populate_index_metrics: Optional[bool] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            session_token: Optional[str] = None,
            throughput_bucket: Optional[int] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :type parameters: [list[dict[str, object]]]
        :param partition_key: Partition key at which the query request is targeted. If the partition key is set to
            None, it will perform a cross partition query. To learn more about using partition keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :param bool enable_cross_partition_query: Allows sending of more than one request to
            execute the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :param bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :param bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword bool populate_index_metrics: Used to obtain the index metrics to understand how the query engine used
            existing indexes and how it could use potential new indexes. Please note that this option will incur
            overhead, so it should be enabled only when debugging slow queries.
        :keyword int continuation_token_limit: The size limit in kb of the response continuation token in the query
            response. Valid values are positive integers.
            A value of 0 is the same as not passing a value (default no limit).
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the Azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword str session_token: Token for use with Session consistency.
        :keyword int throughput_bucket: The desired throughput bucket for the client.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :returns: An Iterable of items (dicts).
        :rtype: ItemPaged[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items]
                :end-before: [END query_items]
                :language: python
                :dedent: 0
                :caption: Get all products that have not been discontinued:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items_param]
                :end-before: [END query_items_param]
                :language: python
                :dedent: 0
                :caption: Parameterized query to get all products that have been discontinued:
        """
        ...

    @overload
    def query_items(
            self,
            query: str,
            *,
            continuation_token_limit: Optional[int] = None,
            enable_cross_partition_query: Optional[bool] = None,
            enable_scan_in_query: Optional[bool] = None,
            feed_range: dict[str, Any],
            initial_headers: Optional[dict[str, str]] = None,
            max_integrated_cache_staleness_in_ms: Optional[int] = None,
            max_item_count: Optional[int] = None,
            parameters: Optional[list[dict[str, object]]] = None,
            populate_index_metrics: Optional[bool] = None,
            populate_query_metrics: Optional[bool] = None,
            priority: Optional[Literal["High", "Low"]] = None,
            response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
            session_token: Optional[str] = None,
            throughput_bucket: Optional[int] = None,
            availability_strategy_config: Optional[dict[str, Any]] = _Unset,
            **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword int continuation_token_limit: The size limit in kb of the response continuation token in the query
            response. Valid values are positive integers.
            A value of 0 is the same as not passing a value (default no limit).
        :keyword bool enable_cross_partition_query: Allows sending of more than one request to
            execute the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :keyword bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the Azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :paramtype parameters: [list[dict[str, object]]]
        :keyword bool populate_index_metrics: Used to obtain the index metrics to understand how the query engine used
            existing indexes and how it could use potential new indexes. Please note that this option will incur
            overhead, so it should be enabled only when debugging slow queries.
        :keyword bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword str session_token: Token for use with Session consistency.
        :keyword int throughput_bucket: The desired throughput bucket for the client.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :returns: An Iterable of items (dicts).
        :rtype: ItemPaged[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items]
                :end-before: [END query_items]
                :language: python
                :dedent: 0
                :caption: Get all products that have not been discontinued:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items_param]
                :end-before: [END query_items_param]
                :language: python
                :dedent: 0
                :caption: Parameterized query to get all products that have been discontinued:
        """
        ...

    @distributed_trace
    def query_items(  # pylint:disable=docstring-missing-param
        self,
        *args: Any,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Return all results matching the given `query`.

        You can use any value for the container name in the FROM clause, but
        often the container name is used. In the examples below, the container
        name is "products," and is aliased as "p" for easier referencing in
        the WHERE clause.

        :param Any args: args
        :keyword int continuation_token_limit: The size limit in kb of the response continuation token in the query
            response. Valid values are positive integers.
            A value of 0 is the same as not passing a value (default no limit).
        :keyword bool enable_cross_partition_query: Allows sending of more than one request to
            execute the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :keyword bool enable_scan_in_query: Allow scan on the queries which couldn't be served as
            indexing was opted out on the requested paths.
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the Azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] feed_range: The feed range that is used to define the scope.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword int max_integrated_cache_staleness_in_ms: The max cache staleness for the integrated cache in
            milliseconds. For accounts configured to use the integrated cache, using Session or Eventual consistency,
            responses are guaranteed to be no staler than this value.
        :keyword int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword parameters: Optional array of parameters to the query.
            Each parameter is a dict() with 'name' and 'value' keys.
            Ignored if no query is provided.
        :paramtype parameters: [list[dict[str, object]]]
        :keyword partition_key: Partition key at which the query request is targeted. If the partition key is set to
            None, it will perform a cross partition query. To learn more about using partition keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :paramtype partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword bool populate_index_metrics: Used to obtain the index metrics to understand how the query engine used
            existing indexes and how it could use potential new indexes. Please note that this option will incur
            overhead, so it should be enabled only when debugging slow queries.
        :keyword bool populate_query_metrics: Enable returning query metrics in response headers.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword str query: The Azure Cosmos DB SQL query to execute.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword str session_token: Token for use with Session consistency.
        :keyword int throughput_bucket: The desired throughput bucket for the client.
        :returns: An Iterable of items (dicts).
        :rtype: ItemPaged[dict[str, Any]]

        .. admonition:: Example:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items]
                :end-before: [END query_items]
                :language: python
                :dedent: 0
                :caption: Get all products that have not been discontinued:

            .. literalinclude:: ../samples/examples.py
                :start-after: [START query_items_param]
                :end-before: [END query_items_param]
                :language: python
                :dedent: 0
                :caption: Parameterized query to get all products that have been discontinued:
        """
        # Add positional arguments to keyword argument to support backward compatibility.
        original_positional_arg_names = ["query", "parameters", "partition_key", "enable_cross_partition_query",
                                         "max_item_count", "enable_scan_in_query", "populate_query_metrics"]
        utils.add_args_to_kwargs(original_positional_arg_names, args, kwargs)
        feed_options = build_options(kwargs)

        # Get container property and init client container caches
        container_properties = self._get_properties_with_options(feed_options)

        # Update 'feed_options' from 'kwargs'
        if utils.valid_key_value_exist(kwargs, "enable_cross_partition_query"):
            feed_options["enableCrossPartitionQuery"] = kwargs.pop("enable_cross_partition_query")
        if utils.valid_key_value_exist(kwargs, "max_item_count"):
            feed_options["maxItemCount"] = kwargs.pop("max_item_count")
        if utils.valid_key_value_exist(kwargs, "populate_query_metrics"):
            feed_options["populateQueryMetrics"] = kwargs.pop("populate_query_metrics")
        if utils.valid_key_value_exist(kwargs, "populate_index_metrics"):
            feed_options["populateIndexMetrics"] = kwargs.pop("populate_index_metrics")
        if utils.valid_key_value_exist(kwargs, "enable_scan_in_query"):
            feed_options["enableScanInQuery"] = kwargs.pop("enable_scan_in_query")
        if utils.valid_key_value_exist(kwargs, "max_integrated_cache_staleness_in_ms"):
            max_integrated_cache_staleness_in_ms = kwargs.pop("max_integrated_cache_staleness_in_ms")
            validate_cache_staleness_value(max_integrated_cache_staleness_in_ms)
            feed_options["maxIntegratedCacheStaleness"] = max_integrated_cache_staleness_in_ms
        if utils.valid_key_value_exist(kwargs, "continuation_token_limit"):
            feed_options["responseContinuationTokenLimitInKb"] = kwargs.pop("continuation_token_limit")
        if utils.valid_key_value_exist(feed_options, Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG, _Unset):
            feed_options[Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG] =\
                _validate_hedging_config(feed_options.pop(Constants.Kwargs.AVAILABILITY_STRATEGY_CONFIG))

        feed_options["correlatedActivityId"] = GenerateGuidId()
        feed_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        # Set query with 'query' and 'parameters' from kwargs
        query_str = kwargs.pop("query", None)
        parameters = kwargs.pop("parameters", None)
        if parameters is not None:
            query = {"query": query_str, "parameters": parameters}
        else:
            query = query_str

        # Set range filters for a query. Options are either 'feed_range' or 'partition_key'
        utils.verify_exclusive_arguments(["feed_range", "partition_key"], **kwargs)
        if utils.valid_key_value_exist(kwargs, "partition_key"):
            partition_key_value = self._set_partition_key(kwargs["partition_key"])
            partition_key_obj = _build_partition_key_from_properties(container_properties)
            if partition_key_obj._is_prefix_partition_key(partition_key_value):
                kwargs["prefix_partition_key_object"] = partition_key_obj
                kwargs["prefix_partition_key_value"] = cast(_SequentialPartitionKeyType, partition_key_value)
            else:
                # Add to feed_options, only when feed_range not given and partition_key was not prefixed partition_key
                feed_options["partitionKey"] = partition_key_value
        kwargs.pop("partition_key", None)

        # Set 'partition_key' for QueryItems method. This can be 'None' if feed range or prefix partition key was set
        partition_key = feed_options.get("partitionKey")

        # Set 'response_hook'
        response_hook = kwargs.pop("response_hook", None)
        if response_hook and hasattr(response_hook, "clear"):
            response_hook.clear()

        items = self.client_connection.QueryItems(
            database_or_container_link=self.container_link,
            query=query,
            options=feed_options,
            partition_key=partition_key,
            response_hook=response_hook,
            **kwargs
        )
        return items

    @distributed_trace
    def semantic_rerank(
        self,
        *,
        context: str,
        documents: list[str],
        options: Optional[dict[str, Any]] = None
    ) -> CosmosDict:
        """ **provisional** Rerank a list of documents using semantic reranking.

        This method uses a semantic reranker to score and reorder the provided documents
        based on their relevance to the given reranking context.

        :keyword str context: The reranking context or query string to use for reranking the documents.
        :keyword list[str] documents: A list of documents (as strings) to be reranked.
        :keyword dict[str, Any] options: Optional dictionary of additional request options to customize the semantic reranking process.

         Supported options:
         * **return_documents** (bool): Whether to return the document text in the response. If False, only scores and indices are returned. Default is True.
         * **top_k** (int): Maximum number of documents to return in the reranked results. If not specified, all documents are returned.
         * **batch_size** (int): Number of documents to process in each batch. Used for optimizing performance with large document sets.
         * **sort** (bool): Whether to sort the results by relevance score in descending order. Default is True.
         * **document_type** (str): Type of documents being reranked. Supported values are "string" and "json".
         * **target_paths** (str): If document_type is "json", the list of JSON paths to extract text from for reranking. Comma-separated string.

        :returns: A CosmosDict containing the reranking results. The structure typically includes results list with reranked documents and their relevance scores. Each result contains index, relevance_score, and optionally document.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the semantic reranking operation fails.
        """

        inference_service = self.client_connection._get_inference_service()
        if inference_service is None:
            raise CosmosHttpResponseError(
                message="Semantic reranking requires AAD credentials (inference service not initialized).",
                response=None
            )

        result = inference_service.rerank(
            reranking_context=context,
            documents=documents,
            semantic_reranking_options=options
        )

        return result

    @distributed_trace
    def replace_item(  # pylint:disable=docstring-missing-param
        self,
        item: Union[str, Mapping[str, Any]],
        body: dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Replaces the specified item if it exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be replaced.
        :type item: Union[str, dict[str, Any]]
        :param body: A dict representing the item to replace.
        :type body: dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip
            sending response payloads. When not specified explicitly here, the default value will be determined from
            kwargs or when also not specified there from client-level kwargs.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
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
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics

        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
        result = self.client_connection.ReplaceItem(
            document_link=item_link,
            new_document=body,
            options=request_options,
            **kwargs)
        return result

    @distributed_trace
    def upsert_item(  # pylint:disable=docstring-missing-param
        self,
        body: dict[str, Any],
        populate_query_metrics: Optional[bool]=None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        *,
        session_token: Optional[str] = None,
        initial_headers: Optional[dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Insert or update the specified item.

        If the item already exists in the container, it is replaced. If the item
        does not already exist, it is inserted.

        :param body: A dict-like object representing the item to update or insert.
        :type body: dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip sending
            response payloads. When not specified explicitly here, the default value will be determined from kwargs or
            when also not specified there from client-level kwargs.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given item could not be upserted.
        :returns: A CosmosDict representing the upserted item. The dict will be empty if `no_response` is specified.
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
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        result = self.client_connection.UpsertItem(
                database_or_container_link=self.container_link,
                document=body,
                options=request_options,
                **kwargs
            )
        return result

    @distributed_trace
    def create_item(  # pylint:disable=docstring-missing-param
        self,
        body: dict[str, Any],
        populate_query_metrics: Optional[bool] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        indexing_directive: Optional[int] = None,
        *,
        enable_automatic_id_generation: bool = False,
        session_token: Optional[str] = None,
        initial_headers: Optional[dict[str, str]] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """Create an item in the container.

        To update or replace an existing item, use the
        :func:`ContainerProxy.upsert_item` method.

        :param body: A dict-like object representing the item to create.
        :type body: dict[str, Any]
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :param indexing_directive: Enumerates the possible values to indicate whether the document should
            be omitted from indexing. Possible values include: 0 for Default, 1 for Exclude, or 2 for Include.
        :type indexing_directive: Union[int, ~azure.cosmos.documents.IndexingDirective]
        :keyword bool enable_automatic_id_generation: Enable automatic id generation if no id present.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip sending
            response payloads. When not specified explicitly here, the default value will be determined from kwargs or
            when also not specified there from client-level kwargs.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: Item with the given ID already exists.
        :returns: A CosmosDict representing the new item. The dict will be empty if `no_response` is specified.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)

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
        if no_response is not None:
            kwargs['no_response'] = no_response
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
        if populate_query_metrics:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if indexing_directive is not None:
            request_options["indexingDirective"] = indexing_directive
        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
        result = self.client_connection.CreateItem(
                database_or_container_link=self.container_link, document=body, options=request_options, **kwargs)
        return result

    @distributed_trace
    def patch_item(
        self,
        item: Union[str, dict[str, Any]],
        partition_key: PartitionKeyType,
        patch_operations: list[dict[str, Any]],
        *,
        filter_predicate: Optional[str] = None,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        no_response: Optional[bool] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], dict[str, Any]], None]] = None,
        **kwargs: Any
    ) -> CosmosDict:
        """ Patches the specified item with the provided operations if it
         exists in the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be patched.
        :type item: Union[str, dict[str, Any]]
        :param partition_key: The partition key of the object to patch. If the partition key is set to None,
            it will try to patch an item with a partition key value of null. To learn more about using partition keys,
            see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :param patch_operations: The list of patch operations to apply to the item.
        :type patch_operations: list[dict[str, Any]]
        :keyword str filter_predicate: conditional filter to apply to Patch operations.
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], dict[str, Any]], None]
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword bool no_response: Indicates whether service should be instructed to skip sending
            response payloads. When not specified explicitly here, the default value will be determined from kwargs or
            when also not specified there from client-level kwargs.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The patch operations failed or the item with
            given id does not exist.
        :returns: A CosmosDict representing the item after the patch operations went through. The dict will be empty
            if `no_response` is specified.
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
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["disableAutomaticIdGeneration"] = True
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if filter_predicate is not None:
            request_options["filterPredicate"] = filter_predicate

        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
        item_link = self._get_document_link(item)
        result = self.client_connection.PatchItem(
            document_link=item_link,
            operations=patch_operations,
            options=request_options, **kwargs)
        return result

    @distributed_trace
    def execute_item_batch(
        self,
        batch_operations: Sequence[Union[Tuple[str, Tuple[Any, ...]], Tuple[str, Tuple[Any, ...], dict[str, Any]]]],
        partition_key: PartitionKeyType,
        *,
        pre_trigger_include: Optional[str] = None,
        post_trigger_include: Optional[str] = None,
        session_token: Optional[str] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], list[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> CosmosList:
        """ Executes the transactional batch for the specified partition key.

        :param batch_operations: The batch of operations to be executed.
        :type batch_operations: list[Tuple[Any]]
        :param partition_key: The partition key value of the batch operations. If the partition key is set to None, it
            will try to execute batch on an item with a partition key value of null. To learn more about using partition
            keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: [Callable[[Mapping[str, str], list[dict[str, Any]]], None]
        :returns: A CosmosList representing the items after the batch operations went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The batch failed to execute.
        :raises ~azure.cosmos.exceptions.CosmosBatchOperationError: A transactional batch operation failed in the batch.
        :rtype: ~azure.cosmos.CosmosList[dict[str, Any]]
        """
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)

        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if priority is not None:
            kwargs['priority'] = priority
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        request_options["disableAutomaticIdGeneration"] = True
        container_properties = self._get_properties_with_options(request_options)
        request_options["containerRID"] = container_properties["_rid"]
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
        initial_headers: Optional[dict[str, str]] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        priority: Optional[Literal["High", "Low"]] = None,
        retry_write: Optional[int] = None,
        throughput_bucket: Optional[int] = None,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        response_hook: Optional[Callable[[Mapping[str, str], None], None]] = None,
        **kwargs: Any
    ) -> None:
        """Delete the specified item from the container.

        If the item does not already exist in the container, an exception is raised.

        :param item: The ID (name) or dict representing item to be deleted.
        :type item: Union[str, dict[str, Any]]
        :param partition_key: Specifies the partition key value for the item. If the partition key is set to None,
            it will try to delete an item with a partition key value of null. To learn more about using partition keys,
            see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :param str pre_trigger_include: trigger id to be used as pre operation trigger.
        :param str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword dict[str, str] initial_headers: Initial headers to be sent as part of the request.
        :keyword str etag: An ETag value, or the wildcard character (*). Used to check if the resource
            has changed, and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition: The match condition to use upon the etag.
        :keyword Literal["High", "Low"] priority: Priority based execution allows users to set a priority for each
            request. Once the user has reached their provisioned throughput, low priority requests are throttled
            before high priority requests start getting throttled. Feature must first be enabled at the account level.
        :keyword int retry_write: Indicates how many times the SDK should automatically retry this write operation, even if
            the operation is not guaranteed to be idempotent. This should only be enabled if the application can
            tolerate such risks or has logic to safely detect and handle duplicate operations. Default is None (no retries).
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword dict[str, Any] availability_strategy_config:
            The threshold-based availability strategy to use for this request.
            If not provided, the client's default strategy will be used.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], None], None]
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
        if retry_write is not None:
            kwargs[Constants.Kwargs.RETRY_WRITE] = retry_write
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if availability_strategy_config is not _Unset:
            kwargs["availability_strategy_config"] = _validate_hedging_config(availability_strategy_config)
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if populate_query_metrics is not None:
            warnings.warn(
                "the populate_query_metrics flag does not apply to this method and will be removed in the future",
                DeprecationWarning,
            )
            request_options["populateQueryMetrics"] = populate_query_metrics
        if pre_trigger_include is not None:
            request_options["preTriggerInclude"] = pre_trigger_include
        if post_trigger_include is not None:
            request_options["postTriggerInclude"] = post_trigger_include
        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]
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
    def get_throughput(
            self,
            *,
            response_hook: Optional[Callable[[Mapping[str, Any], list[dict[str, Any]]], None]] = None,
            **kwargs: Any) -> ThroughputProperties:
        """Get the ThroughputProperties object for this container.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], list[dict[str, Any]]], None]
        :returns: Throughput for the container.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exists for the container or
            the throughput properties could not be retrieved.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        throughput_properties: list[dict[str, Any]]
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        options = {"containerRID": properties["_rid"]}
        throughput_properties = list(self.client_connection.QueryOffers(query_spec, options, **kwargs))

        if response_hook:
            response_hook(self.client_connection.last_response_headers, throughput_properties)

        return _deserialize_throughput(throughput=throughput_properties)

    @distributed_trace
    def replace_throughput(
        self,
        throughput: Union[int, ThroughputProperties],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        **kwargs: Any
    ) -> ThroughputProperties:
        """Replace the container's throughput.

        If no ThroughputProperties already exist for the container, an exception is raised.

        :param throughput: The throughput to be set.
        :type throughput: Union[int, ~azure.cosmos.ThroughputProperties]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], CosmosDict], None]
        :returns: ThroughputProperties for the container, updated with new throughput.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: No throughput properties exist for the container
            or the throughput properties could not be updated.
        :rtype: ~azure.cosmos.ThroughputProperties
        """
        throughput_properties: list[dict[str, Any]]
        properties = self._get_properties()
        link = properties["_self"]
        query_spec = {
            "query": "SELECT * FROM root r WHERE r.resource=@link",
            "parameters": [{"name": "@link", "value": link}],
        }
        options = {"containerRID": properties["_rid"]}
        throughput_properties = list(self.client_connection.QueryOffers(query_spec, options, **kwargs))
        new_throughput_properties = throughput_properties[0].copy()
        _replace_throughput(throughput=throughput, new_throughput_properties=new_throughput_properties)
        data = self.client_connection.ReplaceOffer(
            offer_link=throughput_properties[0]["_self"], offer=throughput_properties[0], response_hook=response_hook, **kwargs)

        return ThroughputProperties(offer_throughput=data["content"]["offerThroughput"], properties=data)

    @distributed_trace
    def list_conflicts(
        self,
        max_item_count: Optional[int] = None,
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """List all the conflicts in the container.

        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]
        :returns: An Iterable of conflicts (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
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
        parameters: Optional[list[dict[str, object]]] = None,
        enable_cross_partition_query: Optional[bool] = None,
        partition_key: Optional[PartitionKeyType] = None,
        max_item_count: Optional[int] = None,
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        **kwargs: Any
    ) -> ItemPaged[dict[str, Any]]:
        """Return all conflicts matching a given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :type parameters: list[dict[str, object]]
        :param bool enable_cross_partition_query: Allows sending of more than one request to execute
            the query in the Azure Cosmos DB service.
            More than one request is necessary if the query is not scoped to single partition key value.
        :param partition_key: Specifies the partition key value for the item. If the partition key is set to None,
            it will perform a cross partition query. To learn more about using partition keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :param int max_item_count: Max number of items to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Optional[Callable[[Mapping[str, Any], ItemPaged[dict[str, Any]]], None]] = None,
        :returns: An Iterable of conflicts (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count
        if enable_cross_partition_query is not None:
            feed_options["enableCrossPartitionQuery"] = enable_cross_partition_query
        if partition_key is not None:
            feed_options["partitionKey"] = self._set_partition_key(partition_key)
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

    @distributed_trace
    def get_conflict(
        self,
        conflict: Union[str, Mapping[str, Any]],
        partition_key: PartitionKeyType,
        **kwargs: Any
    ) -> CosmosDict:
        """Get the conflict identified by `conflict`.

        :param conflict: The ID (name) or dict representing the conflict to retrieve.
        :type conflict: Union[str, dict[str, Any]]
        :param partition_key: Partition key for the conflict to retrieve. If the partition key is set to None,
            it will try to fetch a conflict with a partition key of null. To learn more about using partition keys, see
            `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The given conflict couldn't be retrieved.
        :returns: A CosmosDict representing the retrieved conflict.
        :rtype: ~azure.cosmos.CosmosDict[str, Any]
        """
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

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
        :type conflict: Union[str, dict[str, Any]]
        :param partition_key: Partition key for the conflict to delete. If the partition key is set to None, it will
            try to delete a conflict with a partition key value of null. To learn more about using partition keys, see
            `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The conflict wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The conflict does not exist in the container.
        :rtype: None
        """
        request_options = build_options(kwargs)
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        if self.container_link in self.__get_client_container_caches():
            request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

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
        throughput_bucket: Optional[int] = None,
        response_hook: Optional[Callable[[Mapping[str, str], None], None]] = None,
        **kwargs: Any
    ) -> None:
        """The delete by partition key feature is an asynchronous, background operation that allows you to delete all
        documents with the same logical partition key value, using the Cosmos SDK. The delete by partition key
        operation is constrained to consume at most 10% of the total
        available RU/s on the container each second. This helps in limiting the resources used by
        this background task.

        :param partition_key: Partition key for the items to be deleted. If the partition key is set to None, it will
            try to delete the items with a partition key of null. To learn more about using partition keys, see `here
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: ~azure.cosmos.partition_key.PartitionKeyType
        :keyword str pre_trigger_include: trigger id to be used as pre operation trigger.
        :keyword str post_trigger_include: trigger id to be used as post operation trigger.
        :keyword str session_token: Token for use with Session consistency.
        :keyword int throughput_bucket: The desired throughput bucket for the client
        :keyword Sequence[str] excluded_locations: Excluded locations to be skipped from preferred locations. The locations
            in this list are specified as the names of the azure Cosmos locations like, 'West US', 'East US' and so on.
            If all preferred locations were excluded, primary/hub location will be used.
            This excluded_location will override existing excluded_locations in client level.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Mapping[str, str], None], None] = None,
        :rtype: None
        """
        etag = kwargs.get('etag')
        if etag is not None:
            warnings.warn(
                "The 'etag' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)
        match_condition = kwargs.get('match_condition')
        if match_condition is not None:
            warnings.warn(
                "The 'match_condition' flag does not apply to this method and is always ignored even if passed."
                " It will now be removed in the future.",
                DeprecationWarning)

        if pre_trigger_include is not None:
            kwargs['pre_trigger_include'] = pre_trigger_include
        if post_trigger_include is not None:
            kwargs['post_trigger_include'] = post_trigger_include
        if session_token is not None:
            kwargs['session_token'] = session_token
        if throughput_bucket is not None:
            kwargs["throughput_bucket"] = throughput_bucket
        if response_hook is not None:
            kwargs['response_hook'] = response_hook
        request_options = build_options(kwargs)
        # regardless if partition key is valid we set it as invalid partition keys are set to a default empty value
        request_options["partitionKey"] = self._set_partition_key(partition_key)
        self._get_properties_with_options(request_options)
        request_options["containerRID"] = self.__get_client_container_caches()[self.container_link]["_rid"]

        self.client_connection.DeleteAllItemsByPartitionKey(
            collection_link=self.container_link, options=request_options, **kwargs)

    @distributed_trace
    def read_feed_ranges(
            self,
            *,
            force_refresh: bool = False,
            **kwargs: Any) -> Iterable[dict[str, Any]]:

        """ Obtains a list of feed ranges that can be used to parallelize feed operations.

        :keyword bool force_refresh:
            Flag to indicate whether obtain the list of feed ranges directly from cache or refresh the cache.
        :returns: A list representing the feed ranges in base64 encoded string
        :rtype: Iterable[dict[str, Any]]

        .. warning::
          The structure of the dict representation of a feed range may vary, including which keys
          are present. It therefore should only be treated as an opaque value.

        """
        if force_refresh is True:
            self.client_connection.refresh_routing_map_provider()

        def get_next(continuation_token:str) -> list[dict[str, Any]]: # pylint: disable=unused-argument
            partition_key_ranges = \
                self.client_connection._routing_map_provider.get_overlapping_ranges( # pylint: disable=protected-access
                    self.container_link,
                    [Range("", "FF", True, False)],  # default to full range
                    **kwargs)

            feed_ranges = [FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partitionKeyRange)).to_dict()
                    for partitionKeyRange in partition_key_ranges]

            return feed_ranges

        def extract_data(feed_ranges_response: list[dict[str, Any]]):
            return None, iter(feed_ranges_response)

        return ItemPaged(get_next, extract_data)

    def get_latest_session_token(
            self,
            feed_ranges_to_session_tokens: list[Tuple[dict[str, Any], str]],
            target_feed_range: dict[str, Any]
    ) -> str:
        """ **provisional** This method is still in preview and may be subject to breaking changes.

        Gets the the most up to date session token from the list of session token and feed
        range tuples for a specific target feed range. The feed range can be obtained from a partition key
        or by reading the container feed ranges. This should only be used if maintaining own session token or else
        the CosmosClient instance will keep track of session token. Session tokens and feed ranges are
        scoped to a container. Only input session tokens and feed ranges obtained from the same container.
        :param feed_ranges_to_session_tokens: List of feed range and session token tuples.
        :type feed_ranges_to_session_tokens: list[Tuple[dict[str, Any], str]]
        :param target_feed_range: feed range to get most up to date session token.
        :type target_feed_range: dict[str, Any]
        :returns: a session token
        :rtype: str
        """
        return get_latest_session_token(feed_ranges_to_session_tokens, target_feed_range)

    def feed_range_from_partition_key(self, partition_key: PartitionKeyType) -> dict[str, Any]:
        """Gets the feed range for a given partition key.

        :param partition_key: Partition key value used to derive the feed range. If set to ``None`` a feed range
            representing the logical partition whose partition key value is JSON null will be created. To learn more
            about using partition keys, see `Partition Keys
            <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/PartitionKeys.md>`_.
        :type partition_key: PartitionKeyType
        :returns: A feed range corresponding to the supplied partition key value.
        :rtype: dict[str, Any]

        .. warning::
          The structure of the dict representation of a feed range may vary, including which keys
          are present. It therefore should only be treated as an opaque value.

        """
        container_properties = self._get_properties()
        partition_key_value = self._set_partition_key(partition_key)
        epk_range_for_partition_key = _get_epk_range_for_partition_key(container_properties, partition_key_value)
        return FeedRangeInternalEpk(epk_range_for_partition_key).to_dict()

    def is_feed_range_subset(self, parent_feed_range: dict[str, Any], child_feed_range: dict[str, Any]) -> bool:
        """ Checks if child feed range is a subset of parent feed range.
        :param parent_feed_range: left feed range
        :type parent_feed_range: dict[str, Any]
        :param child_feed_range: right feed range
        :type child_feed_range: dict[str, Any]
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
