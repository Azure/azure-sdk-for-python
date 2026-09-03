# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param(
    [string]$PythonExecutable = "python",
    [string]$OutputPath = (Join-Path $PSScriptRoot "docs\public-methods.md")
)

$ErrorActionPreference = "Stop"
$packageRoot = $PSScriptRoot
$temporaryScript = Join-Path ([System.IO.Path]::GetTempPath()) ("generate-public-methods-{0}.py" -f [guid]::NewGuid())

$pythonScript = @'
from __future__ import annotations

import inspect
import os
from pathlib import Path
import sys
from typing import Any


package_root = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package_root))
os.chdir(package_root)

from azure.core.credentials import AccessToken
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
import azure.ai.projects as projects_package


class FakeCredential:
    def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 2**31)


class AsyncFakeCredential:
    async def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 2**31)


def assert_local_import() -> None:
    imported_path = Path(projects_package.__file__).resolve()
    if not imported_path.is_relative_to(package_root):
        raise RuntimeError(
            f"Expected azure.ai.projects from {package_root}, but imported {imported_path}"
        )


def unwrap_operation(value: Any) -> Any:
    return getattr(value, "_operation", value)


def operation_instances(container: Any, *, exclude: set[str] | None = None) -> dict[str, Any]:
    excluded = exclude or set()
    operations: dict[str, Any] = {}
    for name, value in vars(container).items():
        if name.startswith("_") or name in excluded:
            continue
        operation = unwrap_operation(value)
        if type(operation).__name__.endswith("Operations"):
            operations[name] = operation
    return operations


def is_handwritten_method(cls: type[Any], name: str) -> bool:
    owner = next((base for base in cls.__mro__ if name in vars(base)), None)
    if owner is None:
        raise RuntimeError(f"Unable to find the class that defines {cls.__name__}.{name}")
    source_path = inspect.getsourcefile(owner)
    return source_path is not None and "_patch" in Path(source_path).name


def public_methods(instance: Any) -> dict[str, bool]:
    methods: dict[str, bool] = {}
    for name, member in inspect.getmembers(type(instance), predicate=callable):
        if name.startswith("_"):
            continue
        methods[name] = is_handwritten_method(type(instance), name)
    return methods


def client_methods(client: Any) -> dict[str, bool]:
    included_dunders = {"__enter__", "__exit__"}
    methods: dict[str, bool] = {}
    for name, member in inspect.getmembers(type(client), predicate=callable):
        if name.startswith("_") and name not in included_dunders:
            continue
        methods[name] = is_handwritten_method(type(client), name)
    return methods


def method_label(prefix: str, name: str, handwritten: bool) -> str:
    return f".{prefix}{name}{'*' if handwritten else ''}"


def validate_async_parity(
    sync_operations: dict[str, Any],
    async_operations: dict[str, Any],
    group_name: str,
) -> None:
    if sync_operations.keys() != async_operations.keys():
        sync_only = sorted(sync_operations.keys() - async_operations.keys())
        async_only = sorted(async_operations.keys() - sync_operations.keys())
        raise RuntimeError(
            f"{group_name} sub-client mismatch; sync-only={sync_only}, async-only={async_only}"
        )

    for name in sorted(sync_operations):
        sync_methods = set(public_methods(sync_operations[name]))
        async_methods = set(public_methods(async_operations[name]))
        if sync_methods != async_methods:
            raise RuntimeError(
                f"{group_name}.{name} method mismatch; "
                f"sync-only={sorted(sync_methods - async_methods)}, "
                f"async-only={sorted(async_methods - sync_methods)}"
            )


def table(lines: list[str], rows: list[tuple[str, str, int]]) -> None:
    lines.extend(
        [
            "| Subclient | Class Name | Methods Count |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(f"| `{name}` | {class_name} | {count} |" for name, class_name, count in rows)


assert_local_import()
endpoint = "https://example.services.ai.azure.com/api/projects/example"
sync_client = AIProjectClient(endpoint=endpoint, credential=FakeCredential(), allow_preview=True)
async_client = AsyncAIProjectClient(endpoint=endpoint, credential=AsyncFakeCredential(), allow_preview=True)

try:
    sync_stable = operation_instances(sync_client, exclude={"beta"})
    async_stable = operation_instances(async_client, exclude={"beta"})
    sync_beta = operation_instances(sync_client.beta)
    async_beta = operation_instances(async_client.beta)

    validate_async_parity(sync_stable, async_stable, "stable")
    validate_async_parity(sync_beta, async_beta, "beta")

    stable_methods = {name: public_methods(instance) for name, instance in sync_stable.items()}
    beta_methods = {name: public_methods(instance) for name, instance in sync_beta.items()}
    direct_methods = client_methods(sync_client)

    stable_count = sum(len(methods) for methods in stable_methods.values())
    beta_count = sum(len(methods) for methods in beta_methods.values())
    total_count = len(direct_methods) + stable_count + beta_count

    lines = [
        "# Public AIProjectClient methods",
        "",
        "<!-- Generated by GeneratePublicMethods.ps1. Do not edit manually. -->",
        "",
        "This document lists all public methods available on `AIProjectClient` and its sub-clients. "
        "Overload methods are not counted. Only synchronous methods are counted (but each one has an "
        "equivalent asynchronous method).",
        "",
        "## Summary",
        "",
        f"There are a total of {total_count} unique public methods:",
        "",
        f"- {len(direct_methods)} stable methods on the client",
        f"- {stable_count} stable methods on top-level sub-clients",
        f"- {beta_count} beta methods on nested beta sub-clients",
        "",
        "### Top-level sub-clients (stable operations)",
        "",
    ]

    stable_rows = [
        (name, type(sync_stable[name]).__name__, len(stable_methods[name]))
        for name in sorted(sync_stable)
    ]
    table(lines, stable_rows)
    lines.extend(["", "### Nested sub-clients (beta operations)", ""])
    beta_rows = [
        (f"beta.{name}", type(sync_beta[name]).__name__, len(beta_methods[name]))
        for name in sorted(sync_beta)
    ]
    table(lines, beta_rows)

    lines.extend(
        [
            "",
            "## Stable methods on the client",
            "",
            "Alphabetically sorted. An asterisk at the end of the method name means it is a hand-written method.",
            "",
            "```text",
        ]
    )
    lines.extend(method_label("", name, direct_methods[name]) for name in sorted(direct_methods))
    lines.extend(
        [
            "```",
            "",
            "## Stable methods on top-level sub clients",
            "",
            "Alphabetically sorted. An asterisk at the end of the method name means it is a hand-written method.",
            "",
            "```text",
        ]
    )
    for index, subclient_name in enumerate(sorted(stable_methods)):
        if index:
            lines.append("")
        methods = stable_methods[subclient_name]
        lines.extend(
            method_label(f"{subclient_name}.", name, methods[name]) for name in sorted(methods)
        )
    lines.extend(
        [
            "```",
            "",
            "## Beta methods on nested sub-clients",
            "",
            "Alphabetically sorted. An asterisk at the end of the method name means it is a hand-written method.",
            "",
            "```text",
        ]
    )
    for index, subclient_name in enumerate(sorted(beta_methods)):
        if index:
            lines.append("")
        methods = beta_methods[subclient_name]
        lines.extend(
            method_label(f"beta.{subclient_name}.", name, methods[name]) for name in sorted(methods)
        )
    lines.extend(["```", ""])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        f"Generated {output_path} with {total_count} methods "
        f"({len(direct_methods)} client, {stable_count} stable, {beta_count} beta)."
    )
finally:
    sync_client.close()
'@

try {
    [System.IO.File]::WriteAllText($temporaryScript, $pythonScript, [System.Text.UTF8Encoding]::new($false))
    & $PythonExecutable $temporaryScript $packageRoot $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Public method generation failed with exit code $LASTEXITCODE."
    }
}
finally {
    Remove-Item $temporaryScript -Force -ErrorAction SilentlyContinue
}