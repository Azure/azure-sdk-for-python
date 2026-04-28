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


# Match quoted strings (skip) or @param (replace)
_PARAM_OR_STRING_RE = re.compile(r"('[^']*')|@([A-Za-z_][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class ParameterizedSql:
    """SQL with ordered parameters for driver execution.
    
    Attributes:
        sql: SQL string with ? placeholders
        params: Parameter values in order
    """
    
    sql: str
    params: list[Any]


def parameterize(sql_with_at_params: str, parameters: Iterable[dict[str, Any]] | None) -> ParameterizedSql:
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

    # Track parameter usage order
    used_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        """Replace @param with ? but skip quoted strings."""
        if match.group(1):  # Quoted string — keep as-is
            return match.group(0)
        name = match.group(2)
        used_names.append(name)
        return "?"

    # Match quoted strings (skip) or @param (replace)
    sql = _PARAM_OR_STRING_RE.sub(repl, sql_with_at_params)
    
    # Build ordered parameter list
    try:
        ordered = [params_by_name[n] for n in used_names]
    except KeyError as exc:
        raise UnsupportedCosmosQueryError(f"Missing parameter value for @{exc.args[0]}") from exc
    
    # Warn about unused parameters
    if params_by_name:
        unused = set(params_by_name.keys()) - set(used_names)
        if unused:
            warnings.warn(f"Unused query parameters: {', '.join('@' + n for n in sorted(unused))}")
    
    return ParameterizedSql(sql=sql, params=ordered)
