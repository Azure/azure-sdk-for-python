# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Translation package - Cosmos SQL to Fabric SQL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ..config import MirrorServingConfiguration
from .fabric_sql import emit_fabric_sql
from .parameters import ParameterizedSql, parameterize
from .parser import parse_cosmos_sql


@dataclass(frozen=True)
class TranslateResult:
    """Result of translating a Cosmos query to Fabric SQL.
    
    Attributes:
        sql: Parameterized SQL ready for driver execution (? placeholders)
        params: Ordered parameter values
        select_value: True if SELECT VALUE (returns scalars), False for SELECT (returns docs)
    """
    
    sql: str
    params: list[Any]
    select_value: bool


def translate(
    query_text: str, parameters: Iterable[dict[str, Any]] | None, config: MirrorServingConfiguration
) -> TranslateResult:
    """Translate a Cosmos SQL query to Fabric SQL.
    
    Args:
        query_text: Cosmos SQL query string
        parameters: Query parameters (list of dicts with 'name' and 'value')
        config: Mirror serving configuration
        
    Returns:
        TranslateResult with parameterized SQL and metadata
        
    Raises:
        UnsupportedCosmosQueryError: If query uses unsupported features
        ConfigurationError: If configuration is invalid
    """
    ast = parse_cosmos_sql(query_text)
    sql_unparam = emit_fabric_sql(ast, config)
    p: ParameterizedSql = parameterize(sql_unparam, parameters)
    return TranslateResult(sql=p.sql, params=p.params, select_value=ast.select_value)


__all__ = ["TranslateResult", "translate"]
