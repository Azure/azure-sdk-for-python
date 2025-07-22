# azure/cosmos/_query_builder.py
"""Internal query builder for multi-item operations."""

from typing import Dict, List, Tuple, Any, Union

from azure.cosmos._cosmos_client_connection import PartitionKeyType
from azure.cosmos.partition_key import _Undefined, _Empty, NonePartitionKeyValue


class _QueryBuilder:
    """Internal class for building optimized queries for multi-item operations."""

    @staticmethod
    def is_id_partition_key_query(
            items: List[Tuple[str, PartitionKeyType]],
            partition_key_definition: Dict[str, Any]
    ) -> bool:
        """Check if we can use the optimized ID IN query."""
        # Check if partition key path is "/id"
        partition_key_paths = partition_key_definition.get("paths", [])
        if len(partition_key_paths) != 1 or partition_key_paths[0] != "/id":
            return False

        # Check if all items have ID equal to partition key
        for item_id, partition_key_value in items:
            # Handle different partition key formats
            if isinstance(partition_key_value, list):
                if len(partition_key_value) != 1 or partition_key_value[0] != item_id:
                    return False
            elif partition_key_value != item_id:
                return False

        return True

    @staticmethod
    def is_single_logical_partition_query(
            items: List[Tuple[str, PartitionKeyType]]
    ) -> bool:
        """
        Check if all items in a chunk belong to the same logical partition and would benefit from an IN clause.
        """
        if not items or len(items) <= 1:
            return False
        first_pk = items[0][1]
        return all(item[1] == first_pk for item in items)

    @staticmethod
    def build_pk_and_id_in_query(
            items: List[Tuple[str, PartitionKeyType]],
            partition_key_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a query for items in a single logical partition using an IN clause for IDs.
        e.g., SELECT * FROM c WHERE c.pk = @pk AND c.id IN (@id1, @id2)
        """
        partition_key_path = partition_key_definition['paths'][0].replace('/', '')
        partition_key_value = items[0][1]

        id_params = {f"@id{i}": item[0] for i, item in enumerate(items)}
        id_param_names = ", ".join(id_params.keys())

        query_text = f"SELECT * FROM c WHERE c.{partition_key_path} = @pk AND c.id IN ({id_param_names})"

        parameters = [{"name": "@pk", "value": partition_key_value}]
        parameters.extend([{"name": name, "value": value} for name, value in id_params.items()])

        return {"query": query_text, "parameters": parameters}

    @staticmethod
    def build_id_in_query(items: List[Tuple[str, PartitionKeyType]]) -> Dict[str, Any]:
        """Build optimized query using ID IN clause when ID equals partition key."""
        param_names = []
        parameters = []

        for i, (item_id, _) in enumerate(items):
            param_name = f"@param_id{i}"
            param_names.append(param_name)
            parameters.append({"name": param_name, "value": item_id})

        query_string = f"SELECT * FROM c WHERE c.id IN ( {','.join(param_names)} )"

        return {
            "query": query_string,
            "parameters": parameters
        }

    @staticmethod
    def build_parameterized_query_for_items(
            items_by_partition: Dict[str, List[Tuple[str, PartitionKeyType]]],
            partition_key_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Builds a parameterized SQL query for reading multiple items.

        :param items_by_partition: Dictionary mapping partition range IDs to lists of (item_id, partition_key) tuples
        :param partition_key_definition: The partition key definition for the container
        :return: Query object with 'query' and 'parameters' fields
        """
        if not items_by_partition:
            return {"query": "SELECT * FROM c WHERE false", "parameters": []}

        # Get all items from all partitions
        all_items = []
        for partition_items in items_by_partition.values():
            all_items.extend(partition_items)

        if not all_items:
            return {"query": "SELECT * FROM c WHERE false", "parameters": []}

        # Extract partition key paths for hierarchical partition keys
        partition_key_paths = partition_key_definition.get("paths", [])

        # Build the query conditions
        query_parts = []
        parameters = []

        for i, (item_id, partition_key_value) in enumerate(all_items):
            # Add item ID parameter
            id_param_name = f"@param_id{i}"
            parameters.append({"name": id_param_name, "value": item_id})

            # Start building condition for this item
            condition_parts = [f"c.id = {id_param_name}"]

            # Handle partition key conditions
            if partition_key_value is None or isinstance(partition_key_value, type(NonePartitionKeyValue)):
                # Handle null partition key - all paths should be undefined
                for path in partition_key_paths:
                    # Remove leading "/" from path and format for query
                    field_name = path[1:] if path.startswith("/") else path
                    if "/" in field_name:
                        # Handle nested paths like "a/b" -> c["a"]["b"]
                        field_parts = field_name.split("/")
                        field_expr = "c" + "".join(f'["{part}"]' for part in field_parts)
                    else:
                        # Handle simple paths like "pk" -> c["pk"] or c.pk
                        field_expr = f'c["{field_name}"]' if not field_name.isidentifier() else f"c.{field_name}"

                    condition_parts.append(f"IS_DEFINED({field_expr}) = false")
            else:
                # Handle non-null partition key values
                if isinstance(partition_key_value, list):
                    pk_values = partition_key_value
                else:
                    pk_values = [partition_key_value]

                # Validate partition key component count
                if len(pk_values) != len(partition_key_paths):
                    raise ValueError(
                        f"Number of components in partition key value ({len(pk_values)}) "
                        f"does not match definition ({len(partition_key_paths)})"
                    )

                # Add condition for each partition key component
                for j, (path, pk_value) in enumerate(zip(partition_key_paths, pk_values)):
                    # Remove leading "/" from path and format for query
                    field_name = path[1:] if path.startswith("/") else path
                    if "/" in field_name:
                        # Handle nested paths like "a/b" -> c["a"]["b"]
                        field_parts = field_name.split("/")
                        field_expr = "c" + "".join(f'["{part}"]' for part in field_parts)
                    else:
                        # Handle simple paths like "pk" -> c["pk"] or c.pk
                        field_expr = f'c["{field_name}"]' if not field_name.isidentifier() else f"c.{field_name}"

                    # Check for undefined values (similar to C# Undefined.Value)
                    if pk_value is None or isinstance(pk_value, _Undefined) or isinstance(pk_value, _Empty):
                        condition_parts.append(f"IS_DEFINED({field_expr}) = false")
                    else:
                        # Add parameter for this partition key component
                        pk_param_name = f"@param_pk{i}{j}"
                        parameters.append({"name": pk_param_name, "value": pk_value})
                        condition_parts.append(f"{field_expr} = {pk_param_name}")

            # Combine all conditions for this item with AND
            item_condition = f"( {' AND '.join(condition_parts)} )"
            query_parts.append(item_condition)

        # Combine all item conditions with OR
        query_string = f"SELECT * FROM c WHERE ( {' OR '.join(query_parts)} )"

        return {
            "query": query_string,
            "parameters": parameters
        }