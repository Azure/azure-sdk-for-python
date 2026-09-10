# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Fabric SQL emitter - transforms AST to Fabric SQL syntax."""

from __future__ import annotations

import re

from ..config import MirrorServingConfiguration, default_table_sql
from ..errors import UnsupportedCosmosQueryError
from .ast import QueryAst

_STRING_LITERAL_RE = re.compile(r"'(?:''|[^'])*'")
_PATH_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
_PARENTHESIZED_PATH = (
    r"\(*\s*\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\s*\)*"
)
_NULL_LITERAL = r"\(*\s*NULL\s*\)*"
_NULL_COMPARISON_RE = re.compile(
    rf"(?P<left>{_PARENTHESIZED_PATH})\s*(?P<operator>=|!=|<>)\s*{_NULL_LITERAL}"
    r"(?![A-Za-z0-9_.]|\s*[+\-*/%])",
    re.IGNORECASE,
)
_REVERSED_NULL_COMPARISON_RE = re.compile(
    rf"{_NULL_LITERAL}\s*(?P<operator>=|!=|<>)\s*(?P<right>{_PARENTHESIZED_PATH})"
    r"(?![A-Za-z0-9_.]|\s*[+\-*/%])",
    re.IGNORECASE,
)
_TSQL_RESERVED_WORDS = frozenset(
    {
        "ALTER",
        "AND",
        "AS",
        "BEGIN",
        "CREATE",
        "DATABASE",
        "DELETE",
        "DROP",
        "EXEC",
        "EXECUTE",
        "FALSE",
        "FROM",
        "GRANT",
        "GROUP",
        "HAVING",
        "INSERT",
        "INTO",
        "JOIN",
        "MERGE",
        "NOT",
        "NULL",
        "OFFSET",
        "OR",
        "ORDER",
        "SELECT",
        "SET",
        "TABLE",
        "TOP",
        "TRANSACTION",
        "TRUE",
        "TRUNCATE",
        "UNION",
        "UPDATE",
        "USE",
        "VALUES",
        "WAITFOR",
        "WHERE",
    }
)


def _rewrite_sql_segment(segment: str) -> str:
    if re.search(r"\bNULL\b", segment, re.IGNORECASE) and re.search(
        r"[+\-*/%]", segment
    ):
        raise UnsupportedCosmosQueryError(
            "Null comparisons cannot be combined with arithmetic expressions"
        )

    def _rewrite_null(match: re.Match) -> str:
        operator = "IS" if match.group("operator") == "=" else "IS NOT"
        return f"{match.group('left').strip()} {operator} NULL"

    def _rewrite_reversed_null(match: re.Match) -> str:
        operator = "IS" if match.group("operator") == "=" else "IS NOT"
        return f"{match.group('right').strip()} {operator} NULL"

    def _quote_path(match: re.Match) -> str:
        parts = match.group(0).split(".")
        return ".".join(
            f"[{part}]" if part.upper() in _TSQL_RESERVED_WORDS else part
            for part in parts
        )

    segment = _NULL_COMPARISON_RE.sub(_rewrite_null, segment)
    segment = _REVERSED_NULL_COMPARISON_RE.sub(_rewrite_reversed_null, segment)
    segment = re.sub(r"(?<!\.)\bTRUE\b(?!\s*\.)", "1", segment, flags=re.IGNORECASE)
    segment = re.sub(r"(?<!\.)\bFALSE\b(?!\s*\.)", "0", segment, flags=re.IGNORECASE)
    return _PATH_RE.sub(_quote_path, segment)


def _translate_expression(expression: str) -> str:
    """Translate validated Cosmos expression tokens to Fabric T-SQL."""
    parts: list[str] = []
    position = 0
    for match in _STRING_LITERAL_RE.finditer(expression):
        parts.append(_rewrite_sql_segment(expression[position : match.start()]))
        parts.append(match.group(0))
        position = match.end()
    parts.append(_rewrite_sql_segment(expression[position:]))
    return "".join(parts)


def emit_fabric_sql(ast: QueryAst, config: MirrorServingConfiguration) -> str:
    """Emit Fabric SQL from parsed Cosmos query AST.

    Args:
        ast: Parsed query AST
        config: Mirror serving configuration

    Returns:
        Fabric SQL query string (may contain @param references)

    Raises:
        ConfigurationError: If config is invalid
    """
    table_sql = default_table_sql(config)
    select_expr = _translate_expression(ast.select_expr)
    source_alias = ast.source_alias

    # Handle TOP + ORDER BY (no offset)
    # Note: TOP and OFFSET/FETCH values are safe from injection because the parser
    # validates they are integer literals before they reach this emitter.
    if ast.limit is not None and ast.offset is None:
        sql = f"SELECT TOP {ast.limit} {select_expr} FROM {table_sql} AS {source_alias}"
        if ast.where_expr:
            sql += f" WHERE {_translate_expression(ast.where_expr)}"
        if ast.group_by:
            sql += f" GROUP BY {_translate_expression(ast.group_by)}"
        if ast.having_expr:
            sql += f" HAVING {_translate_expression(ast.having_expr)}"
        if ast.order_by:
            sql += f" ORDER BY {_translate_expression(ast.order_by)}"
        return sql

    # Standard SELECT
    sql = f"SELECT {select_expr} FROM {table_sql} AS {source_alias}"
    if ast.where_expr:
        sql += f" WHERE {_translate_expression(ast.where_expr)}"
    if ast.group_by:
        sql += f" GROUP BY {_translate_expression(ast.group_by)}"
    if ast.having_expr:
        sql += f" HAVING {_translate_expression(ast.having_expr)}"
    if ast.order_by:
        sql += f" ORDER BY {_translate_expression(ast.order_by)}"

    # OFFSET/LIMIT (requires ORDER BY in Fabric SQL)
    if ast.offset is not None and ast.order_by is None:
        from ..errors import UnsupportedCosmosQueryError

        raise UnsupportedCosmosQueryError(
            "OFFSET/LIMIT requires ORDER BY in Fabric SQL"
        )
    if ast.offset is not None and ast.limit is None:
        from ..errors import UnsupportedCosmosQueryError

        raise UnsupportedCosmosQueryError("OFFSET requires LIMIT in Fabric SQL")
    if ast.offset is not None and ast.limit is not None:
        sql += f" OFFSET {ast.offset} ROWS FETCH NEXT {ast.limit} ROWS ONLY"

    return sql
