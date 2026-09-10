# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cosmos SQL subset parser using lark."""

from __future__ import annotations

import re as _re

from lark import Lark, Transformer, Tree

from ..errors import UnsupportedCosmosQueryError
from .ast import QueryAst

_STRING_LITERAL_RE = _re.compile(r"'(?:''|[^'])*'")
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

select: "SELECT"i PROJ_EXPR

// Projection expression - may include VALUE keyword
PROJ_EXPR: /.+?(?=\s+FROM\s+)/is

from_clause: "FROM"i NAME ("AS"i? NAME)?
where_clause: "WHERE"i WHERE_EXPR
WHERE_EXPR: /.+?(?=\s+GROUP\s+BY\s+|\s+ORDER\s+BY\s+|\s+OFFSET\s+\d+\s+LIMIT\s+\d+|$)/is

group_clause: "GROUP"i "BY"i GROUP_EXPR
GROUP_EXPR: /.+?(?=\s+HAVING\s+|\s+ORDER\s+BY\s+|\s+OFFSET\s+\d+\s+LIMIT\s+\d+|$)/is

having_clause: "HAVING"i HAVING_EXPR
HAVING_EXPR: /.+?(?=\s+ORDER\s+BY\s+|\s+OFFSET\s+\d+\s+LIMIT\s+\d+|$)/is

order_clause: "ORDER"i "BY"i ORDER_EXPR
ORDER_EXPR: /.+?(?=\s+OFFSET\s+\d+\s+LIMIT\s+\d+|$)/is

offset_clause: "OFFSET"i INT "LIMIT"i INT

%import common.CNAME -> NAME
%import common.INT
%import common.WS
%ignore WS
"""

_EXPRESSION_GRAMMAR = r"""
projection: projection_item ("," projection_item)*
projection_item: expr ("AS"i NAME)?
expression_list: expr ("," expr)*
order_list: order_item ("," order_item)*
order_item: expr ("ASC"i | "DESC"i)?

?expr: or_expr
?or_expr: and_expr ("OR"i and_expr)*
?and_expr: not_expr ("AND"i not_expr)*
?not_expr: "NOT"i not_expr
         | comparison
?comparison: sum_expr (COMPARISON_OP sum_expr)?
?sum_expr: term (ADD_OP term)*
?term: factor (MULTIPLY_OP factor)*
?factor: "-" factor
       | atom
?atom: function
     | path
     | PARAMETER
     | NUMBER
     | STRING
     | "TRUE"i
     | "FALSE"i
     | "NULL"i
     | "*"
     | "(" expr ")"
function: AGGREGATE_FUNCTION "(" [expr ("," expr)*] ")"
path: NAME ("." NAME)*

AGGREGATE_FUNCTION.2: "COUNT"i | "SUM"i | "MAX"i | "MIN"i | "AVG"i
COMPARISON_OP: "=" | "!=" | "<>" | "<=" | ">=" | "<" | ">"
ADD_OP: "+" | "-"
MULTIPLY_OP: "*" | "/" | "%"
PARAMETER: /@[A-Za-z_][A-Za-z0-9_]*/
STRING: /'(?:''|[^'])*'/
NAME: /[A-Za-z_][A-Za-z0-9_]*/
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
"""


class _Transformer(Transformer):
    """Transform lark parse tree to QueryAst."""

    def query(self, items):
        """Build QueryAst from parsed components."""
        select_ast: QueryAst = items[0]
        source_alias = items[1][1]
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

        if offset is not None and select_ast.limit is not None:
            raise UnsupportedCosmosQueryError(
                "TOP cannot be combined with OFFSET/LIMIT"
            )

        return QueryAst(
            select_value=select_ast.select_value,
            select_expr=select_ast.select_expr,
            source_alias=source_alias,
            where_expr=where,
            group_by=group_by,
            having_expr=having,
            order_by=order,
            offset=offset,
            limit=limit if limit is not None else select_ast.limit,
        )

    def select(self, items):
        """Parse SELECT clause, detecting VALUE keyword manually."""
        if not items:
            raise UnsupportedCosmosQueryError("Empty SELECT expression")

        expr_str = str(items[0]).strip()
        limit = None
        top_match = _re.match(
            r"TOP\s+(\d+)\s+(.+)\Z", expr_str, _re.IGNORECASE | _re.DOTALL
        )
        if top_match:
            limit = int(top_match.group(1))
            expr_str = top_match.group(2).strip()

        # Check if expression starts with VALUE keyword
        has_value = False
        if expr_str.upper().startswith("VALUE "):
            has_value = True
            expr_str = expr_str[6:].strip()  # Remove 'VALUE '

        if not expr_str:
            raise UnsupportedCosmosQueryError("Empty SELECT expression after VALUE")

        return QueryAst(
            select_value=has_value,
            select_expr=expr_str,
            source_alias="",
            where_expr=None,
            group_by=None,
            having_expr=None,
            order_by=None,
            offset=None,
            limit=limit,
        )

    def from_clause(self, items):
        """Use the explicit alias when present, otherwise the source name."""
        return ("from", str(items[-1]))

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
_EXPRESSION_PARSER = Lark(
    _EXPRESSION_GRAMMAR,
    start=["projection", "expr", "expression_list", "order_list"],
    parser="lalr",
)
_TRANSFORM = _Transformer()


def _validate_expression(text: str, start: str) -> Tree:
    """Validate a clause against the supported expression subset."""
    try:
        return _EXPRESSION_PARSER.parse(text, start=start)
    except Exception as exc:
        raise UnsupportedCosmosQueryError(
            f"Unsupported expression in {start}: {exc}"
        ) from exc


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
        if any(token in masked for token in (";", "--", "/*", "*/")):
            raise UnsupportedCosmosQueryError(
                "SQL statement delimiters and comments are not supported"
            )
        if len(_re.findall(r"(?<!\.)\bSELECT\b", masked, _re.IGNORECASE)) != 1:
            raise UnsupportedCosmosQueryError("Subqueries are not supported")
        tree = _PARSER.parse(masked)
        ast = _TRANSFORM.transform(tree)
        select_expr = _unmask_string_literals(ast.select_expr, literals)
        where_expr = (
            _unmask_string_literals(ast.where_expr, literals)
            if ast.where_expr
            else None
        )
        group_by = (
            _unmask_string_literals(ast.group_by, literals) if ast.group_by else None
        )
        having_expr = (
            _unmask_string_literals(ast.having_expr, literals)
            if ast.having_expr
            else None
        )
        order_by = (
            _unmask_string_literals(ast.order_by, literals) if ast.order_by else None
        )

        projection = _validate_expression(select_expr, "projection")
        if ast.select_value and len(projection.children) != 1:
            raise UnsupportedCosmosQueryError(
                "SELECT VALUE requires exactly one projection expression"
            )
        if where_expr:
            _validate_expression(where_expr, "expr")
        if group_by:
            _validate_expression(group_by, "expression_list")
        if having_expr:
            _validate_expression(having_expr, "expr")
        if order_by:
            _validate_expression(order_by, "order_list")

        return QueryAst(
            select_value=ast.select_value,
            select_expr=select_expr,
            source_alias=ast.source_alias,
            where_expr=where_expr,
            group_by=group_by,
            having_expr=having_expr,
            order_by=order_by,
            offset=ast.offset,
            limit=ast.limit,
        )
    except UnsupportedCosmosQueryError:
        raise
    except Exception as exc:
        raise UnsupportedCosmosQueryError(
            f"Unsupported or invalid Cosmos SQL: {exc}"
        ) from exc
