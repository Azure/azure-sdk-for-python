# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

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

    This is a lightweight text heuristic over the full query string (not a SQL
    parser). Aggregate function tokens inside subqueries can therefore produce
    false positives for the outer query.

    :param query: Query text or query spec dictionary.
    :type query: Optional[Union[str, dict[str, Any]]]
    :returns: One of ``COUNT``, ``SUM``, ``MIN``, ``MAX``, ``AVG`` when matched; otherwise ``None``.
    :rtype: Optional[str]
    """
    query_text = _extract_query_text(query)
    if not query_text:
        return None

    normalized = " ".join(query_text.upper().split())
    if "SELECT VALUE" not in normalized:
        return None

    # NOTE: This checks the full normalized query text, so aggregate function
    # names inside subqueries can be matched as false positives.
    for aggregate_fn in ("COUNT", "SUM", "MIN", "MAX", "AVG"):
        if f"{aggregate_fn}(" in normalized:
            return aggregate_fn
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
