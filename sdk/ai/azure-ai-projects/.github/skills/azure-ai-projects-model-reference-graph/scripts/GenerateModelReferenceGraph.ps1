# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

<#
.SYNOPSIS
Generates and validates model-reference reports in the user's temp directory.
.DESCRIPTION
Uses the package virtual environment when available, otherwise Python on PATH.
JSON and TXT filenames share a UTC timestamp. Explicit output paths are supported.
Prints counts, unreferenced models, runtime owners, and absolute report locations;
returns GraphPath and TreePath. Use -ModelName for a model's complete reference entry.
Unreferenced excludes definitions and public exports, but includes union aliases,
runtime code, samples, tests, and inheritance. Operation reachability alone does not
prove safe removal: review TypeSpec, runtime consumers, discriminators, public exports,
and regenerated API impact before changing TypeSpec and regenerating the SDK.
Never delete generated classes directly.
#>
[CmdletBinding()]
param(
    [string]$PythonExecutable,
    [string]$ModelsPath,
    [string]$OutputPath,
    [string]$TreeOutputPath,
    [string]$ModelName
)

$ErrorActionPreference = "Stop"
$packageRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
if (-not $PythonExecutable) {
    $packagePython = Join-Path $packageRoot ".venv\Scripts\python.exe"
    $PythonExecutable = if (Test-Path -LiteralPath $packagePython -PathType Leaf) { $packagePython } else { "python" }
}
Get-Command -Name $PythonExecutable -CommandType Application -ErrorAction Stop | Out-Null
$tempDirectory = [System.IO.Path]::GetTempPath()
$timestamp = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss'Z'", [Globalization.CultureInfo]::InvariantCulture)
if (-not $ModelsPath) {
    $ModelsPath = Join-Path $packageRoot "azure\ai\projects\models\_models.py"
}
if (-not (Test-Path -LiteralPath $ModelsPath -PathType Leaf)) {
    throw "Required models file does not exist: $ModelsPath"
}
if (-not $OutputPath) {
    $OutputPath = Join-Path $tempDirectory "model-reference-graph-$timestamp.json"
}
if (-not $TreeOutputPath) {
    $TreeOutputPath = Join-Path $tempDirectory "model-reference-trees-$timestamp.txt"
}
$temporaryScript = Join-Path $tempDirectory ("generate-model-reference-graph-{0}.py" -f [guid]::NewGuid())

$pythonScript = @'
from __future__ import annotations

import ast
from collections import defaultdict, deque
import json
from pathlib import Path
import re
import sys
from typing import Iterable


package_root = Path(sys.argv[1]).resolve()
models_path = Path(sys.argv[2]).resolve()
output_path = Path(sys.argv[3]).resolve()
tree_output_path = Path(sys.argv[4]).resolve()
requested_model = sys.argv[5] if len(sys.argv) > 5 else ""
if output_path == tree_output_path:
    raise ValueError("JSON and TXT reports must use different output paths.")

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


def body_without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr):
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return body[1:]
    return body


class ReferenceCollector(ast.NodeVisitor):
    def __init__(self, known_symbols: set[str]) -> None:
        self.known_symbols = known_symbols
        self.references: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.known_symbols:
            self.references.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in self.known_symbols:
            self.references.add(node.attr)
        self.visit(node.value)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str):
            for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", node.value):
                if name in self.known_symbols:
                    self.references.add(name)

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


def collect_references(node: ast.AST, known_symbols: set[str]) -> set[str]:
    collector = ReferenceCollector(known_symbols)
    collector.visit(node)
    return collector.references


def python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not any(part in excluded_directories or part.startswith(".venv") for part in path.parts):
            yield path


def find_public_exports(init_path: Path, known_models: set[str]) -> set[str]:
    exports: set[str] = set()
    for node in parse_python(init_path).body:
        if isinstance(node, ast.ImportFrom) and node.module == "_models":
            exports.update(alias.name for alias in node.names if alias.name in known_models)
    return exports


def assignment_nodes(tree: ast.Module) -> dict[str, ast.AST]:
    assignments: dict[str, ast.AST] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            assignments[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments[node.target.id] = node.value
    return assignments


def scoped_references(tree: ast.Module, known_symbols: set[str]) -> dict[str, set[str]]:
    scopes: dict[str, set[str]] = defaultdict(set)
    module_nodes: list[ast.AST] = []
    for node in body_without_docstring(tree.body):
        if isinstance(node, ast.ClassDef):
            class_nodes: list[ast.AST] = [*node.decorator_list, *node.bases, *node.keywords]
            for statement in body_without_docstring(node.body):
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    scopes[f"{node.name}.{statement.name}"].update(
                        collect_references(statement, known_symbols)
                    )
                else:
                    class_nodes.append(statement)
            for class_node in class_nodes:
                scopes[node.name].update(collect_references(class_node, known_symbols))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes[node.name].update(collect_references(node, known_symbols))
        else:
            module_nodes.append(node)
    for module_node in module_nodes:
        scopes["<module>"].update(collect_references(module_node, known_symbols))
    return {name: references for name, references in scopes.items() if references}


models_tree = parse_python(models_path)
model_nodes = {
    node.name: node
    for node in models_tree.body
    if isinstance(node, ast.ClassDef)
}
known_models = set(model_nodes)
if requested_model and requested_model not in known_models:
    raise ValueError(f"Unknown model: {requested_model}")

unions_path = models_path.parent.parent / "_unions.py"
union_nodes = assignment_nodes(parse_python(unions_path))
known_unions = set(union_nodes)
known_symbols = known_models | known_unions

union_references = {
    name: collect_references(node, known_symbols) - {name}
    for name, node in union_nodes.items()
}
resolved_union_models: dict[str, set[str]] = {}


def models_for_union(name: str, resolving: set[str] | None = None) -> set[str]:
    if name in resolved_union_models:
        return resolved_union_models[name]
    resolving = set() if resolving is None else resolving
    if name in resolving:
        return set()
    resolving.add(name)
    symbols = union_references.get(name, set())
    models = set(symbols & known_models)
    for referenced_union in symbols & known_unions:
        models.update(models_for_union(referenced_union, resolving))
    resolving.remove(name)
    resolved_union_models[name] = models
    return models


def expand_models(symbols: set[str]) -> set[str]:
    models = set(symbols & known_models)
    for union_name in symbols & known_unions:
        models.update(models_for_union(union_name))
    return models


model_bases: dict[str, set[str]] = {}
model_dependencies: dict[str, set[str]] = {}
for name, node in model_nodes.items():
    base_symbols: set[str] = set()
    for base in node.bases:
        base_symbols.update(collect_references(base, known_symbols))
    model_bases[name] = expand_models(base_symbols) - {name}
    model_dependencies[name] = expand_models(collect_references(node, known_symbols)) - {name} - model_bases[name]

direct_model_referrers: dict[str, set[str]] = defaultdict(set)
for referring_model, referenced_models in model_dependencies.items():
    for referenced_model in referenced_models:
        direct_model_referrers[referenced_model].add(referring_model)

model_subclasses: dict[str, set[str]] = defaultdict(set)
for child_model, base_models in model_bases.items():
    for base_model in base_models:
        model_subclasses[base_model].add(child_model)

def outward_models(name: str) -> set[str]:
    return direct_model_referrers[name] | model_bases[name] | model_subclasses[name]

models_init_path = models_path.parent / "__init__.py"
public_exports = find_public_exports(models_init_path, known_models)
operation_references: dict[str, set[str]] = defaultdict(set)
other_references: dict[str, set[str]] = defaultdict(set)

union_location = unions_path.relative_to(package_root).as_posix()
for union_name in sorted(known_unions):
    for model_name in models_for_union(union_name):
        other_references[model_name].add(f"{union_location}::{union_name}")

for path in python_files(package_root):
    resolved_path = path.resolve()
    if resolved_path in {models_path, models_init_path, unions_path}:
        continue
    relative_path = path.relative_to(package_root)
    is_operation = "operations" in relative_path.parts
    references_by_scope = scoped_references(parse_python(path), known_symbols)
    for scope, symbols in references_by_scope.items():
        if is_operation and ("." not in scope or scope.rsplit(".", maxsplit=1)[-1].startswith("_")):
            continue
        location = f"{relative_path.as_posix()}::{scope}"
        target = operation_references if is_operation else other_references
        for model_name in expand_models(symbols):
            target[model_name].add(location)

# These protocol/runtime models are owned by public operations but are intentionally
# absent from their Python signatures: WebSocket messages flow over the upgraded
# connection, and the memory update result is consumed by a custom polling method.
# Verify protocol/custom transport evidence before changing these mappings.
runtime_operation_owners = {
    "RealtimeClientEvent": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "RealtimeServerEvent": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "RealtimeServerEventError": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "VoiceAgentClientEventSessionUpdate": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "VoiceAgentSessionResponseConfig": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "VoiceAgentSessionUpdateConfig": "azure/ai/projects/_realtime.py::BetaRealtime.connect",
    "MemoryStoreUpdateResult": "azure/ai/projects/operations/_patch_memories.py::BetaMemoryStoresOperations.begin_update_memories",
    "UpdateToolboxRequest": "azure/ai/projects/operations/_operations.py::ToolboxesOperations.update",
}
for model_name, operation in runtime_operation_owners.items():
    if model_name not in known_models:
        raise ValueError(f"Runtime ownership mapping names a missing model: {model_name}")
    owner_path, owner_scope = operation.split("::", maxsplit=1)
    owner_class, owner_method = owner_scope.split(".", maxsplit=1)
    owner_tree = parse_python(package_root / owner_path)
    if owner_method.startswith("_") or not any(
        isinstance(node, ast.ClassDef)
        and node.name == owner_class
        and any(
            isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            and member.name == owner_method
            for member in node.body
        )
        for node in owner_tree.body
    ):
        raise ValueError(f"Runtime ownership mapping names a missing or private method: {operation}")
    operation_references[model_name].add(operation)


def reverse_reachability(start: str) -> tuple[set[str], dict[str, tuple[str, ...]]]:
    reached: set[str] = set()
    shortest_paths: dict[str, tuple[str, ...]] = {start: (start,)}
    pending: deque[str] = deque([start])
    while pending:
        current = pending.popleft()
        for referrer in sorted(outward_models(current)):
            if referrer in shortest_paths:
                continue
            reached.add(referrer)
            shortest_paths[referrer] = (*shortest_paths[current], referrer)
            pending.append(referrer)
    return reached, shortest_paths


graph: dict[str, object] = {}
models_with_operation_paths = 0
for name in sorted(known_models):
    indirect_referrers, shortest_paths = reverse_reachability(name)
    direct_referrers = direct_model_referrers[name]
    indirect_only = indirect_referrers - direct_referrers - model_bases[name]

    direct_operations = set(operation_references[name])
    indirect_operations: set[str] = set()
    paths_to_operations: list[dict[str, object]] = []
    for referring_model, model_path in sorted(shortest_paths.items()):
        for operation in sorted(operation_references[referring_model]):
            if referring_model != name:
                indirect_operations.add(operation)
            paths_to_operations.append(
                {
                    "operation": operation,
                    "modelPath": list(reversed(model_path)),
                }
            )

    all_operations = direct_operations | indirect_operations
    if all_operations:
        models_with_operation_paths += 1

    all_other_references: set[str] = set(other_references[name])
    for referring_model in indirect_referrers:
        all_other_references.update(other_references[referring_model])

    graph[name] = {
        "definedLine": model_nodes[name].lineno,
        "publiclyExported": name in public_exports,
        "baseModels": sorted(model_bases[name]),
        "derivedModels": sorted(model_subclasses[name]),
        "referencesModels": sorted(model_dependencies[name]),
        "directModelReferrers": sorted(direct_referrers),
        "indirectModelReferrers": sorted(indirect_only),
        "directOperationReferences": sorted(direct_operations),
        "indirectOperationReferences": sorted(indirect_operations - direct_operations),
        "pathsToOperations": paths_to_operations,
        "otherReferences": sorted(all_other_references),
    }

models_without_operation_paths = [
    name for name in sorted(known_models) if not graph[name]["pathsToOperations"]
]
unreferenced_models = [
    name
    for name in sorted(known_models)
    if not outward_models(name) and not operation_references[name] and not other_references[name]
]

document = {
    "metadata": {
        "modelsPath": models_path.relative_to(package_root).as_posix(),
        "modelCount": len(known_models),
        "modelsWithOperationPaths": models_with_operation_paths,
        "modelsWithoutOperationPaths": len(models_without_operation_paths),
        "modelsWithoutOperationPathNames": models_without_operation_paths,
        "unreferencedModelCount": len(unreferenced_models),
        "unreferencedModelNames": unreferenced_models,
        "unreferencedModelCriteria": (
            "No model referrers, inheritance links, public operation references, or non-operation "
            "references (including union aliases); definitions and public exports are excluded."
        ),
        "explicitRuntimeOperationOwners": runtime_operation_owners,
        "pathSemantics": "Each path is operation -> referring models -> keyed model. One shortest model path is emitted for each reachable operation reference.",
    },
    "models": graph,
}


def operation_scope(location: str) -> str:
    return location.split("::", maxsplit=1)[-1]


def render_tree(root: str) -> list[str]:
    lines = [root]
    expanded = {root}

    def append_children(current: str, prefix: str, ancestors: set[str]) -> None:
        base_children = [("base", name) for name in sorted(model_bases[current])]
        derived_children = [
            ("derived", name)
            for name in sorted(model_subclasses[current] - ancestors)
        ]
        model_children = [
            ("model", name)
            for name in sorted(direct_model_referrers[current] - ancestors)
        ]
        operation_children = [
            ("operation", name)
            for name in sorted({operation_scope(location) for location in operation_references[current]})
        ]
        children = base_children + derived_children + model_children + operation_children
        if not children:
            lines.append(f"{prefix}`- [no model or operation referrer]")
            return

        for index, (kind, name) in enumerate(children):
            is_last = index == len(children) - 1
            connector = "`-" if is_last else "+-"
            child_prefix = f"{prefix}{'   ' if is_last else '|  '}"
            if kind == "operation":
                lines.append(f"{prefix}{connector} {name} [operation]")
                continue

            if kind == "base":
                label = f"{name} [base class]"
            elif kind == "derived":
                label = f"{name} [derived class]"
            else:
                label = name

            if name in ancestors:
                lines.append(f"{prefix}{connector} {label} [cycle]")
                continue
            if name in expanded:
                lines.append(f"{prefix}{connector} {label} [already expanded]")
                continue

            lines.append(f"{prefix}{connector} {label}")
            expanded.add(name)
            append_children(name, child_prefix, ancestors | {name})

    append_children(root, "  ", {root})
    return lines


output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(document, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
    newline="\n",
)

tree_lines = [
    "Model reference trees",
    "=====================",
    "",
    "Each root is a model from _models.py. Child models directly reference their parent.",
    "[base class] marks traversal from a derived model to a base type accepted by other models or operations.",
    "[derived class] marks traversal from a base model to a derived model used by other models or operations.",
    "Operation leaves are deduplicated across sync and async files by class and method name.",
    "[already expanded] marks a shared branch rendered elsewhere under the same root.",
    "[cycle] marks a reference cycle.",
    "",
    "Summary",
    "-------",
    "",
    f"Models: {len(known_models)}",
    f"Models with a path to a public operation: {models_with_operation_paths}",
    f"Models with no path to a public operation: {len(models_without_operation_paths)}",
    f"Unreferenced models: {len(unreferenced_models)}",
    "",
    "Unreferenced models (excluding definitions and public exports):",
    *([f"- {name}" for name in unreferenced_models] if unreferenced_models else ["- None"]),
    "",
    "These have no model referrers, inheritance links, operation paths, or alias/patch/sample/test references.",
    "Static analysis does not prove a publicly exported model is safe to remove.",
    "Review public exports, aliases, runtime consumers, inheritance/discriminators, TypeSpec, and regenerated API impact.",
    "Change TypeSpec and regenerate the SDK; never delete generated classes directly.",
    "",
    "Models with no path to a public operation:",
    *([f"- {name}" for name in models_without_operation_paths] if models_without_operation_paths else ["- None"]),
    "",
    "Trees",
    "-----",
    "",
]
for model_name in sorted(known_models):
    tree_lines.extend(render_tree(model_name))
    tree_lines.append("")

tree_output_path.parent.mkdir(parents=True, exist_ok=True)
tree_output_path.write_text("\n".join(tree_lines), encoding="utf-8", newline="\n")


def validate_reports(graph_path: Path, tree_path: Path) -> None:
    saved = json.loads(graph_path.read_text(encoding="utf-8"))
    saved_models = saved["models"]
    without_operations = sorted(
        name for name, entry in saved_models.items() if not entry["pathsToOperations"]
    )
    unreferenced = sorted(
        name
        for name, entry in saved_models.items()
        if not any(
            entry[field]
            for field in (
                "directModelReferrers", "baseModels", "derivedModels",
                "pathsToOperations", "otherReferences",
            )
        )
    )
    expected_metadata = {
        "modelCount": len(saved_models),
        "modelsWithOperationPaths": len(saved_models) - len(without_operations),
        "modelsWithoutOperationPaths": len(without_operations),
        "modelsWithoutOperationPathNames": without_operations,
        "unreferencedModelCount": len(unreferenced),
        "unreferencedModelNames": unreferenced,
    }
    for key, expected in expected_metadata.items():
        if saved["metadata"][key] != expected:
            raise ValueError(f"JSON metadata does not match the graph: {key}")

    lines = tree_path.read_text(encoding="utf-8").splitlines()
    for label, key in (
        ("Models", "modelCount"),
        ("Models with a path to a public operation", "modelsWithOperationPaths"),
        ("Models with no path to a public operation", "modelsWithoutOperationPaths"),
        ("Unreferenced models", "unreferencedModelCount"),
    ):
        if f"{label}: {expected_metadata[key]}" not in lines:
            raise ValueError(f"TXT summary does not match the graph: {label}")
    for heading, names in (
        ("Unreferenced models (excluding definitions and public exports):", unreferenced),
        ("Models with no path to a public operation:", without_operations),
    ):
        index = lines.index(heading) + 1
        listed_names = []
        while index < len(lines) and lines[index].startswith("- "):
            listed_names.append(lines[index][2:])
            index += 1
        if listed_names != (names or ["None"]):
            raise ValueError(f"TXT model list does not match the graph: {heading}")


validate_reports(output_path, tree_output_path)
print(f"Models: {len(known_models)}")
print(f"Models with operation paths: {models_with_operation_paths}")
print(f"Models without operation paths: {len(models_without_operation_paths)}")
print(f"Unreferenced models: {len(unreferenced_models)}")
for name in unreferenced_models or ["None"]:
    print(f"- {name}")
print("Explicit runtime operation owners:")
for name, operation in runtime_operation_owners.items():
    print(f"- {name}: {operation}")
print("Validation passed: JSON/TXT counts and model lists match; runtime owners exist.")
print("Static analysis is not proof of safe removal; review TypeSpec/runtime/API impact.")
print(f"Graph: {output_path}")
print(f"Trees: {tree_output_path}")
if requested_model:
    print(f"Model details: {requested_model}")
    print(json.dumps(graph[requested_model], indent=2))
'@

try {
    [System.IO.File]::WriteAllText($temporaryScript, $pythonScript, [System.Text.UTF8Encoding]::new($false))
    & $PythonExecutable $temporaryScript $packageRoot $ModelsPath $OutputPath $TreeOutputPath $ModelName | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Model reference graph generation failed with exit code $LASTEXITCODE."
    }
    [pscustomobject]@{
        GraphPath = (Resolve-Path -LiteralPath $OutputPath).Path
        TreePath = (Resolve-Path -LiteralPath $TreeOutputPath).Path
    }
}
finally {
    if (Test-Path -LiteralPath $temporaryScript) {
        Remove-Item -LiteralPath $temporaryScript -Force
    }
}