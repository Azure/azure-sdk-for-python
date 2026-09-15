# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""One-time, comment-preserving refactor of internal generated type references."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from lazy_model_emitter import canonical, definitions


class Qualify(ast.NodeTransformer):
    def __init__(self, names):
        self.names = names

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.names:
            return ast.copy_location(ast.parse(self.names[node.id], mode="eval").body, node)
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            try:
                value = ast.parse(node.value, mode="eval")
            except SyntaxError:
                return node
            return ast.copy_location(ast.Constant(ast.unparse(self.visit(value))), node)
        return node

    def visit_Subscript(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "Literal":
            return node
        return self.generic_visit(node)


def refactor(path, generated_names):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    starts, total = [], 0
    for line in lines:
        starts.append(total)
        total += len(line)

    def offset(line, column):
        return starts[line - 1] + len(lines[line - 1].encode()[:column].decode())

    def span(node):
        return offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)

    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    edits = []
    names, imports = {}, set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if not (module.endswith("models") or "_generated" in module):
            continue
        selected = [alias for alias in node.names if alias.name in generated_names]
        if not selected:
            continue
        alias_name = (
            "_generated_unions"
            if module.endswith("_unions")
            else "_generated_models" if "_generated" in module else "_public_models"
        )
        head, _, tail = module.rpartition(".")
        statement = f"from {'.' * node.level}{head} import {tail or module} as {alias_name}"
        imports.add(statement)
        for alias in selected:
            names[alias.asname or alias.name] = f"{alias_name}.{alias.name}"
        remaining = [alias for alias in node.names if alias not in selected]
        replacement = ""
        if remaining:
            replacement = f"from {'.' * node.level}{module} import " + ", ".join(
                alias.name + (f" as {alias.asname}" if alias.asname else "") for alias in remaining
            )
        elif isinstance(parents.get(node), ast.If) and len(parents[node].body) == 1:
            replacement = "pass"
        edits.append((*span(node), replacement))
    model_modules = {"generated_models", "response_models", "_generated_models", "_public_models", "_generated_unions"}
    existing_model_casts = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "cast"
        and node.args
        and any(isinstance(child, ast.Name) and child.id in model_modules for child in ast.walk(node.args[0]))
        for node in ast.walk(tree)
    )
    if not names and not existing_model_casts:
        return False
    qualifier = Qualify(names)
    protected = [item[:2] for item in edits]

    def within(node):
        start, end = span(node)
        return any(a <= start and end <= b for a, b in protected)

    def changed_type(node):
        return ast.unparse(ast.fix_missing_locations(qualifier.visit(ast.parse(ast.unparse(node), mode="eval").body)))

    def has_generated(node):
        return any(
            isinstance(child, ast.Name) and (child.id in names or child.id in model_modules) for child in ast.walk(node)
        )

    # Casts have no runtime type checking. Keep the type expression for type checkers only.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "cast" and node.args:
            arg = node.args[0]
            if has_generated(arg) and not within(arg):
                a, b = span(arg)
                edits.append((a, b, repr(changed_type(arg))))
                protected.append((a, b))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_is_type"
            and len(node.args) == 3
        ):
            arg = node.args[1]
            if has_generated(arg):
                a, b = span(arg)
                edits.append((a, b, repr(changed_type(arg))))
                protected.append((a, b))

    for node in ast.walk(tree):
        annotations = []
        if isinstance(node, ast.AnnAssign):
            annotations.append(node.annotation)
        elif isinstance(node, ast.arg) and node.annotation is not None:
            annotations.append(node.annotation)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None:
            annotations.append(node.returns)
        for annotation in annotations:
            if not within(annotation):
                updated = changed_type(annotation)
                a, b = span(annotation)
                if ast.dump(ast.parse(updated, mode="eval").body) != ast.dump(annotation):
                    edits.append((a, b, updated))
                protected.append((a, b))

    # The routing layer's public callable aliases are typing-only, not model constructors.
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript) and has_generated(node.value):

            def forward_names(item):
                if isinstance(item, ast.Name) and item.id in names:
                    return ast.copy_location(ast.Constant(names[item.id]), item)
                for field, value in ast.iter_fields(item):
                    if isinstance(value, ast.AST):
                        setattr(item, field, forward_names(value))
                    elif isinstance(value, list):
                        setattr(item, field, [forward_names(v) if isinstance(v, ast.AST) else v for v in value])
                return item

            value = ast.parse(ast.unparse(node.value), mode="eval").body
            updated = ast.unparse(ast.fix_missing_locations(forward_names(value)))
            a, b = span(node.value)
            edits.append((a, b, updated))
            protected.append((a, b))

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in names and not within(node):
            edits.append((*span(node), names[node.id]))

    # Keep module aliases globally available to public get_type_hints().
    insertion = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        insertion = span(tree.body[0])[1]
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            insertion = span(node)[1]
    header = "\n" + "\n".join(sorted(imports)) + "\n"
    if not any(isinstance(node, ast.ImportFrom) and node.module == "__future__" for node in tree.body):
        header = "\nfrom __future__ import annotations\n" + header
    edits.append((insertion, insertion, header))
    for start, end, replacement in sorted(edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    ast.parse(source)
    path.write_text(source, encoding="utf-8")
    return True


def main():
    root = Path(__file__).resolve().parents[1] / "azure" / "ai" / "agentserver" / "responses"
    generated = root / "models" / "_generated"
    names = set()
    for name in ("types.py", "_unions.py"):
        names.update(definitions(ast.parse(canonical((generated / name).read_text()))))
    changed = []
    for path in sorted(root.rglob("*.py")):
        if "_generated" in path.parts or path in (root / "__init__.py", root / "models" / "__init__.py"):
            continue
        if path.name in ("_lazy_models.py", "_request_validators.py"):
            continue
        if refactor(path, names):
            changed.append(path.relative_to(root).as_posix())
    print(json.dumps(changed, indent=2))


if __name__ == "__main__":
    main()
