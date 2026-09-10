# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parameter mapping from Cosmos @ parameters to driver ? placeholders."""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from typing import Any, Iterable

from ..errors import UnsupportedCosmosQueryError

_PARAM_OR_STRING_RE = re.compile(r"('(?:''|[^'])*')|@([A-Za-z_][A-Za-z0-9_]*)")
_STRING_LITERAL_RE = re.compile(r"'(?:''|[^'])*'")
_SQL_IDENTIFIER = r"(?:[A-Za-z_][A-Za-z0-9_]*|\[[^\]]+\])"
_SQL_PATH = rf"\(*{_SQL_IDENTIFIER}(?:\.{_SQL_IDENTIFIER})*\)*"
_NULL_PARAMETER = r"\(*@(?P<name>[A-Za-z_][A-Za-z0-9_]*)\)*"
_NULL_PARAM_COMPARISON_RE = re.compile(
    rf"(?P<left>{_SQL_PATH})\s*(?P<operator>=|!=|<>)\s*{_NULL_PARAMETER}"
    r"(?![A-Za-z0-9_.]|\s*[+\-*/%])"
)
_REVERSED_NULL_PARAM_COMPARISON_RE = re.compile(
    rf"{_NULL_PARAMETER}\s*(?P<operator>=|!=|<>)\s*(?P<right>{_SQL_PATH})"
    r"(?![A-Za-z0-9_.]|\s*[+\-*/%])"
)


@dataclass(frozen=True)
class ParameterizedSql:
    """SQL with ordered parameters for driver execution.

    Attributes:
        sql: SQL string with ? placeholders
        params: Parameter values in order
    """

    sql: str
    params: list[Any]


def parameterize(
    sql_with_at_params: str, parameters: Iterable[dict[str, Any]] | None
) -> ParameterizedSql:
    """Replace @param references with ? and build ordered parameter list.

    Args:
        sql_with_at_params: SQL with @paramName references
        parameters: List of parameter dicts with 'name' and 'value' keys

    Returns:
        ParameterizedSql with ? placeholders and ordered params

    Raises:
        UnsupportedCosmosQueryError: If referenced parameter is missing
    """
    # Build parameter lookup dict
    params_by_name: dict[str, Any] = {}
    if parameters:
        for p in parameters:
            name = str(p.get("name") or "")
            if name.startswith("@"):  # Cosmos SDK uses '@name'
                name = name[1:]
            params_by_name[name] = p.get("value")

    null_parameter_names: set[str] = set()

    def rewrite_null_parameters(segment: str) -> str:
        upper_segment = segment.upper()
        clause_positions = [
            position
            for delimiter in (" WHERE ", " HAVING ")
            if (position := upper_segment.find(delimiter)) >= 0
        ]
        condition = segment[min(clause_positions) :] if clause_positions else segment
        for name, value in params_by_name.items():
            if value is None:
                if re.search(rf"@{re.escape(name)}\b", condition) and re.search(
                    r"[+\-*/%]", condition
                ):
                    raise UnsupportedCosmosQueryError(
                        f"Null parameter @{name} cannot be combined with arithmetic expressions"
                    )

        def rewrite(match: re.Match[str]) -> str:
            name = match.group("name")
            if name not in params_by_name or params_by_name[name] is not None:
                return match.group(0)
            null_parameter_names.add(name)
            operator = "IS" if match.group("operator") == "=" else "IS NOT"
            operand = match.groupdict().get("left") or match.group("right")
            return f"{operand.strip()} {operator} NULL"

        segment = _NULL_PARAM_COMPARISON_RE.sub(rewrite, segment)
        return _REVERSED_NULL_PARAM_COMPARISON_RE.sub(rewrite, segment)

    parts: list[str] = []
    position = 0
    for string_match in _STRING_LITERAL_RE.finditer(sql_with_at_params):
        parts.append(
            rewrite_null_parameters(sql_with_at_params[position : string_match.start()])
        )
        parts.append(string_match.group(0))
        position = string_match.end()
    parts.append(rewrite_null_parameters(sql_with_at_params[position:]))
    sql_with_at_params = "".join(parts)

    # Track bound parameter usage order
    used_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        """Replace @param with ? but skip quoted strings."""
        if match.group(1):  # Quoted string — keep as-is
            return match.group(0)
        name = match.group(2)
        if name in params_by_name and params_by_name[name] is None:
            raise UnsupportedCosmosQueryError(
                f"Null parameter @{name} must be used in a direct equality or inequality comparison"
            )
        used_names.append(name)
        return "?"

    # Match quoted strings (skip) or @param (replace)
    sql = _PARAM_OR_STRING_RE.sub(repl, sql_with_at_params)

    # Build ordered parameter list
    try:
        ordered = [params_by_name[n] for n in used_names]
    except KeyError as exc:
        raise UnsupportedCosmosQueryError(
            f"Missing parameter value for @{exc.args[0]}"
        ) from exc

    # Warn about unused parameters
    if params_by_name:
        unused = set(params_by_name.keys()) - set(used_names) - null_parameter_names
        if unused:
            warnings.warn(
                f"Unused query parameters: {', '.join('@' + n for n in sorted(unused))}"
            )

    return ParameterizedSql(sql=sql, params=ordered)
