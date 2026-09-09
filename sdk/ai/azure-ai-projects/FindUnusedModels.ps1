# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$PythonExecutable = "python",
    [string]$ModelsPath = (Join-Path $PSScriptRoot "azure\ai\projects\models\_models.py"),
    [string]$OutputPath = (Join-Path $PSScriptRoot "unused-models-report.md"),
    [switch]$FailOnCandidates
)

$ErrorActionPreference = "Stop"
$packageRoot = $PSScriptRoot
$temporaryScript = Join-Path ([System.IO.Path]::GetTempPath()) ("find-unused-models-{0}.py" -f [guid]::NewGuid())

$pythonScript = @'
from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
import re
import sys
from typing import Iterable


package_root = Path(sys.argv[1]).resolve()
models_path = Path(sys.argv[2]).resolve()
output_path = Path(sys.argv[3]).resolve()

excluded_directories = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def parse_python(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as error:
        raise RuntimeError(f"Unable to parse {path}: {error}") from error


def body_without_docstring(body: list[ast.stmt]) -> Iterable[ast.stmt]:
    if body and isinstance(body[0], ast.Expr):
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return body[1:]
    return body


class ReferenceCollector(ast.NodeVisitor):
    def __init__(self, known_models: set[str]) -> None:
        self.known_models = known_models
        self.references: set[str] = set()

    def add_string_references(self, value: str) -> None:
        for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", value):
            if name in self.known_models:
                self.references.add(name)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.known_models:
            self.references.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in self.known_models:
            self.references.add(node.attr)
        self.visit(node.value)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            self.add_string_references(node.value)

    def visit_Module(self, node: ast.Module) -> None:
        for statement in body_without_docstring(node.body):
            self.visit(statement)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in [*node.decorator_list, *node.bases, *node.keywords]:
            self.visit(child)
        for statement in body_without_docstring(node.body):
            self.visit(statement)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for child in [*node.decorator_list, node.args]:
            self.visit(child)
        if node.returns:
            self.visit(node.returns)
        for statement in body_without_docstring(node.body):
            self.visit(statement)

    visit_AsyncFunctionDef = visit_FunctionDef


def collect_references(node: ast.AST, known_models: set[str]) -> set[str]:
    collector = ReferenceCollector(known_models)
    collector.visit(node)
    return collector.references


def find_public_exports(init_path: Path, known_models: set[str]) -> set[str]:
    exports: set[str] = set()
    for node in parse_python(init_path).body:
        if isinstance(node, ast.ImportFrom) and node.module == "_models":
            exports.update(alias.name for alias in node.names if alias.name in known_models)
    return exports


def python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not any(part in excluded_directories or part.startswith(".venv") for part in path.parts):
            yield path


def reachable_models(roots: set[str], dependencies: dict[str, set[str]]) -> set[str]:
    reachable: set[str] = set()
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        pending.extend(dependencies[name] - reachable)
    return reachable


def format_names(names: Iterable[str]) -> str:
    values = sorted(names)
    return ", ".join(f"`{name}`" for name in values) if values else "None"


models_tree = parse_python(models_path)
model_nodes = {
    node.name: node
    for node in models_tree.body
    if isinstance(node, ast.ClassDef)
}
known_models = set(model_nodes)

dependencies: dict[str, set[str]] = {}
for name, node in model_nodes.items():
    dependencies[name] = collect_references(node, known_models) - {name}

reverse_dependencies: dict[str, set[str]] = defaultdict(set)
for name, referenced_models in dependencies.items():
    for referenced_model in referenced_models:
        reverse_dependencies[referenced_model].add(name)

models_init_path = models_path.parent / "__init__.py"
public_exports = find_public_exports(models_init_path, known_models)

external_references: dict[str, set[str]] = defaultdict(set)
for path in python_files(package_root):
    if path.resolve() == models_path:
        continue
    relative_path = path.relative_to(package_root).as_posix()
    for name in collect_references(parse_python(path), known_models):
        external_references[name].add(relative_path)

external_roots = set(external_references)
roots = public_exports | external_roots
reachable = reachable_models(roots, dependencies)
candidates = known_models - reachable

lines = [
    "# Unused generated model analysis",
    "",
    "<!-- Generated by FindUnusedModels.ps1. Do not edit manually. -->",
    "",
    "This is a conservative static reachability analysis. A class is a removal candidate only when it is not "
    "publicly exported and cannot be reached from any Python reference outside `_models.py`. Dynamic references "
    "constructed at runtime are not detectable; regenerate the SDK and run its tests after removing any candidate.",
    "",
    "## Summary",
    "",
    f"- Models defined: {len(known_models)}",
    f"- Publicly exported roots: {len(public_exports)}",
    f"- Models referenced outside `_models.py`: {len(external_roots)}",
    f"- Reachable models: {len(reachable)}",
    f"- Removal candidates: {len(candidates)}",
    "",
    "## Removal candidates",
    "",
]

if candidates:
    lines.extend(
        [
            "| Model | Line | Referenced by removable models | References removable models | References retained models |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for name in sorted(candidates):
        removable_dependents = reverse_dependencies[name] & candidates
        removable_dependencies = dependencies[name] & candidates
        retained_dependencies = dependencies[name] & reachable
        lines.append(
            f"| `{name}` | {model_nodes[name].lineno} | {format_names(removable_dependents)} | "
            f"{format_names(removable_dependencies)} | {format_names(retained_dependencies)} |"
        )

    lines.extend(["", "## Dependency details", ""])
    for name in sorted(candidates):
        lines.extend(
            [
                f"### `{name}`",
                "",
                f"- Can be removed with this model: {format_names(dependencies[name] & candidates)}",
                f"- Must be retained independently: {format_names(dependencies[name] & reachable)}",
                f"- Other removable models that reference it: {format_names(reverse_dependencies[name] & candidates)}",
                "- References outside `_models.py`: None",
                "",
            ]
        )
else:
    lines.extend(["No statically unreachable model classes were found.", ""])

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

print(f"Analyzed {len(known_models)} models; found {len(candidates)} removal candidates.")
print(f"Report: {output_path}")
for name in sorted(candidates):
    removable_dependencies = dependencies[name] & candidates
    suffix = f" (also removable: {', '.join(sorted(removable_dependencies))})" if removable_dependencies else ""
    print(f"  {name}{suffix}")

raise SystemExit(2 if candidates and sys.argv[4] == "true" else 0)
'@

try {
    [System.IO.File]::WriteAllText($temporaryScript, $pythonScript, [System.Text.UTF8Encoding]::new($false))
    $failOnCandidatesArgument = if ($FailOnCandidates) { "true" } else { "false" }
    & $PythonExecutable $temporaryScript $packageRoot $ModelsPath $OutputPath $failOnCandidatesArgument
    $exitCode = $LASTEXITCODE
    if ($exitCode -notin 0, 2) {
        throw "Unused model analysis failed with exit code $exitCode."
    }
    if ($exitCode -eq 2) {
        throw "Unused model analysis found removal candidates. See $OutputPath."
    }
}
finally {
    Remove-Item $temporaryScript -Force 