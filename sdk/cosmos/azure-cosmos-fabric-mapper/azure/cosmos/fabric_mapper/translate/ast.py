# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""AST node types for the supported Cosmos SQL subset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryAst:
    """Abstract syntax tree for a parsed Cosmos SQL query.
    
    Attributes:
        select_value: True if SELECT VALUE (returns scalars), False for SELECT (returns docs)
        select_expr: The projection expression after SELECT [VALUE]
        where_expr: WHERE clause expression (None if no WHERE)
        group_by: GROUP BY expression (None if no GROUP BY)
        having_expr: HAVING clause expression (None if no HAVING)
        order_by: ORDER BY expression (None if no ORDER BY)
        offset: OFFSET value for pagination (None if not specified)
        limit: LIMIT/TOP value (None if not specified)
    """
    
    select_value: bool
    select_expr: str
    where_expr: str | None
    group_by: str | None
    having_expr: str | None
    order_by: str | None
    offset: int | None
    limit: int | None
