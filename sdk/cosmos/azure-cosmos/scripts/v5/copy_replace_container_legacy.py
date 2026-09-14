# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the active v4 policy-replacement methods, preserving their bodies."""

import argparse
import ast
from pathlib import Path

from legacy_copy_generator import render_init_py


ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ("computed_properties", "full_text_policy", "vector_policy")
HELPERS = ("computedPropertiesTestCases", "_assert_query_count_eventually")


def generated_files():
    for surface in ("sync", "aio"):
        suffix = "_async" if surface == "aio" else ""
        base = "AsyncReplacementCase" if surface == "aio" else "SyncReplacementCase"
        for family in FAMILIES:
            source_path = ROOT / "tests" / f"test_{family}{suffix}.py"
            source = source_path.read_text(encoding="utf-8")
            lines = source.splitlines()
            tree = ast.parse(source)
            cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
            methods = [
                node for node in cls.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name.startswith("test_")
                and not node.decorator_list
                and any(
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "replace_container"
                    for call in ast.walk(node)
                )
            ]
            imports = ["import uuid", "import pytest", "from azure.cosmos import PartitionKey, exceptions"]
            if family == "computed_properties":
                imports.append("import asyncio" if surface == "aio" else "import time")
            imports.extend([
                f"from azure.cosmos{'.aio' if surface == 'aio' else ''} import CosmosClient",
                f"from replace_container._legacy_setup import {base}",
            ])
            chunks = [
                render_init_py().rstrip(),
                '"""Unchanged v4 policy-replacement methods with isolated Rust setup."""',
                "\n".join(imports),
                f"class {cls.name}({base}):\n"
                "    def _create_key_client(self):\n"
                "        return CosmosClient(self.host, self.key, _backend=\"rust\", read_timeout=30)",
            ]
            if family == "computed_properties":
                setup = next(node for node in cls.body if getattr(node, "name", "") ==
                             ("asyncSetUp" if surface == "aio" else "setUpClass"))
                assignments = [
                    node for node in setup.body if isinstance(node, ast.Assign)
                    and isinstance(node.targets[0], ast.Attribute)
                    and node.targets[0].attr in ("items", "computed_properties")
                ]
                assert len(assignments) == 2
                data = ["    def _initialize_data(self):"]
                for node in assignments:
                    data.extend(line.replace("cls.items", "self.items").replace(
                        "cls.computed_properties", "self.computed_properties")
                        for line in lines[node.lineno - 1:node.end_lineno])
                chunks.append("\n".join(data))
                for node in cls.body:
                    if getattr(node, "name", "") in HELPERS:
                        chunks.append("\n".join(lines[node.lineno - 1:node.end_lineno]))
            for method in methods:
                copied = lines[method.lineno - 1:method.end_lineno]
                copied.insert(1, f"        # Source: tests/{source_path.name}::{cls.name}.{method.name}")
                chunks.append("\n".join(copied))
            destination = ROOT / "tests" / "replace_container" / surface / "legacy" / f"test_{family}.py"
            yield destination, "\n\n".join(chunks) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in generated_files():
        ast.parse(text)
        if args.check:
            if path.read_text(encoding="utf-8") != text:
                raise AssertionError(f"Generated copy differs: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            init = path.parent / "__init__.py"
            if not init.exists():
                init.write_text(render_init_py(), encoding="utf-8")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
