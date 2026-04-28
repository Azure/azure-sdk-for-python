# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cosmos SQL subset parser using lark."""

from __future__ import annotations

import re as _re

from lark import Lark, Transformer

from ..errors import UnsupportedCosmosQueryError
from .ast import QueryAst

_STRING_LITERAL_RE = _re.compile(r"'[^']*'")
_PLACEHOLDER_PREFIX = "\x00STR"


def _mask_string_literals(query: str) -> tuple[str, list[str]]:
    """Replace single-quoted strings with placeholders to prevent keyword collisions."""
    literals: list[str] = []

    def _replace(m: _re.Match) -> str:
        literals.append(m.group(0))
        return f"{_PLACEHOLDER_PREFIX}{len(literals) - 1}\x00"

    masked = _STRING_LITERAL_RE.sub(_replace, query)
    return masked, literals


def _unmask_string_literals(text: str, literals: list[str]) -> str:
    """Restore masked string literals."""
    for i, lit in enumerate(literals):
        text = text.replace(f"{_PLACEHOLDER_PREFIX}{i}\x00", lit)
    return text


# Grammar for the supported Cosmos SQL subset
_GRAMMAR = r"""
?start: query

query: select from_clause where_clause? group_clause? having_clause? order_clause? offset_clause?

select: "SELECT"i top_clause? PROJ_EXPR
top_clause: "TOP"i INT

// Projection expression - may include VALUE keyword
PROJ_EXPR: /.+?(?=\bFROM\b)/is

from_clause: "FROM"i NAME
where_clause: "WHERE"i WHERE_EXPR
WHERE_EXPR: /.+?(?=\bGROUP\b|\bORDER\b|\bOFFSET\b|$)/is

group_clause: "GROUP"i "BY"i GROUP_EXPR
GROUP_EXPR: /.+?(?=\bHAVING\b|\bORDER\b|\bOFFSET\b|$)/is

having_clause: "HAVING"i HAVING_EXPR
HAVING_EXPR: /.+?(?=\bORDER\b|\bOFFSET\b|$)/is

order_clause: "ORDER"i "BY"i ORDER_EXPR
ORDER_EXPR: /.+?(?=\bOFFSET\b|$)/is

offset_clause: "OFFSET"i INT "LIMIT"i INT

%import common.CNAME -> NAME
%import common.INT
%import common.WS
%ignore WS
"""


class _Transformer(Transformer):
    """Transform lark parse tree to QueryAst."""

    def query(self, items):
        """Build QueryAst from parsed components."""
        select_ast: QueryAst = items[0]
        where = None
        group_by = None
        having = None
        order = None
        offset = None
        limit = None
        
        # Process optional clauses (starting from index 2, after select and from)
        for node in items[2:]:
            if isinstance(node, tuple):
                if node[0] == "where":
                    where = node[1]
                elif node[0] == "group":
                    group_by = node[1]
                elif node[0] == "having":
                    having = node[1]
                elif node[0] == "order":
                    order = node[1]
                elif node[0] == "offset":
                    offset = node[1]
                    limit = node[2]
        
        return QueryAst(
            select_value=select_ast.select_value,
            select_expr=select_ast.select_expr,
            where_expr=where,
            group_by=group_by,
            having_expr=having,
            order_by=order,
            offset=offset,
            limit=limit if limit is not None else select_ast.limit,
        )

    def select(self, items):
        """Parse SELECT clause, detecting VALUE keyword manually."""
        limit = None
        expr_token = None
        
        for item in items:
            if isinstance(item, tuple) and item[0] == "top":
                limit = item[1]
            else:
                # Should be PROJ_EXPR terminal
                expr_token = item
        
        if not expr_token:
            raise UnsupportedCosmosQueryError("Empty SELECT expression")
        
        expr_str = str(expr_token).strip()
        
        # Check if expression starts with VALUE keyword
        has_value = False
        if expr_str.upper().startswith('VALUE '):
            has_value = True
            expr_str = expr_str[6:].strip()  # Remove 'VALUE '
        
        if not expr_str:
            raise UnsupportedCosmosQueryError("Empty SELECT expression after VALUE")
        
        return QueryAst(
            select_value=has_value,
            select_expr=expr_str,
            where_expr=None,
            group_by=None,
            having_expr=None,
            order_by=None,
            offset=None,
            limit=limit,
        )
    
    def top_clause(self, items):
        """Parse TOP clause."""
        return ("top", int(items[0]))

    def where_clause(self, items):
        """Parse WHERE clause."""
        return ("where", str(items[0]).strip())

    def group_clause(self, items):
        """Parse GROUP BY clause."""
        return ("group", str(items[0]).strip())

    def having_clause(self, items):
        """Parse HAVING clause."""
        return ("having", str(items[0]).strip())

    def order_clause(self, items):
        """Parse ORDER BY clause."""
        return ("order", str(items[0]).strip())

    def offset_clause(self, items):
        """Parse OFFSET ... LIMIT ... clause."""
        return ("offset", int(items[0]), int(items[1]))


_PARSER = Lark(_GRAMMAR, start="start", parser="lalr")
_TRANSFORM = _Transformer()


def parse_cosmos_sql(query_text: str) -> QueryAst:
    """Parse a Cosmos SQL query into an AST.
    
    Args:
        query_text: Cosmos SQL query string
        
    Returns:
        Parsed QueryAst
        
    Raises:
        UnsupportedCosmosQueryError: If query uses unsupported features or has syntax errors
    """
    try:
        masked, literals = _mask_string_literals(query_text.strip())
        tree = _PARSER.parse(masked)
        ast = _TRANSFORM.transform(tree)
        return QueryAst(
            select_value=ast.select_value,
            select_expr=_unmask_string_literals(ast.select_expr, literals),
            where_expr=_unmask_string_literals(ast.where_expr, literals) if ast.where_expr else None,
            group_by=_unmask_string_literals(ast.group_by, literals) if ast.group_by else None,
            having_expr=_unmask_string_literals(ast.having_expr, literals) if ast.having_expr else None,
            order_by=_unmask_string_literals(ast.order_by, literals) if ast.order_by else None,
            offset=ast.offset,
            limit=ast.limit,
        )
    except UnsupportedCosmosQueryError:
        raise
    except Exception as exc:
        raise UnsupportedCosmosQueryError(f"Unsupported or invalid Cosmos SQL: {exc}") from exc
