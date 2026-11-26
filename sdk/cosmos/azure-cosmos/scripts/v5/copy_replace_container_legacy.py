# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Append missing replacement tests from main without overwriting existing copies."""

import argparse
import ast
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PREFIX = "sdk/cosmos/azure-cosmos/tests/"
DATA_FIELDS = {"supported_languages", "language_abstracts", "search_terms"}


def main_sources():
    """Read the fetched main branch, never the checkout's legacy implementation."""
    result = subprocess.run(
        ["git", "grep", "--full-name", "-l", "-F", "replace_container(", "origin/main", "--",
         ":(top)" + SOURCE_PREFIX + "*.py"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError("Fetch origin/main before checking replacement test migration: " + result.stderr)
    if not result.stdout:
        raise AssertionError("No replacement sources found on origin/main")
    return {
        ref.split(":" + SOURCE_PREFIX, 1)[1]: subprocess.check_output(
            ["git", "show", ref], cwd=ROOT, text=True, encoding="utf-8-sig",
        )
        for ref in result.stdout.splitlines()
    }


def replacement_cases(source):
    """Include skipped methods: their original markers must survive migration."""
    for cls in ast.parse(source).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for method in cls.body:
            if (
                isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                and method.name.startswith("test_")
                and any(
                    isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "replace_container" for call in ast.walk(method)
                )
            ):
                yield cls, method


def destination(filename):
    surface = "aio" if filename.endswith("_async.py") else "sync"
    return ROOT / "tests" / "replace_container" / surface / filename.replace("_async.py", ".py")


def generated_files():
    for filename, source in main_sources().items():
        cases = list(replacement_cases(source))
        if not cases:
            continue
        path = destination(filename)
        if not path.exists():
            raise AssertionError(f"Add an API-scoped migration for {filename} before generating copies")
        existing = path.read_text(encoding="utf-8")
        tree = ast.parse(existing)
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        names = {node.name for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        lines = source.splitlines()
        additions = []
        if "full_text_policy" in filename:
            fields = {
                target.id for node in cls.body if isinstance(node, ast.Assign)
                for target in node.targets if isinstance(target, ast.Name)
            }
            for node in cases[0][0].body:
                if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id in DATA_FIELDS - fields
                    for target in node.targets
                ):
                    additions.append("\n".join(lines[node.lineno - 1:node.end_lineno]))
            if "import re\n" not in existing:
                existing = existing.replace("import uuid\n", "import re\nimport uuid\n", 1)
        for original_class, method in cases:
            if method.name + "_rust" in names:
                continue
            start = min([method.lineno] + [decorator.lineno for decorator in method.decorator_list])
            copied = lines[start - 1:method.end_lineno]
            def_index = method.lineno - start
            copied[def_index] = copied[def_index].replace(
                "def " + method.name + "(", "def " + method.name + "_rust(", 1,
            )
            copied.insert(def_index + 1, f"        # Source: tests/{filename}::{original_class.name}.{method.name}")
            additions.append("\n".join(copied))
        text = existing.rstrip() + ("\n\n" + "\n\n".join(additions) if additions else "") + "\n"
        text = text.replace(
            "    @pytest.mark.skip\n",
            '    @pytest.mark.skip(reason="environment-gap: the original main test is skipped; retain its disabled status.")\n',
        )
        yield path, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in generated_files():
        ast.parse(text)
        if args.check:
            if path.read_text(encoding="utf-8") != text:
                raise AssertionError(f"Missing main test copies or fixture data: {path}")
        else:
            path.write_text(text, encoding="utf-8")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
