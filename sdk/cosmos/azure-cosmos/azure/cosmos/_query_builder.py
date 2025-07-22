# azure/cosmos/_query_builder.py
"""Internal query builder for multi-item operations."""

from typing import Dict, List, Tuple, Any, Union

from azure.cosmos._cosmos_client_connection import PartitionKeyType
from azure.cosmos.partition_key import _Undefined, _Empty, NonePartitionKeyValue


class _QueryBuilder:
    """Internal class for building optimized queries for multi-item operations."""

    @staticmethod
    def _get_field_expression(path: str) -> str:
        """Converts a path string into a query field expression."""
        field_name = path.lstrip("/")
        if "/" in field_name:
            # Handle nested paths like "a/b" -> c["a"]["b"]
            field_parts = field_name.split("/")
            return "c" + "".join(f'["{part}"]' for part in field_parts)
        # Handle simple paths like "pk" -> c.pk or c["non-identifier-pk"]
        return f"c.{field_name}" if field_name.isidentifier() else f'c["{field_name}"]'

    @staticmethod
    def is_id_partition_key_query(
            items: List[Tuple[str, PartitionKeyType]],
            partition_key_definition: Dict[str, Any]
    ) -> bool:
        """Check if we can use the optimized ID IN query."""
        partition_key_paths = partition_key_definition.get("paths", [])
        if len(partition_key_paths) != 1 or partition_key_paths[0] != "/id":
            return False

        for item_id, partition_key_value in items:
            pk_val = partition_key_value[0] if isinstance(partition_key_value, list) else partition_key_value
            if pk_val != item_id:
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
        partition_key_path = partition_key_definition['paths'][0].lstrip('/')
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
        id_params = {f"@param_id{i}": item_id for i, (item_id, _) in enumerate(items)}
        param_names = ", ".join(id_params.keys())
        parameters = [{"name": name, "value": value} for name, value in id_params.items()]

        query_string = f"SELECT * FROM c WHERE c.id IN ( {param_names} )"

        return {"query": query_string, "parameters": parameters}

    @staticmethod
    def build_parameterized_query_for_items(
            items_by_partition: Dict[str, List[Tuple[str, PartitionKeyType]]],
            partition_key_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Builds a parameterized SQL query for reading multiple items."""
        all_items = [item for partition_items in items_by_partition.values() for item in partition_items]

        if not all_items:
            return {"query": "SELECT * FROM c WHERE false", "parameters": []}

        partition_key_paths = partition_key_definition.get("paths", [])
        query_parts = []
        parameters = []

        for i, (item_id, partition_key_value) in enumerate(all_items):
            id_param_name = f"@param_id{i}"
            parameters.append({"name": id_param_name, "value": item_id})
            condition_parts = [f"c.id = {id_param_name}"]

            pk_values = []
            if partition_key_value is not None and not isinstance(partition_key_value, type(NonePartitionKeyValue)):
                pk_values = partition_key_value if isinstance(partition_key_value, list) else [partition_key_value]
                if len(pk_values) != len(partition_key_paths):
                    raise ValueError(
                        f"Number of components in partition key value ({len(pk_values)}) "
                        f"does not match definition ({len(partition_key_paths)})"
                    )

            for j, path in enumerate(partition_key_paths):
                field_expr = _QueryBuilder._get_field_expression(path)
                pk_value = pk_values[j] if j < len(pk_values) else None

                if pk_value is None or isinstance(pk_value, (_Undefined, _Empty)):
                    condition_parts.append(f"IS_DEFINED({field_expr}) = false")
                else:
                    pk_param_name = f"@param_pk{i}{j}"
                    parameters.append({"name": pk_param_name, "value": pk_value})
                    condition_parts.append(f"{field_expr} = {pk_param_name}")

            query_parts.append(f"( {' AND '.join(condition_parts)} )")

        query_string = f"SELECT * FROM c WHERE ( {' OR '.join(query_parts)} )"
        return {"query": query_string, "parameters": parameters}