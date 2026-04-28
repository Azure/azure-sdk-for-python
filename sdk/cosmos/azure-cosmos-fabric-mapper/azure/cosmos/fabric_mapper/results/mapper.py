# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Result mapper - tabular rows to Cosmos-like documents."""

from __future__ import annotations

import json
from typing import Any

from ..driver.base import ResultSet


def map_result_set(result_set: ResultSet, select_value: bool) -> list[Any]:
    """Map a tabular result set to Cosmos-like result format.
    
    Args:
        result_set: Tabular result from driver
        select_value: True if SELECT VALUE (return scalars), False for SELECT (return dicts)
        
    Returns:
        List of documents (dicts) or scalars, matching Cosmos result shape
    """
    if not result_set.columns:
        return []

    if select_value:
        # SELECT VALUE returns list of scalars (first column only)
        return [row[0] for row in result_set.rows]

    # Heuristic: if single column with JSON-like name, try to parse as JSON
    if len(result_set.columns) == 1 and result_set.columns[0].lower() in {"doc", "document", "json", "_rawbody"}:
        out: list[Any] = []
        for (v,) in result_set.rows:
            if v is None:
                out.append(None)
            elif isinstance(v, (dict, list)):
                out.append(v)
            else:
                try:
                    out.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    out.append(v)
        return out

    # Standard SELECT: map columns to dict
    items: list[dict[str, Any]] = []
    cols = result_set.columns
    for row in result_set.rows:
        items.append({cols[i]: row[i] for i in range(len(cols))})
    return items
