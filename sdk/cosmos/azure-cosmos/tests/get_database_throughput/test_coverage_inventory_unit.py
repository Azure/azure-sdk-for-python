# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep every original database-throughput contract in the copied Rust tests."""

import ast
from pathlib import Path
import re

from common._retired_test_sources import RETIRED_THROUGHPUT_SOURCES
from common._throughput_copy_inventory import database_test_files, database_test_targets


ROOT = Path(__file__).resolve().parents[2]


def test_original_database_contract_inventory_and_backend_pins_rust():
    references = set()
    for path in database_test_files("get"):
        text = path.read_text(encoding="utf-8")
        selected = database_test_targets(path, "get")
        if selected == [str(path)]:
            references.update(re.findall(r"# Source: (tests/\S+)", text))
        else:
            tree = ast.parse(text)
            for target in selected:
                _, class_name, method_name = target.split("::")
                cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
                method = next(node for node in cls.body if getattr(node, "name", None) == method_name)
                references.update(re.findall(r"# Source: (tests/\S+)", ast.get_source_segment(text, method)))
        pins = [
            node.value.value for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.keyword) and node.arg == "_backend"
            and isinstance(node.value, ast.Constant)
        ]
        assert pins == ["rust"], path

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
        filename, qualified = RETIRED_THROUGHPUT_SOURCES.get(reference, reference).split("::")
        class_name, method = qualified.split(".")
        tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        assert any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method for node in cls.body)


def test_baseline_paths_keep_neighboring_families_distinct_rust():
    files = database_test_files("get")
    targets = {(path.parent.parent.name, path.parent.name, path.name) for path in files}
    assert len(targets) == len(files)


def test_original_replacement_contract_inventory_and_assertions_rust():
    references = set()
    targets = []
    for path in database_test_files("replace"):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        pins = [
            node.value.value for node in ast.walk(tree)
            if isinstance(node, ast.keyword) and node.arg == "_backend"
            and isinstance(node.value, ast.Constant)
        ]
        assert pins == ["rust"], path
        for target in database_test_targets(path, "replace"):
            targets.append(target)
            _, class_name, method_name = target.split("::")
            cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
            method = next(node for node in cls.body if getattr(node, "name", None) == method_name)
            reference, = re.findall(r"# Source: (tests/\S+)", ast.get_source_segment(text, method))
            references.add(reference)
            filename, qualified = RETIRED_THROUGHPUT_SOURCES.get(reference, reference).split("::")
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

