# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep reviewed AST fingerprints independent of Python's dump formatting."""

import ast


def stable_ast_dump(node):
    """Use the compact field representation used by the Python 3.13 ledgers.

    Omit empty lists and absent optional fields, not meaningful values or
    nonempty fields introduced by newer Python versions.
    """
    if isinstance(node, ast.AST):
        fields = []
        for name, value in ast.iter_fields(node):
            if value is None and getattr(type(node), name, ...) is None:
                continue
            if isinstance(value, list) and not value:
                continue
            fields.append(f"{name}={stable_ast_dump(value)}")
        return f"{type(node).__name__}({', '.join(fields)})"
    if isinstance(node, list):
        return f"[{', '.join(stable_ast_dump(value) for value in node)}]"
    return repr(node)
