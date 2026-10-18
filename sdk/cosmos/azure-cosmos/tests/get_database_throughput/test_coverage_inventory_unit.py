# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep every original database-throughput contract in the parity selection."""

import ast
import importlib.util
from pathlib import Path
import re
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _runner():
    spec = importlib.util.spec_from_file_location(
        "database_throughput_runner", ROOT / "scripts" / "v5" / "run_database_throughput_parity.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_original_database_contract_inventory_and_backend_pins():
    runner = _runner()
    references = set()
    for path in runner.test_files("get"):
        text = path.read_text(encoding="utf-8")
        selected = runner.test_targets(path, "get")
        if selected == [str(path)]:
            references.update(re.findall(r"# Source: (tests/\S+)", text))
        else:
            tree = ast.parse(text)
            for target in selected:
                _, class_name, method_name = target.split("::")
                cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
                method = next(node for node in cls.body if getattr(node, "name", None) == method_name)
                references.update(re.findall(r"# Source: (tests/\S+)", ast.get_source_segment(text, method)))
        for backend in ("rust", "core-python"):
            source = runner._source_for_backend(path, backend)
            tree = ast.parse(source)
            pins = [
                node.value.value for node in ast.walk(tree)
                if isinstance(node, ast.keyword) and node.arg == "_backend"
                and isinstance(node.value, ast.Constant)
            ]
            assert pins == [backend], path

    expected = {
        "tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_offer_methods",
    }
    for suffix, class_suffix, method_suffix in (("", "", ""), ("_async", "Async", "_async")):
        expected.update({
            f"tests/test_crud_database{suffix}.py::TestCRUDDatabaseOperations{class_suffix}.test_database_crud{method_suffix}",
            f"tests/test_crud_database{suffix}.py::TestCRUDDatabaseOperations{class_suffix}.test_database_level_offer_throughput{method_suffix}",
            f"tests/test_auto_scale{suffix}.py::TestAutoScale{class_suffix}.test_autoscale_create_database{method_suffix}",
            f"tests/test_cosmos_responses{suffix}.py::TestCosmosResponses{class_suffix}.test_database_replace_throughput{method_suffix}",
        })
        disabled_class = (
            "TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled"
            if suffix else "TestCRUDOperationsResponsePayloadOnWriteDisabled"
        )
        expected.update({
            f"tests/test_crud_response_payload_on_write_disabled{suffix}.py::{disabled_class}.test_database_crud{method_suffix}",
            f"tests/test_crud_response_payload_on_write_disabled{suffix}.py::{disabled_class}.test_database_level_offer_throughput{method_suffix}",
        })
    expected.update({
        "tests/test_auto_scale.py::TestAutoScale.test_autoscale_replace_throughput",
        "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_replace_throughput_async",
    })
    assert references == expected
    assert len(references) == 15
    for reference in references:
        filename, qualified = reference.split("::")
        class_name, method = qualified.split(".")
        tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        assert any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method for node in cls.body)


def test_baseline_paths_keep_neighboring_families_distinct():
    files = _runner().test_files("get")
    targets = {(path.parent.parent.parent.name, path.parent.parent.name, path.name) for path in files}
    assert len(targets) == len(files)


def test_original_replacement_contract_inventory_and_assertions():
    runner = _runner()
    references = set()
    targets = []
    for path in runner.test_files("replace"):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for backend in ("rust", "core-python"):
            pins = [
                node.value.value for node in ast.walk(ast.parse(runner._source_for_backend(path, backend)))
                if isinstance(node, ast.keyword) and node.arg == "_backend"
                and isinstance(node.value, ast.Constant)
            ]
            assert pins == [backend], path
        for target in runner.test_targets(path, "replace"):
            targets.append(target)
            _, class_name, method_name = target.split("::")
            cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
            method = next(node for node in cls.body if getattr(node, "name", None) == method_name)
            reference, = re.findall(r"# Source: (tests/\S+)", ast.get_source_segment(text, method))
            references.add(reference)
            filename, qualified = reference.split("::")
            original_class, original_method = qualified.split(".")
            original = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
            original_cls = next(node for node in original.body if isinstance(node, ast.ClassDef) and node.name == original_class)
            original_node = next(node for node in original_cls.body if getattr(node, "name", None) == original_method)
            def assertions(node):
                return {
                    ast.dump(item) for item in ast.walk(node)
                    if isinstance(item, ast.Assert) or (
                        isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute)
                        and item.func.attr.startswith("assert")
                    )
                }
            assert assertions(original_node) <= assertions(method), reference
    expected = {
        "tests/test_auto_scale.py::TestAutoScale.test_autoscale_replace_throughput",
        "tests/test_auto_scale_async.py::TestAutoScaleAsync.test_replace_throughput_async",
    }
    for suffix, class_suffix, method_suffix in (("", "", ""), ("_async", "Async", "_async")):
        disabled_class = (
            "TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled"
            if suffix else "TestCRUDOperationsResponsePayloadOnWriteDisabled"
        )
        expected.update({
            f"tests/test_crud_database{suffix}.py::TestCRUDDatabaseOperations{class_suffix}.test_database_level_offer_throughput{method_suffix}",
            f"tests/test_cosmos_responses{suffix}.py::TestCosmosResponses{class_suffix}.test_database_replace_throughput{method_suffix}",
            f"tests/test_crud_response_payload_on_write_disabled{suffix}.py::{disabled_class}.test_database_level_offer_throughput{method_suffix}",
        })
    assert references == expected
    assert len(targets) == len(set(targets)) == 8
    assert all("::test_database_crud" not in target for target in targets)


@pytest.mark.parametrize("backend", ["rust", "core-python"])
def test_runner_pins_source_and_selects_eight_replacements(monkeypatch, backend):
    runner = _runner()
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(sys, "argv", ["runner", "--operation", "replace", "--backend", backend])
    monkeypatch.setenv("COSMOS_BACKEND", "rust")
    monkeypatch.setenv("COSMOS_PARITY_CAPTURE_OP", "")
    invocations = []
    monkeypatch.setattr(runner.pytest, "main", lambda args: invocations.append(args) or 0)
    assert runner.main() == 0
    assert sys.path[:2] == [str(ROOT), str(ROOT / "tests")]
    targets = [argument for argument in invocations[0] if "::" in argument]
    assert len(targets) == len(set(targets)) == 8
