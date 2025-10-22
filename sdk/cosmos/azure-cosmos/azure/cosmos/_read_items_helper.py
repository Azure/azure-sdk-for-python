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

import logging
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Any, Optional, TYPE_CHECKING, Mapping

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base, exceptions
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos.partition_key import _get_partition_key_from_partition_key_definition
from azure.cosmos import CosmosList
if TYPE_CHECKING:
    from azure.cosmos._cosmos_client_connection import PartitionKeyType , CosmosClientConnection



class ReadItemsHelperSync:
    """Helper class for handling synchronous read many items operations."""
    logger = logging.getLogger("azure.cosmos.ReadManyItemsHelperSync")

    def __init__(
            self,
            client: 'CosmosClientConnection',
            collection_link: str,
            items: Sequence[Tuple[str, "PartitionKeyType"]],
            options: Optional[Mapping[str, Any]],
            partition_key_definition: dict[str, Any],
            *,
            executor: Optional[ThreadPoolExecutor] = None,
            max_concurrency: Optional[int] = None,
            **kwargs: Any
    ):
        self.client = client
        self.collection_link = collection_link
        self.items = items
        self.options = dict(options) if options is not None else {}
        self.partition_key_definition = partition_key_definition
        self.kwargs = kwargs
        self.executor = executor
        self.max_concurrency = max_concurrency
        self.max_items_per_query = 1000

    def read_items(self) -> CosmosList:
        """Reads many items synchronously using a query-based approach with a thread pool.

        :return: A list of the retrieved items in the same order as the input.
        :rtype: ~azure.cosmos.CosmosList
        """

        if not self.items:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        items_by_partition = self._partition_items_by_range()
        if not items_by_partition:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        query_chunks = self._create_query_chunks(items_by_partition)

        # Use the provided executor if available, otherwise create one with max_concurrency
        if self.executor is not None:
            return self._execute_with_executor(self.executor, query_chunks)

        # Create a new executor; if max_concurrency is None, use ThreadPoolExecutor's default
        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            return self._execute_with_executor(executor, query_chunks)

    def _execute_with_executor(
            self,
            executor: ThreadPoolExecutor,
            query_chunks: list[dict[str, list[Tuple[int, str, "PartitionKeyType"]]]]
    ) -> CosmosList:
        """Execute the queries using the provided executor with improved error handling.

        :param ThreadPoolExecutor executor: The ThreadPoolExecutor to use
        :param query_chunks: A list of query chunks to be executed.
        :type query_chunks: list[dict[str, list[tuple[int, str, "_PartitionKeyType"]]]]
        :return: A list of the retrieved items in original order
        :rtype: ~azure.cosmos.CosmosList
        """
        indexed_results = []
        total_request_charge = 0.0
        futures = []
        # Create a clear mapping of futures to chunks for better error handling
        future_to_chunk = {}

        for chunk in query_chunks:
            for partition_id, partition_items in chunk.items():
                future = executor.submit(self._execute_query_chunk_worker, partition_id, partition_items)
                futures.append(future)
                future_to_chunk[future] = (partition_id, partition_items)

        try:
            for future in as_completed(futures):
                chunk_results, chunk_ru_charge = future.result()
                indexed_results.extend(chunk_results)
                total_request_charge += chunk_ru_charge
        except (Exception, KeyboardInterrupt) as e:
            self.logger.error("Error in query execution: %s", str(e))
            # Cancel all pending futures
            for f in futures:
                if not f.done():
                    f.cancel()

            if self.executor is None:
                executor.shutdown(wait=False, cancel_futures=True)
            raise

        # Sort results by original index
        indexed_results.sort(key=lambda x: x[0])
        # Remove the index from results
        results = [item[1] for item in indexed_results]

        final_headers = CaseInsensitiveDict()
        final_headers['x-ms-request-charge'] = str(total_request_charge)

        cosmos_list = CosmosList(results, response_headers=final_headers)

        # Call the original response hook with the final results if provided
        if 'response_hook' in self.kwargs:
            self.kwargs['response_hook'](final_headers, cosmos_list)

        return cosmos_list

    def _partition_items_by_range(self) -> dict[str, list[Tuple[int, str, "PartitionKeyType"]]]:
        # pylint: disable=protected-access
        """Groups items by their partition key range ID efficiently while preserving original order.

        :return: A dictionary of items grouped by partition key range ID with original indices.
        :rtype: dict[str, list[tuple[int, str, any]]]
        """
        collection_rid = _base.GetResourceIdOrFullNameFromLink(self.collection_link)
        partition_key = _get_partition_key_from_partition_key_definition(self.partition_key_definition)
        items_by_partition: dict[str, list[Tuple[int, str, "PartitionKeyType"]]] = {}

        # Group items by logical partition key first to avoid redundant range lookups
        items_by_pk_value: dict[Any, list[Tuple[int, str, "PartitionKeyType"]]] = {}
        for idx, (item_id, pk_value) in enumerate(self.items):
            # Convert list to tuple to use as a dictionary key, as lists are unhashable
            key = tuple(pk_value) if isinstance(pk_value, list) else pk_value
            if key not in items_by_pk_value:
                items_by_pk_value[key] = []
            items_by_pk_value[key].append((idx, item_id, pk_value))

        # Now, resolve the range ID once per unique logical partition key
        for _, pk_items in items_by_pk_value.items():
            # All items in this list share the same partition key value. Get it from the first item.
            pk_value = pk_items[0][2]
            epk_range = partition_key._get_epk_range_for_partition_key(pk_value)
            overlapping_ranges = self.client._routing_map_provider.get_overlapping_ranges(
                collection_rid, [epk_range], self.options
            )
            if overlapping_ranges:
                range_id = overlapping_ranges[0]["id"]
                if range_id not in items_by_partition:
                    items_by_partition[range_id] = []
                items_by_partition[range_id].extend(pk_items)

        return items_by_partition


    def _create_query_chunks(
            self,
            items_by_partition: dict[str, list[Tuple[int, str, "PartitionKeyType"]]]
    ) -> list[dict[str, list[Tuple[int, str, "PartitionKeyType"]]]]:
        """Create query chunks for concurrency control while preserving original indices.

        :param items_by_partition: A dictionary mapping partition key range IDs to lists of items with indices.
        :type items_by_partition: dict[str, list[tuple[int, str, "PartitionKeyType"]]]
        :return: A list of query chunks, where each chunk is a dictionary with a single partition.
        :rtype: list[dict[str, list[tuple[int, str, "PartitionKeyType"]]]]
        """
        query_chunks = []
        for partition_id, partition_items in items_by_partition.items():
            # Split large partitions into chunks of self.max_items_per_query
            for i in range(0, len(partition_items), self.max_items_per_query):
                chunk = partition_items[i:i + self.max_items_per_query]
                query_chunks.append({partition_id: chunk})
        return query_chunks

    def _execute_query_chunk_worker(
            self, partition_id: str, chunk_partition_items: Sequence[Tuple[int, str, "PartitionKeyType"]]
    ) -> Tuple[list[Tuple[int, dict[str, Any]]], float]:
        """Synchronous worker to build and execute a query for a chunk of items.

        :param str partition_id: The ID of the partition to query.
        :param list[tuple[int, str, any]] chunk_partition_items: A chunk of items to be queried.
        :return: A tuple containing the list of query results with original indices and the request charge.
        :rtype: tuple[list[tuple[int, dict[str, any]]], float]
        """
        id_to_idx = {item[1]: item[0] for item in chunk_partition_items}
        items_for_query = [(item[1], item[2]) for item in chunk_partition_items]
        request_kwargs = self.kwargs.copy()

        if len(items_for_query) == 1:
            item_id, pk_value = items_for_query[0]
            result, headers = self._execute_point_read(item_id, pk_value, request_kwargs)
            chunk_results = [(id_to_idx[item_id], result)] if result else []
        else:
            chunk_results, headers = self._execute_query(partition_id, items_for_query, id_to_idx, request_kwargs)

        total_ru_charge = 0.0
        charge = headers.get('x-ms-request-charge')
        if charge:
            try:
                total_ru_charge = float(charge)
            except (ValueError, TypeError):
                self.logger.warning("Invalid request charge format: %s", charge)

        return chunk_results, total_ru_charge

    def _execute_query(
            self,
            partition_id: str,
            items_for_query: Sequence[Tuple[str, "PartitionKeyType"]],
            id_to_idx: dict[str, int],
            request_kwargs: dict[str, Any]
    ) -> Tuple[list[Tuple[int, Any]], CaseInsensitiveDict]:
        """
        Builds and executes a query for a chunk of items.

        :param partition_id: The ID of the partition to query.
        :type partition_id: str
        :param items_for_query: List of tuples containing item IDs and partition key values.
        :type items_for_query: list[tuple[str, PartitionKeyType]]
        :param id_to_idx: Mapping from item ID to its original index in the input list.
        :type id_to_idx: dict[str, int]
        :param request_kwargs: Additional keyword arguments for the request.
        :type request_kwargs: dict[str, any]
        :return: A tuple containing the list of query results with original indices and the request charge headers.
        :rtype: tuple[list[tuple[int, dict[str, any]]], CaseInsensitiveDict]
        """
        captured_headers = {}

        def local_response_hook(hook_headers, _):
            captured_headers.update(hook_headers)

        request_kwargs['response_hook'] = local_response_hook

        if _QueryBuilder.is_id_partition_key_query(items_for_query, self.partition_key_definition):
            query_obj = _QueryBuilder.build_id_in_query(items_for_query)
        elif _QueryBuilder.is_single_logical_partition_query(items_for_query):
            query_obj = _QueryBuilder.build_pk_and_id_in_query(items_for_query, self.partition_key_definition)
        else:
            partition_items_dict = {partition_id: items_for_query}
            query_obj = _QueryBuilder.build_parameterized_query_for_items(
                partition_items_dict, self.partition_key_definition)

        query_iterator = self.client.QueryItems(self.collection_link, query_obj, self.options, **request_kwargs)
        results = list(query_iterator)

        chunk_indexed_results = []
        for item in results:
            doc_id = item.get('id')
            if doc_id in id_to_idx:
                chunk_indexed_results.append((id_to_idx[doc_id], item))
            else:
                self.logger.warning("Received document with unexpected ID: %s", doc_id)

        return chunk_indexed_results, CaseInsensitiveDict(captured_headers)

    def _execute_point_read(
            self,
            item_id: str,
            pk_value: "PartitionKeyType",
            request_kwargs: dict[str, Any]
    ) -> Tuple[Optional[Any], CaseInsensitiveDict]:
        """
        Executes a point read for a single item.

        :param item_id: The ID of the item to read.
        :type item_id: str
        :param pk_value: The partition key value for the item.
        :type pk_value: _PartitionKeyType
        :param request_kwargs: Additional keyword arguments for the request.
        :type request_kwargs: dict[str, any]
        :return: A tuple containing the item (or None if not found) and the response headers.
        :rtype: tuple[Optional[any], CaseInsensitiveDict]
        """
        doc_link = f"{self.collection_link}/docs/{item_id}"
        point_read_options = self.options.copy()
        point_read_options["partitionKey"] = pk_value
        captured_headers = {}

        def local_response_hook(hook_headers, _):
            captured_headers.update(hook_headers)

        request_kwargs['response_hook'] = local_response_hook
        request_kwargs.pop("containerProperties", None)

        try:
            result = self.client.ReadItem(doc_link, point_read_options, **request_kwargs)
            return result, CaseInsensitiveDict(captured_headers)
        except exceptions.CosmosResourceNotFoundError as e:
            captured_headers.update(e.headers)
            return None, CaseInsensitiveDict(captured_headers)
