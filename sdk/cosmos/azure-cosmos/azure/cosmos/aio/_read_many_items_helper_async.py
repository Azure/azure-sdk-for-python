import asyncio
from typing import Dict, List, Tuple, Any, Union, Mapping, Optional

from azure.cosmos import _base
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos.partition_key import _Undefined, _Empty, NonePartitionKeyValue, _get_partition_key_from_partition_key_definition
from azure.cosmos import CosmosList
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from azure.cosmos.aio._cosmos_client_connection_async import PartitionKeyType


class ReadManyItemsHelper:
    """Helper class for handling read many items operations."""
    logger = logging.getLogger("azure.cosmos.ReadManyItemsHelper")

    def __init__(
            self,
            client: 'CosmosClientConnection',
            collection_link: str,
            items: List[Tuple[str, "PartitionKeyType"]],
            options: Optional[Mapping[str, Any]],
            partition_key_definition: Dict[str, Any],
            **kwargs: Any
    ):
        self.client = client
        self.collection_link = collection_link
        self.items = items
        self.options = options if options is not None else {}
        self.partition_key_definition = partition_key_definition
        self.kwargs = kwargs
        self.max_concurrency = 10
        self.max_items_per_query = 1000

    async def read_many_items(self) -> 'CosmosList':
        """Executes the read-many operation."""
        # Group items by partition key range
        items_by_partition = await self.partition_items_by_range(
            self.items, self.collection_link, self.partition_key_definition
        )

        # Create query chunks from the grouped items
        query_chunks = self.create_query_chunks(items_by_partition)

        # Execute queries concurrently
        all_results, combined_headers = await self.execute_queries_concurrently(
            query_chunks,
            self.collection_link,
            self.partition_key_definition,
            self.options,
            self.max_concurrency,
            **self.kwargs
        )

        return CosmosList(all_results, response_headers=combined_headers)

    async def partition_items_by_range(
            self,
            items: List[Tuple[str, "PartitionKeyType"]],
            collection_link: str,
            partition_key_definition: Dict[str, Any]
    ) -> Dict[str, List[Tuple[str, "PartitionKeyType"]]]:
        """Groups items by their partition key range ID efficiently."""
        collection_rid = _base.GetResourceIdOrFullNameFromLink(collection_link)
        partition_key = _get_partition_key_from_partition_key_definition(partition_key_definition)
        items_by_partition: Dict[str, List[Tuple[str, "PartitionKeyType"]]] = {}

        # Group items by logical partition key first to avoid redundant range lookups
        items_by_pk_value: Dict[Any, List[Tuple[str, "PartitionKeyType"]]] = {}
        for item_id, pk_value in items:
            # Convert list to tuple to use as a dictionary key, as lists are unhashable
            key = tuple(pk_value) if isinstance(pk_value, list) else pk_value
            if key not in items_by_pk_value:
                items_by_pk_value[key] = []
            items_by_pk_value[key].append((item_id, pk_value))

        # Now, resolve the range ID once per unique logical partition key
        for _, pk_items in items_by_pk_value.items():
            # All items in this list share the same partition key value. Get it from the first item.
            pk_value = pk_items[0][1]
            epk_range = partition_key._get_epk_range_for_partition_key(pk_value)
            overlapping_ranges = await self.client._routing_map_provider.get_overlapping_ranges(
                collection_rid, [epk_range]
            )
            if overlapping_ranges:
                range_id = overlapping_ranges[0]["id"]
                if range_id not in items_by_partition:
                    items_by_partition[range_id] = []
                items_by_partition[range_id].extend(pk_items)

        return items_by_partition

    def create_query_chunks(
            self,
            items_by_partition: Dict[str, List[Tuple[str, "PartitionKeyType"]]]
    ) -> List[Dict[str, List[Tuple[str, "PartitionKeyType"]]]]:
        """Create query chunks for concurrency control."""
        query_chunks = []
        for partition_id, partition_items in items_by_partition.items():
            # Split large partitions into chunks of self.max_items_per_query
            for i in range(0, len(partition_items), self.max_items_per_query):
                chunk = partition_items[i:i + self.max_items_per_query]
                query_chunks.append({partition_id: chunk})
        return query_chunks

    async def execute_queries_concurrently(
            self,
            query_chunks: List[Dict[str, List[Tuple[str, "PartitionKeyType"]]]],
            collection_link: str,
            partition_key_definition: Dict[str, Any],
            options: Optional[Mapping[str, Any]],
            max_concurrency: int = 10,
            **kwargs: Any
    ) -> Tuple[List[Any], CaseInsensitiveDict]:
        """Execute query chunks concurrently and return aggregated results."""
        if not query_chunks:
            return [], CaseInsensitiveDict()

        semaphore = asyncio.Semaphore(max_concurrency)

        async def execute_chunk_query(partition_id, chunk_partition_items):
            async with semaphore:
                captured_headers = {}
                request_kwargs = kwargs.copy()
                request_kwargs['response_hook'] = lambda hook_headers, _: captured_headers.update(hook_headers)
                # Optimization for when the partition key is the item's ID.
                # This allows for a highly efficient query using an IN clause on the ID field.
                if _QueryBuilder.is_id_partition_key_query(chunk_partition_items, partition_key_definition):
                    query_obj = _QueryBuilder.build_id_in_query(chunk_partition_items)
                # Optimization for when all items in a chunk belong to the same logical partition.
                # This allows for a more efficient query by targeting a single partition
                # and using an IN clause for the item IDs.
                elif _QueryBuilder.is_single_logical_partition_query(chunk_partition_items):
                    query_obj = _QueryBuilder.build_pk_and_id_in_query(chunk_partition_items, partition_key_definition)
                else:
                    query_obj = _QueryBuilder.build_parameterized_query_for_items(
                        {partition_id: chunk_partition_items},
                        partition_key_definition)

                query_results_iterator = self.client.QueryItems(collection_link, query_obj, options, **request_kwargs)
                page_iterator = query_results_iterator.by_page()

                # Use nested async for in the list comprehension
                individual_chunk_results = [item async for page in page_iterator async for item in page]

                total_ru_charge = 0.0
                headers = CaseInsensitiveDict(captured_headers)
                charge = headers.get('x-ms-request-charge')
                if charge:
                    try:
                        total_ru_charge = float(charge)
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid request charge format: {charge}")

                return individual_chunk_results, total_ru_charge

        chunk_tasks = [
            asyncio.create_task(execute_chunk_query(partition_id, items))
            for chunk in query_chunks
            for partition_id, items in chunk.items()
        ]

        try:
            chunk_results = await asyncio.gather(*chunk_tasks)
        except Exception:
            # Cancel remaining tasks on failure
            for task in chunk_tasks:
                if not task.done():
                    task.cancel()
            # Wait for tasks to cancel and then re-raise the original exception
            await asyncio.gather(*chunk_tasks, return_exceptions=True)
            raise

        all_results = [item for res, _ in chunk_results for item in res]
        total_request_charge = sum(ru for _, ru in chunk_results)

        final_headers = CaseInsensitiveDict()
        final_headers['x-ms-request-charge'] = str(total_request_charge)

        return all_results, final_headers