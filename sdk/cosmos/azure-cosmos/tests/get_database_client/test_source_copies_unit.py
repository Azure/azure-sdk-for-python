# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect the database-only copies without treating mixed originals as retired."""

import ast
from pathlib import Path

import pytest

from common import test_migration_enforcer_unit as enforcer
from common._retired_test_sources import RETIRED_TEST_SOURCES


ROOT = Path(__file__).resolve().parents[2]
FAMILY = Path(__file__).resolve().parent
CASES = [
    ("sync", "test_crud.py", "TestCRUDOperations", "test_get_resource_with_dictionary_and_object"),
    ("aio", "test_crud_async.py", "TestCRUDOperationsAsync",
     "test_get_resource_with_dictionary_and_object_async"),
    ("sync", "test_crud_response_payload_on_write_disabled.py",
     "TestCRUDOperationsResponsePayloadOnWriteDisabled", "test_get_resource_with_dictionary_and_object"),
    ("aio", "test_crud_response_payload_on_write_disabled_async.py",
     "TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled",
     "test_get_resource_with_dictionary_and_object_async"),
]


def _method(path, class_name, method_name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    return next(node for node in cls.body if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef)
    ) and node.name == method_name)


@pytest.mark.parametrize("surface,filename,class_name,method_name", CASES)
def test_original_database_statements_are_preserved_rust(surface, filename, class_name, method_name):
    source = ROOT / "tests" / filename
    copy = FAMILY / surface / filename
    original = _method(source, class_name, method_name)
    copied = _method(copy, class_name, method_name + "_rust")
    assert len(copied.body) == 7
    assert ast.dump(copied.body[0]) == ast.dump(original.body[0])
    assertion = (
        "self.assertEqual(read_db.id, created_db.id)"
        if surface == "sync" else "assert read_db.id == created_db.id"
    )
    properties = "created_db.read()" if surface == "sync" else "await created_db.read()"
    for index, argument in enumerate(("created_db.id", "created_db", properties)):
        expected = ast.parse(f"read_db = self.client.get_database_client({argument})\n{assertion}")
        assert [ast.dump(node) for node in copied.body[1 + index * 2:3 + index * 2]] == [
            ast.dump(node) for node in expected.body
        ]
    remaining_calls = [
        node.func.attr for node in ast.walk(original)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    assert "get_database_client" not in remaining_calls
    assert "get_container_client" in remaining_calls
    assert "read_item" in remaining_calls
    assert type(copied) is type(original)
    assert copied.decorator_list == []
    reference = f"tests/{filename}::{class_name}.{method_name}"
    assert f"# Source: {reference}" in copy.read_text(encoding="utf-8")
    assert reference not in RETIRED_TEST_SOURCES
    assert "Retire this mixed method only after" in source.read_text(encoding="utf-8")

    setup_name = "setUp" if surface == "sync" else "asyncSetUp"
    setup = _method(copy, class_name, setup_name)
    constructors = [
        node for node in ast.walk(setup) if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("create_data_client", "create_data_client_async")
    ]
    assert len(constructors) == 1
    options = {keyword.arg: ast.literal_eval(keyword.value) for keyword in constructors[0].keywords}
    assert options == (
        {"_backend": "rust", "no_response_on_write": True}
        if "payload" in filename else {"_backend": "rust"}
    )


@pytest.mark.parametrize("check_name", [
    "test_migrated_folders_discovered_rust",
    "test_every_migrated_folder_is_a_package_rust",
    "test_every_test_method_has_a_source_comment_rust",
    "test_every_source_reference_resolves_rust",
    "test_every_migrated_file_pins_rust_backend_rust",
    "test_no_unstructured_skips_rust",
    "test_every_copy_keeps_original_lane_markers_rust",
    "test_every_migrated_test_collects_without_conftest_rust",
])
def test_getter_copies_pass_migration_enforcement_rust(monkeypatch, check_name):
    monkeypatch.setattr(enforcer, "_TESTS_DIR", FAMILY)
    getattr(enforcer.LegacyMigrationEnforcerTests(check_name), check_name)()
