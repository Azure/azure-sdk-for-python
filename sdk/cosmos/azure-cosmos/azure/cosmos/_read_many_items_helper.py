from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Any, Mapping, Optional, TYPE_CHECKING

from azure.core.utils import CaseInsensitiveDict

from azure.cosmos import _base
from azure.cosmos._query_builder import _QueryBuilder
from azure.cosmos.partition_key import _get_partition_key_from_partition_key_definition
from azure.cosmos import CosmosList
if TYPE_CHECKING:
    from azure.cosmos._cosmos_client_connection import PartitionKeyType
import logging


class ReadManyItemsHelperSync:
    """Helper class for handling synchronous read many items operations."""
    logger = logging.getLogger("azure.cosmos.ReadManyItemsHelperSync")

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

    def read_many_items(self) -> CosmosList:
        """Reads many items synchronously using a query-based approach with a thread pool."""
        if not self.items:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        items_by_partition = self._partition_items_by_range()
        if not items_by_partition:
            return CosmosList([], response_headers=CaseInsensitiveDict())

        results: List[Dict[str, Any]] = []
        total_request_charge = 0.0

        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            futures = []
            for partition_id, partition_items in items_by_partition.items():
                for i in range(0, len(partition_items), self.max_items_per_query):
                    chunk = partition_items[i:i + self.max_items_per_query]
                    futures.append(executor.submit(self._execute_query_chunk_worker, partition_id, chunk))
            try:
                for future in as_completed(futures):
                    chunk_results, chunk_ru_charge = future.result()
                    results.extend(chunk_results)
                    total_request_charge += chunk_ru_charge
            except Exception:
                # On failure, shutdown the executor to cancel pending futures and re-raise
                executor.shutdown(wait=False, cancel_futures=True)
                raise

        final_headers = CaseInsensitiveDict()
        final_headers['x-ms-request-charge'] = str(total_request_charge)

        return CosmosList(results, response_headers=final_headers)

    def _partition_items_by_range(self) -> Dict[str, List[Tuple[str, "PartitionKeyType"]]]:
        """Groups items by their partition key range ID efficiently."""
        collection_rid = _base.GetResourceIdOrFullNameFromLink(self.collection_link)
        partition_key = _get_partition_key_from_partition_key_definition(self.partition_key_definition)
        items_by_partition: Dict[str, List[Tuple[str, "PartitionKeyType"]]] = {}

        # Group items by logical partition key first to avoid redundant range lookups
        items_by_pk_value: Dict[Any, List[Tuple[str, "PartitionKeyType"]]] = {}
        for item_id, pk_value in self.items:
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
            overlapping_ranges = self.client._routing_map_provider.get_overlapping_ranges(
                collection_rid, [epk_range]
            )
            if overlapping_ranges:
                range_id = overlapping_ranges[0]["id"]
                if range_id not in items_by_partition:
                    items_by_partition[range_id] = []
                items_by_partition[range_id].extend(pk_items)

        return items_by_partition

    def _execute_query_chunk_worker(
            self, partition_id: str, chunk_partition_items: List[Tuple[str, "PartitionKeyType"]]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Synchronous worker to build and execute a query for a chunk of items."""
        captured_headers = {}

        # Define the response hook function
        def response_hook(hook_headers, _):
            captured_headers.update(hook_headers)

        # Copy the kwargs and add the response hook
        request_kwargs = self.kwargs.copy()
        request_kwargs['response_hook'] = response_hook

        if _QueryBuilder.is_id_partition_key_query(chunk_partition_items, self.partition_key_definition):
            query_obj = _QueryBuilder.build_id_in_query(chunk_partition_items)
        elif _QueryBuilder.is_single_logical_partition_query(chunk_partition_items):
            query_obj = _QueryBuilder.build_pk_and_id_in_query(chunk_partition_items, self.partition_key_definition)
        else:
            # Pass only the current chunk to the query builder
            query_obj = _QueryBuilder.build_parameterized_query_for_items(
                {partition_id: chunk_partition_items}, self.partition_key_definition)

        # Execute query with the response hook
        query_iterator = self.client.QueryItems(self.collection_link, query_obj, self.options, **request_kwargs)
        results = list(query_iterator)

        # Process the captured headers
        total_ru_charge = 0.0
        headers = CaseInsensitiveDict(captured_headers)
        charge = headers.get('x-ms-request-charge')
        if charge:
            try:
                total_ru_charge = float(charge)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid request charge format: {charge}")

        return results, total_ru_charge