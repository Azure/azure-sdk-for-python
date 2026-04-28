# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import re
from enum import Enum
from typing import Any, Optional, Union


# Used by query paging and query merge paths to decide whether a row is
# a normal row or part of an aggregate result.
class _AggregatePartialClassification(Enum):
    """Classification for one-partition query partial payloads."""

    NONE = "none"
    OBJECT = "object"
    VALUE = "value"


def _extract_query_text(query: Optional[Union[str, dict[str, Any]]]) -> Optional[str]:
    """Extract SQL text from a string or query-spec dictionary.

    :param query: Query text or query spec dictionary.
    :type query: Optional[Union[str, dict[str, Any]]]
    :returns: Query text when present; otherwise ``None``.
    :rtype: Optional[str]
    """
    if isinstance(query, str):
        return query
    if isinstance(query, dict):
        query_text = query.get("query")
        if isinstance(query_text, str):
            return query_text
    return None


def _get_select_value_aggregate_function(query: Optional[Union[str, dict[str, Any]]]) -> Optional[str]:
    """Identify the aggregate function for ``SELECT VALUE`` aggregate queries.

    This is a lightweight text heuristic (not a SQL parser). It extracts only
    the OUTER ``SELECT VALUE`` projection and then matches aggregate function
    names in that projection so nested subqueries do not drive outer
    classification.

    :param query: Query text or query spec dictionary.
    :type query: Optional[Union[str, dict[str, Any]]]
    :returns: One of ``COUNT``, ``SUM``, ``MIN``, ``MAX``, ``AVG`` when matched; otherwise ``None``.
    :rtype: Optional[str]
    """
    query_text = _extract_query_text(query)
    if not query_text:
        return None

    normalized = " ".join(query_text.upper().split())
    projection = _extract_outer_select_value_projection(normalized)
    if projection is None:
        return None

    # Match whole function names only (avoid MYCOUNT) and allow COUNT (1).
    for aggregate_fn in ("COUNT", "SUM", "MIN", "MAX", "AVG"):
        if re.search(rf"(?<![A-Z0-9_]){aggregate_fn}\s*\(", projection):
            return aggregate_fn
    return None


def _extract_outer_select_value_projection(normalized_query: str) -> Optional[str]:
    """Return the outer ``SELECT VALUE`` projection text up to the outer ``FROM``.

    Uses a lightweight parenthesis-depth scan so nested subqueries do not
    influence outer aggregate detection.
    """
    select_value = "SELECT VALUE"
    start_idx = normalized_query.find(select_value)
    if start_idx < 0:
        return None

    projection_start = start_idx + len(select_value)
    if projection_start < len(normalized_query) and normalized_query[projection_start] == " ":
        projection_start += 1

    depth = 0
    index = projection_start
    while index <= len(normalized_query) - 4:
        ch = normalized_query[index]
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1

        if depth == 0 and normalized_query[index:index + 4] == "FROM":
            prev_char = normalized_query[index - 1] if index > 0 else " "
            next_char = normalized_query[index + 4] if index + 4 < len(normalized_query) else " "
            if not (prev_char.isalnum() or prev_char == "_") and not (next_char.isalnum() or next_char == "_"):
                projection = normalized_query[projection_start:index].strip()
                return projection or None
        index += 1

    return None


def _classify_aggregate_partial(
    docs: Any,
    query: Optional[Union[str, dict[str, Any]]]
) -> _AggregatePartialClassification:
    """Classify whether a partial result row is part of an aggregate result.

    :param docs: Partial ``Documents`` payload from one backend response.
    :type docs: Any
    :param query: Query text or query spec dictionary.
    :type query: Optional[Union[str, dict[str, Any]]]
    :returns: Aggregate partial classification.
    :rtype: _AggregatePartialClassification
    """
    if not isinstance(docs, list) or len(docs) != 1:
        return _AggregatePartialClassification.NONE

    row = docs[0]
    if isinstance(row, dict) and row.get("_aggregate") is not None:
        return _AggregatePartialClassification.OBJECT

    # bool is intentionally excluded: VALUE-aggregate merge semantics are numeric.
    if isinstance(row, (int, float)) and not isinstance(row, bool):
        if _get_select_value_aggregate_function(query) is not None:
            return _AggregatePartialClassification.VALUE

    return _AggregatePartialClassification.NONE
