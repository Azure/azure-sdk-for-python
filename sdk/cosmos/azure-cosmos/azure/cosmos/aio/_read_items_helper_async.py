# The MIT License (MIT)
# Copyright (c) 2018 Microsoft Corporation

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
import asyncio # pylint: disable=C4763  # Used for Semaphore and gather, not for sleep
from typing import Tuple, Any, Sequence, Optional, TYPE_CHECKING, Mapping

from azure.cosmos import _base, exceptions
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos.partition_key import _get_partition_key_from_partition_key_definition, PartitionKeyType
from azure.cosmos import CosmosList

if TYPE_CHECKING:
    from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection

class ReadItemsHelperAsync:
    """Helper class for handling read many items operations.

    This implementation preserves the original order of items in the input sequence
    when returning results, regardless of how items are distributed across partitions
    or processed in chunks.
    """
    logger = logging.getLogger("azure.cosmos.ReadManyItemsHelper")

    def __init__(
            self,
            client: 'CosmosClientConnection',
            collection_link: str,
            items: Sequence[Tuple[str, PartitionKeyType]],
            options: Optional[Mapping[str, Any]],
            partition_key_definition: dict[str, Any],
            max_concurrency: int = 5,
            **kwargs: Any
    ):
        self.client = client
        self.collection_link = collection_link
        self.items = items
        self.options = dict(options) if options is not None else {}
        self.partition_key_definition = partition_key_definition
        self.kwargs = kwargs
        self.max_concurrency = max_concurrency if max_concurrency and max_concurrency > 0 else 5
        self.max_items_per_query = 1000

    async def read_items(self) -> 'CosmosList':
        """Executes the read-many operation.

        :return: A list of the retrieved items in the same order as the input.
        :rtype: ~azure.cosmos.CosmosList
        """

        if not self.items:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        items_by_partition = await self._partition_items_by_range()
        if not items_by_partition:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        query_chunks = self._create_query_chunks(items_by_partition)

        indexed_results, combined_headers = await self._execute_queries_concurrently(query_chunks)

        indexed_results.sort(key=lambda x: x[0])
        all_results = [item[1] for item in indexed_results]
        cosmos_list = CosmosList(all_results, response_headers=combined_headers)

        if 'response_hook' in self.kwargs:
            self.kwargs['response_hook'](combined_headers, cosmos_list)

        return cosmos_list

    async def _partition_items_by_range(self) -> dict[str, list[Tuple[int, str, "PartitionKeyType"]]]:
        # pylint: disable=protected-access
        """
        Groups items by their partition key range ID efficiently while preserving original order.

        :return: A dictionary mapping partition key range IDs to lists of tuples containing the
                    original index, item ID, and partition key value.
        :rtype: dict[str, list[tuple[int, str, PartitionKeyType]]]
        """
        collection_rid = _base.GetResourceIdOrFullNameFromLink(self.collection_link)
        partition_key = _get_partition_key_from_partition_key_definition(self.partition_key_definition)
        items_by_partition: dict[str, list[Tuple[int, str, "PartitionKeyType"]]] = {}

        items_by_pk_value: dict[Any, list[Tuple[int, str, "PartitionKeyType"]]] = {}
        for idx, (item_id, pk_value) in enumerate(self.items):
            key = tuple(pk_value) if isinstance(pk_value, list) else pk_value
            if key not in items_by_pk_value:
                items_by_pk_value[key] = []
            items_by_pk_value[key].append((idx, item_id, pk_value))

        for pk_items in items_by_pk_value.values():
            pk_value = pk_items[0][2]
            epk_range = partition_key._get_epk_range_for_partition_key(pk_value)
            overlapping_ranges = await self.client._routing_map_provider.get_overlapping_ranges(
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

        """
        Create query chunks for concurrency control while preserving original indices.

        :param items_by_partition: A dictionary mapping partition key range IDs to lists of tuples containing the
                                original index, item ID, and partition key value.
        :type items_by_partition: dict[str, list[tuple[int, str, PartitionKeyType]]]
        :return: A list of dictionaries, each mapping a partition ID to a chunk of items.
        :rtype: list[dict[str, list[tuple[int, str, PartitionKeyType]]]]
        """
        query_chunks = []
        for partition_id, partition_items in items_by_partition.items():
            for i in range(0, len(partition_items), self.max_items_per_query):
                chunk = partition_items[i:i + self.max_items_per_query]
                query_chunks.append({partition_id: chunk})
        return query_chunks

    async def _execute_queries_concurrently(
            self,
            query_chunks: list[dict[str, list[Tuple[int, str, "PartitionKeyType"]]]],
    ) -> Tuple[list[Tuple[int, Any]], CaseInsensitiveDict]:
        """
        Execute query chunks concurrently and return aggregated results with original indices.

        :param query_chunks: A list of dictionaries, each mapping a partition ID to a chunk of items to query.
        :type query_chunks: list[dict[str, list[tuple[int, str, PartitionKeyType]]]]
        :return: A tuple containing a list of results with original indices and the combined response headers.
        :rtype: tuple[list[tuple[int, any]], CaseInsensitiveDict]
        """
        if not query_chunks:
            return [], CaseInsensitiveDict()

        semaphore = asyncio.Semaphore(self.max_concurrency)
        indexed_results = []
        total_request_charge = 0.0

        async def execute_chunk_query(partition_id, chunk_partition_items):
            async with semaphore:
                id_to_idx = {item[1]: item[0] for item in chunk_partition_items}
                items_for_query = [(item[1], item[2]) for item in chunk_partition_items]
                request_kwargs = self.kwargs.copy()

                if len(items_for_query) == 1:
                    item_id, pk_value = items_for_query[0]
                    result, headers = await self._execute_point_read(item_id, pk_value, request_kwargs)
                    chunk_results = [(id_to_idx[item_id], result)] if result else []
                else:
                    chunk_results, headers = await self._execute_query(
                        partition_id, items_for_query, id_to_idx, request_kwargs)

                request_charge = self._extract_request_charge(headers)
                return chunk_results, request_charge

        tasks = [
            asyncio.create_task(execute_chunk_query(partition_id, items))
            for chunk in query_chunks
            for partition_id, items in chunk.items()
        ]

        try:
            all_chunk_results = await asyncio.gather(*tasks)
        except Exception:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

        for chunk_result, ru_charge in all_chunk_results:
            indexed_results.extend(chunk_result)
            total_request_charge += ru_charge

        final_headers = CaseInsensitiveDict({'x-ms-request-charge': str(total_request_charge)})
        return indexed_results, final_headers

    def _extract_request_charge(self, headers: CaseInsensitiveDict) -> float:
        """Extract the request charge from the headers.

        :param headers: The response headers.
        :type headers: ~azure.core.utils.CaseInsensitiveDict
        :return: The request charge.
        :rtype: float
        """
        charge = headers.get('x-ms-request-charge')
        request_charge = 0.0  # Renamed from ru_charge to avoid shadowing
        if charge:
            try:
                request_charge = float(charge)
            except (ValueError, TypeError):
                self.logger.warning("Invalid request charge format: %s", charge)
        return request_charge

    async def _execute_point_read(
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
        :type pk_value: PartitionKeyType
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
            result = await self.client.ReadItem(doc_link, point_read_options, **request_kwargs)
            return result, CaseInsensitiveDict(captured_headers)
        except exceptions.CosmosResourceNotFoundError as e:
            captured_headers.update(e.headers)
            return None, CaseInsensitiveDict(captured_headers)

    async def _execute_query(
            self,
            partition_id: str,
            items_for_query: Sequence[Tuple[str, "PartitionKeyType"]],
            id_to_idx: dict[str, int],
            request_kwargs: dict[str, Any]
    ) -> Tuple[list[Tuple[int, Any]], CaseInsensitiveDict]:
        """
        Builds and executes a query for a chunk of items.

        :param partition_id: The partition key range ID for the query.
        :type partition_id: str
        :param items_for_query: A list of tuples containing item IDs and partition key values to query.
        :type items_for_query: list[tuple[str, PartitionKeyType]]
        :param id_to_idx: A mapping from item ID to its original index in the input sequence.
        :type id_to_idx: dict[str, int]
        :param request_kwargs: Additional keyword arguments for the request.
        :type request_kwargs: dict[str, any]
        :return: A tuple containing a list of results with original indices and the response headers.
        :rtype: tuple[list[tuple[int, any]], CaseInsensitiveDict]
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

        page_iterator = self.client.QueryItems(
            self.collection_link, query_obj, self.options, **request_kwargs).by_page()

        chunk_indexed_results = []
        async for page in page_iterator:
            async for item in page:
                doc_id = item.get('id')
                if doc_id in id_to_idx:
                    chunk_indexed_results.append((id_to_idx[doc_id], item))
                else:
                    self.logger.warning("Received document with unexpected ID: %s", doc_id)

        return chunk_indexed_results, CaseInsensitiveDict(captured_headers)
