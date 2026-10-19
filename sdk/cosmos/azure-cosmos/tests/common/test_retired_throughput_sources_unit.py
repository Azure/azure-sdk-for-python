# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retired originals must retain explicit, executable Rust replacements."""

import ast
from pathlib import Path

import pytest

from common import test_legacy_migration_enforcer_unit as enforcer
from common._retired_test_sources import RETIRED_THROUGHPUT_SOURCES


ROOT = Path(__file__).resolve().parents[2]


def _method(tree, qualified):
    class_name, method_name = qualified.split(".")
    return next(
        method for cls in tree.body if isinstance(cls, ast.ClassDef) and cls.name == class_name
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name == method_name
    )


def test_retirements_are_scoped_to_verified_throughput_cases():
    assert len(RETIRED_THROUGHPUT_SOURCES) == 33
    assert len(set(RETIRED_THROUGHPUT_SOURCES.values())) == 33
    for reference, replacement in RETIRED_THROUGHPUT_SOURCES.items():
        assert replacement not in RETIRED_THROUGHPUT_SOURCES
        assert Path(reference.split("::")[0]).parent == Path("tests")
        assert replacement.split("/")[1] in {
            "get_database_throughput", "replace_database_throughput",
            "get_container_throughput", "replace_throughput",
        }


@pytest.mark.parametrize("reference,replacement", RETIRED_THROUGHPUT_SOURCES.items())
def test_each_retired_original_has_a_retained_rust_contract(reference, replacement):
    original_file, original_name = reference.split("::")
    original_path = ROOT / original_file
    if original_path.exists():
        with pytest.raises(StopIteration):
            _method(ast.parse(original_path.read_text(encoding="utf-8")), original_name)

    filename, qualified = replacement.split("::")
    text = (ROOT / filename).read_text(encoding="utf-8")
    tree = ast.parse(text)
    method = _method(tree, qualified)
    class_name, _ = qualified.split(".")
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    assert f"# Source: {reference}" in {
        line.strip() for line in ast.get_source_segment(text, method).splitlines()
    }
    pins = [
        node.value.value for node in ast.walk(tree)
        if isinstance(node, ast.keyword) and node.arg == "_backend" and isinstance(node.value, ast.Constant)
    ]
    assert pins == ["rust"]
    helper_names = {
        node.func.attr for node in ast.walk(method)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"
    }
    bodies = [method] + [
        helper for helper in cls.body
        if isinstance(helper, (ast.FunctionDef, ast.AsyncFunctionDef)) and helper.name in helper_names
    ]
    assert any(
        isinstance(node, ast.Assert) or (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and (
                node.func.attr.startswith("assert") or (
                    node.func.attr == "raises" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pytest"
                )
            )
        )
        for body in bodies for node in ast.walk(body)
    )


@pytest.mark.parametrize("failure", ["unapproved-original", "missing-replacement", "missing-method"])
def test_lineage_enforcement_does_not_ignore_missing_tests(monkeypatch, tmp_path, failure):
    reference, replacement = next(iter(RETIRED_THROUGHPUT_SOURCES.items()))
    if failure == "unapproved-original":
        reference = "tests/test_not_retired.py::TestOriginal.test_missing"
    elif failure == "missing-method":
        filename, qualified = replacement.split("::")
        path = tmp_path / filename
        path.parent.mkdir(parents=True)
        class_name, _ = qualified.split(".")
        path.write_text(f"class {class_name}:\n    pass\n", encoding="utf-8")
    copied = tmp_path / "copied.py"
    copied.write_text(
        "class TestCopy:\n"
        "    def test_copied(self):\n"
        f"        # Source: {reference}\n"
        "        assert True\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(enforcer, "_PKG_ROOT", tmp_path)
    monkeypatch.setattr(enforcer, "_legacy_test_files", lambda: [copied])
    check = enforcer.LegacyMigrationEnforcerTests("test_every_source_reference_resolves")
    with pytest.raises(AssertionError, match="lineage no longer resolves"):
        check.test_every_source_reference_resolves()
