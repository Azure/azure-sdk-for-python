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


def _strip_sql_block_comments(query_text: str) -> str:
    """Return ``query_text`` with ``/* ... */`` comment spans removed.

    The aggregate detector is a lightweight scanner, so this helper keeps the
    same lightweight approach and removes only block comments before scanning.
    Quoted strings are preserved so comment-like text inside literals does not
    get stripped.

    :param query_text: Raw query text.
    :type query_text: str
    :returns: Query text with block comments removed.
    :rtype: str
    """
    out: list[str] = []
    index = 0
    length = len(query_text)
    in_quote: Optional[str] = None

    while index < length:
        ch = query_text[index]

        if in_quote is not None:
            out.append(ch)
            # SQL-style escaped quote inside same quote type, e.g. 'it''s'.
            if ch == in_quote and index + 1 < length and query_text[index + 1] == in_quote:
                out.append(query_text[index + 1])
                index += 2
                continue
            if ch == in_quote:
                in_quote = None
            index += 1
            continue

        if ch in ("'", '"'):
            in_quote = ch
            out.append(ch)
            index += 1
            continue

        if ch == "/" and index + 1 < length and query_text[index + 1] == "*":
            index += 2
            while index + 1 < length and not (query_text[index] == "*" and query_text[index + 1] == "/"):
                index += 1
            if index + 1 < length:
                index += 2
            # Preserve token separation where a comment was removed.
            out.append(" ")
            continue

        out.append(ch)
        index += 1

    return "".join(out)


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

    without_comments = _strip_sql_block_comments(query_text)
    normalized = " ".join(without_comments.upper().split())
    projection = _extract_outer_select_value_projection(normalized)
    if projection is None:
        return None

    projection = _unwrap_outer_parentheses(projection)
    # A projection-level subquery should not classify as an outer VALUE aggregate.
    if projection.startswith("SELECT VALUE "):
        return None

    return _find_top_level_aggregate_function(projection)


def _find_top_level_aggregate_function(projection: str) -> Optional[str]:
    """Return an aggregate function name only when the projection is a bare aggregate call.

    A bare call is exactly one top-level aggregate function and nothing
    else: ``COUNT(1)``, ``SUM(c.amount)``, ``MIN(c["score"])`` qualify;
    compound shapes like ``SUM(c.x) + 1``, ``1 + SUM(c.x)``,
    ``SUM(c.x) - SUM(c.y)``, or ``-MIN(c.x)`` return ``None``.

    Compound projections cannot be merged across partitions with the
    aggregate-merge rules without introducing silent arithmetic errors,
    so returning ``None`` here forces the caller onto the standard
    list-concat path. The unsupported shape then surfaces as a visibly
    multi-row result instead of a silently wrong scalar.

    :param projection: SELECT VALUE projection text (uppercased,
        whitespace-normalized, outer parentheses already unwrapped).
    :type projection: str
    :returns: Aggregate function name when the projection is a bare
        aggregate call; otherwise ``None``.
    :rtype: Optional[str]
    """
    aggregate_fns = {"COUNT", "SUM", "MIN", "MAX", "AVG"}
    depth = 0
    index = 0
    length = len(projection)

    while index < length:
        ch = projection[index]
        if ch == "(":
            depth += 1
            index += 1
            continue
        if ch == ")":
            if depth > 0:
                depth -= 1
            index += 1
            continue

        if depth == 0 and (ch.isalpha() or ch == "_"):
            start = index
            index += 1
            while index < length and (projection[index].isalnum() or projection[index] == "_"):
                index += 1
            token = projection[start:index]

            if token in aggregate_fns:
                # Confirm the token is immediately followed (modulo whitespace)
                # by '(' so we are looking at a function call, not a column
                # named SUM/COUNT/etc.
                open_paren = index
                while open_paren < length and projection[open_paren].isspace():
                    open_paren += 1
                if open_paren >= length or projection[open_paren] != "(":
                    continue

                # Walk to the matching close-paren tracking depth so nested
                # parens inside the argument list do not confuse us.
                call_depth = 0
                close_paren = -1
                cursor = open_paren
                while cursor < length:
                    inner = projection[cursor]
                    if inner == "(":
                        call_depth += 1
                    elif inner == ")":
                        call_depth -= 1
                        if call_depth == 0:
                            close_paren = cursor
                            break
                    cursor += 1
                if close_paren < 0:
                    # Unbalanced parentheses in a normalized projection means
                    # we cannot reason about the shape safely.
                    return None

                # Classify only when the bare aggregate call spans the whole
                # projection. Any non-whitespace prefix or suffix is a compound
                # expression whose per-partition partials cannot be merged with
                # the aggregate-merge rules.
                prefix_clean = projection[:start].strip() == ""
                suffix_clean = projection[close_paren + 1:].strip() == ""
                if prefix_clean and suffix_clean:
                    return token
                return None
            continue

        index += 1

    return None


def _unwrap_outer_parentheses(text: str) -> str:
    """Strip redundant outer parentheses while preserving inner structure.

    :param text: Projection text to normalize.
    :type text: str
    :returns: Projection text with only redundant outer parentheses removed.
    :rtype: str
    """
    candidate = text.strip()
    while candidate.startswith("(") and candidate.endswith(")"):
        depth = 0
        balanced = True
        outer_pair = False
        for idx, char in enumerate(candidate):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    balanced = False
                    break
                # Closing the opening '(' at index 0 means we found the outer pair.
                if depth == 0:
                    outer_pair = idx == len(candidate) - 1
                    break
        if not balanced or not outer_pair:
            break
        candidate = candidate[1:-1].strip()
    return candidate


def _extract_outer_select_value_projection(normalized_query: str) -> Optional[str]:
    """Return the outer ``SELECT VALUE`` projection text up to the outer ``FROM``.

    Uses a lightweight parenthesis-depth scan so nested subqueries do not
    influence outer aggregate detection.

    :param normalized_query: Uppercased, whitespace-normalized query text.
    :type normalized_query: str
    :returns: Outer ``SELECT VALUE`` projection when found; otherwise ``None``.
    :rtype: Optional[str]
    """
    select_value = "SELECT VALUE"
    # Minimal hardening: only classify when the OUTER query starts with
    # SELECT VALUE. This avoids matching nested SELECT VALUE occurrences.
    if not normalized_query.startswith(select_value):
        return None
    start_idx = 0

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
