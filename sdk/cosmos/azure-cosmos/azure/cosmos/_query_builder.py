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

"""Internal query builder for multi-item operations."""

import json
from typing import Tuple, Any, TYPE_CHECKING, Sequence

from azure.cosmos.partition_key import _Undefined
from azure.cosmos._helpers._paths import parse_paths
from azure.cosmos._helpers._read_items import partition_key_components, partition_key_identity
if TYPE_CHECKING:
    from azure.cosmos._cosmos_client_connection import PartitionKeyType


class _QueryBuilder:
    """Internal class for building optimized queries for multi-item operations."""

    @staticmethod
    def _get_field_expression(path: str) -> str:
        """Converts a path string into a query field expression.

        :param str path: The path string to convert.
        :return: The query field expression.
        :rtype: str
        """
        parts = parse_paths([path])
        return "c" + "".join(f"[{json.dumps(part)}]" for part in parts)

    @staticmethod
    def is_id_partition_key_query(
            items: Sequence[Tuple[str, "PartitionKeyType"]],
            partition_key_definition: dict[str, Any]
    ) -> bool:
        """Check if we can use the optimized ID IN query.

        :param Sequence[tuple[str, any]] items: The list of items to check.
        :param dict[str, any] partition_key_definition: The partition key definition of the container.
        :return: True if the optimized ID IN query can be used, False otherwise.
        :rtype: bool
        """
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
            items: Sequence[Tuple[str, "PartitionKeyType"]]
    ) -> bool:
        """Check if all items in a chunk belong to the same logical partition.

        This is used to determine if an optimized query with an IN clause can be used.

        :param Sequence[tuple[str, any]] items: The list of items to check.
        :return: True if all items belong to the same logical partition, False otherwise.
        :rtype: bool
        """
        if not items or len(items) <= 1:
            return False
        first_pk = partition_key_identity(items[0][1])
        return all(partition_key_identity(item[1]) == first_pk for item in items)

    @staticmethod
    def _partition_predicates(
        value: Any, paths: Sequence[str], prefix: str
    ) -> Tuple[list[str], list[dict[str, Any]]]:
        components = partition_key_components(value)
        if len(components) != len(paths):
            raise ValueError("read_items requires every component of the container's partition key.")
        predicates = []
        parameters: list[dict[str, Any]] = []
        for index, (path, component) in enumerate(zip(paths, components)):
            field = _QueryBuilder._get_field_expression(path)
            if isinstance(component, _Undefined):
                predicates.append(f"IS_DEFINED({field}) = false")
            else:
                name = f"{prefix}_{index}"
                predicates.append(f"{field} = {name}")
                parameters.append({"name": name, "value": component})
        return predicates, parameters

    @staticmethod
    def build_pk_and_id_in_query(
            items: Sequence[Tuple[str, "PartitionKeyType"]],
            partition_key_definition: dict[str, Any]
    ) -> dict[str, Any]:
        """Build a query for items in a single logical partition using an IN clause for IDs.

        e.g., SELECT * FROM c WHERE c.pk = @pk AND c.id IN (@id1, @id2)

        :param Sequence[tuple[str, any]] items: The list of items to build the query for.
        :param dict[str, any] partition_key_definition: The partition key definition of the container.
        :return: A dictionary containing the query text and parameters.
        :rtype: dict[str, any]
        """
        id_params = {f"@id{i}": item[0] for i, item in enumerate(items)}
        id_param_names = ", ".join(id_params.keys())

        predicates, parameters = _QueryBuilder._partition_predicates(
            items[0][1], partition_key_definition["paths"], "@pk"
        )
        query_text = f"SELECT * FROM c WHERE {' AND '.join(predicates)} AND c.id IN ({id_param_names})"
        parameters.extend([{"name": name, "value": value} for name, value in id_params.items()])

        return {"query": query_text, "parameters": parameters}

    @staticmethod
    def build_id_in_query(items: Sequence[Tuple[str, "PartitionKeyType"]]) -> dict[str, Any]:
        """Build optimized query using ID IN clause when ID equals partition key.

        :param Sequence[tuple[str, any]] items: The list of items to build the query for.
        :return: A dictionary containing the query text and parameters.
        :rtype: dict[str, any]
        """
        id_params = {f"@param_id{i}": item_id for i, (item_id, _) in enumerate(items)}
        param_names = ", ".join(id_params.keys())
        parameters = [{"name": name, "value": value} for name, value in id_params.items()]

        query_string = f"SELECT * FROM c WHERE c.id IN ( {param_names} )"

        return {"query": query_string, "parameters": parameters}

    @staticmethod
    def build_parameterized_query_for_items(
            items_by_partition: dict[str, Sequence[Tuple[str, "PartitionKeyType"]]],
            partition_key_definition: dict[str, Any]
    ) -> dict[str, Any]:
        """Builds a parameterized SQL query for reading multiple items.

        :param dict[str, Sequence[tuple[str, any]]] items_by_partition: A dictionary of items grouped by partition key.
        :param dict[str, any] partition_key_definition: The partition key definition of the container.
        :return: A dictionary containing the query text and parameters.
        :rtype: dict[str, any]
        """
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

            predicates, pk_parameters = _QueryBuilder._partition_predicates(
                partition_key_value, partition_key_paths, f"@param_pk{i}"
            )
            condition_parts.extend(predicates)
            parameters.extend(pk_parameters)

            query_parts.append(f"( {' AND '.join(condition_parts)} )")

        query_string = f"SELECT * FROM c WHERE ( {' OR '.join(query_parts)} )"
        return {"query": query_string, "parameters": parameters}
