import asyncio
from typing import Dict, List, Tuple, Any, Union, Mapping, Optional

from azure.cosmos import _base
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._cosmos_client_connection import PartitionKeyType
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos.partition_key import _Undefined, _Empty, NonePartitionKeyValue, _get_partition_key_from_partition_key_definition

class ReadManyItemsHelper:
    """Helper class for handling read many items operations."""

    def __init__(self, client: 'CosmosClientConnection'):
        self.client = client
        self.max_concurrency = 10
        self.max_items_per_query = 1000

    async def partition_items_by_range(
            self,
            items: List[Tuple[str, PartitionKeyType]],
            collection_link: str,
            partition_key_definition: Dict[str, Any]
    ) -> Dict[str, List[Tuple[str, PartitionKeyType]]]:
        """Group items by their partition key range ID."""
        # Get collection resource ID
        collection_rid = _base.GetResourceIdOrFullNameFromLink(collection_link)
        # Create partition key object from definition
        partition_key = _get_partition_key_from_partition_key_definition(partition_key_definition)
        # Dictionary to group items by partition key range ID
        items_by_partition: Dict[str, List[Tuple[str, PartitionKeyType]]] = {}

        # Process each item and group by physical partition
        for item_id, partition_key_value in items:
            try:
                # Get the EPK range for the given partition key value
                epk_range = partition_key._get_epk_range_for_partition_key(partition_key_value)

                # Get overlapping ranges for this EPK range
                overlapping_ranges = await self.client._routing_map_provider.get_overlapping_ranges(
                    collection_rid,
                    [epk_range]
                )

                # Use the first overlapping range (there should be exactly one for a point lookup)
                if overlapping_ranges:
                    range_id = overlapping_ranges[0]["id"]

                    # Group items by the partition key range ID
                    if range_id not in items_by_partition:
                        items_by_partition[range_id] = []
                    items_by_partition[range_id].append((item_id, partition_key_value))

            except Exception as e:
                # Log the error but skip the item
                # logger.warning(f"Failed to process item {item_id}:{partition_key_value} - {e}")
                continue  # Skip this item entirely

        return items_by_partition

    def create_query_chunks(
            self,
            items_by_partition: Dict[str, List[Tuple[str, PartitionKeyType]]],
            max_items_per_query: int
    ) -> List[Dict[str, List[Tuple[str, PartitionKeyType]]]]:
        """Create query chunks for concurrency control."""
        query_chunks = []
        for partition_id, partition_items in items_by_partition.items():
            # Split large partitions into chunks of max_items_per_query
            for i in range(0, len(partition_items), max_items_per_query):
                chunk = partition_items[i:i + max_items_per_query]
                query_chunks.append({partition_id: chunk})
        return query_chunks

    async def execute_queries_concurrently(
            self,
            query_chunks: List[Dict[str, List[Tuple[str, PartitionKeyType]]]],
            collection_link: str,
            partition_key_definition: Dict[str, Any],
            options: Optional[Mapping[str, Any]],
            max_concurrency: int = 10,
            **kwargs: Any
    ) -> Tuple[List[Any], CaseInsensitiveDict]:
        """Execute query chunks concurrently and return aggregated results."""
        semaphore = asyncio.Semaphore(max_concurrency)

        async def execute_chunk_query(chunk_items):
            async with semaphore:  # Acquire slot, auto-released on exit
                # Get all items from this chunk
                chunk_partition_items = list(chunk_items.values())[0]

                # Use _can_use_id_in_query to determine which query building approach to use
                if _QueryBuilder._can_optimize_with_id_in_clause(chunk_partition_items, partition_key_definition):
                    query_obj = _QueryBuilder._build_id_in_query(chunk_partition_items)
                else:
                    query_obj = _QueryBuilder._build_parameterized_query_for_items(
                        {list(chunk_items.keys())[0]: chunk_partition_items},
                        partition_key_definition)

                # Execute query using existing QueryItems method
                query_results = self.client.QueryItems(collection_link, query_obj, options, **kwargs)

                individual_chunk_results = []
                last_headers = CaseInsensitiveDict()

                async for item in query_results:
                    individual_chunk_results.append(item)
                    # Get headers from the last response if available
                    if hasattr(self.client, 'last_response_headers'):
                        last_headers.update(self.client.last_response_headers)

                return individual_chunk_results, last_headers

        # Execute all chunks concurrently
        chunk_tasks = [execute_chunk_query(chunk) for chunk in query_chunks]
        chunk_results = await asyncio.gather(*chunk_tasks)

        # Aggregate results
        all_results = []
        combined_headers = CaseInsensitiveDict()

        for chunk_result, chunk_headers in chunk_results:
            all_results.extend(chunk_result)
            combined_headers.update(chunk_headers)

        return all_results, combined_headers