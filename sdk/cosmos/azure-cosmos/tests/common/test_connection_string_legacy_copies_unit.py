# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep all five approved factory retirements mapped to enabled Rust copies."""

import ast
from pathlib import Path

import pytest

from common import test_legacy_migration_enforcer_unit as enforcer
from common._retired_test_sources import RETIRED_CONNECTION_STRING_SOURCES, RETIRED_TEST_SOURCES

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ("sync", "test_utils.py", "TestsUtils", "test_connection_string"),
    ("sync", "test_item_body_serialization.py", "TestClientOptionWiring",
     "test_sync_connection_string_forwards_option"),
    ("aio", "test_item_body_serialization.py", "TestClientOptionWiring",
     "test_async_connection_string_forwards_option"),
    ("sync", "test_user_agent_overwrite_regression.py", "TestUserAgentOverwriteRegression",
     "test_overwrite_via_from_connection_string"),
    ("aio", "test_user_agent_overwrite_regression_async.py", "TestUserAgentOverwriteRegressionAsync",
     "test_overwrite_via_from_connection_string_async"),
]


def _classes(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def _method(cls, name):
    return next(
        node for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    )


@pytest.mark.parametrize("surface,original_file,class_name,method_name", CASES)
def test_factory_copy_replaces_only_approved_original_rust(surface, original_file, class_name, method_name):
    original = _classes(ROOT / "tests" / original_file)
    copied_path = ROOT / "tests" / "from_connection_string" / surface / "legacy" / "test_from_connection_string.py"
    copied = _classes(copied_path)
    assert all(node.name != method_name for node in original[class_name].body if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef)
    ))
    assert any(node.name.startswith("test_") for node in original[class_name].body if isinstance(
        node, (ast.FunctionDef, ast.AsyncFunctionDef)
    ))
    actual = _method(copied[class_name], method_name + "_rust")
    source = f"tests/{original_file}::{class_name}.{method_name}"
    assert f"# Source: {source}" in copied_path.read_text(encoding="utf-8")
    replacement = f"{copied_path.relative_to(ROOT).as_posix()}::{class_name}.{method_name}_rust"
    assert RETIRED_CONNECTION_STRING_SOURCES[source] == RETIRED_TEST_SOURCES[source] == replacement
    assert actual.decorator_list == []

    backend_pins = []
    for node in ast.walk(actual):
        if isinstance(node, ast.Call):
            backend_pins.extend(keyword for keyword in node.keywords if keyword.arg == "_backend")
    assert len(backend_pins) == 1
    assert isinstance(backend_pins[0].value, ast.Constant)
    assert backend_pins[0].value.value == "rust"

    if method_name == "test_connection_string":
        cleanup = [
            node for node in actual.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "addCleanup"
        ]
        assert len(cleanup) == 2
    assertions = [
        node for node in ast.walk(actual) if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert")
    ]
    if method_name == "test_connection_string":
        expected_assertion = "self.assertTrue(db is not None)"
    elif "forwards_option" in method_name:
        expected_assertion = "self.assertTrue(init.call_args.kwargs['enable_compact_utf8_item_writes'])"
    else:
        expected_assertion = None
    if expected_assertion is not None:
        assert [ast.dump(node) for node in assertions] == [
            ast.dump(ast.parse(expected_assertion, mode="eval").body)
        ]

    if "user_agent_overwrite" in original_file:
        for helper in ("_smoke_data_plane_call", "_assert_user_agent_headers", "setUpClass"):
            assert ast.dump(_method(copied[class_name], helper)) == ast.dump(
                _method(original[class_name], helper)
            )
        transport = "_AsyncUserAgentCaptureTransport" if surface == "aio" else "_UserAgentCaptureTransport"
        assert ast.dump(copied[transport]) == ast.dump(original[transport])


def test_exactly_five_factory_sources_are_retired_rust():
    assert set(RETIRED_CONNECTION_STRING_SOURCES) == {
        f"tests/{filename}::{cls}.{method}" for _, filename, cls, method in CASES
    }
    assert len(RETIRED_CONNECTION_STRING_SOURCES) == len(set(RETIRED_CONNECTION_STRING_SOURCES.values())) == 5
    retained = []
    for path in (ROOT / "tests" / "from_connection_string").glob("*/legacy/test_*.py"):
        retained.extend(enforcer._iter_test_functions(ast.parse(path.read_text(encoding="utf-8"))))
    assert len(retained) == 5


@pytest.mark.parametrize("check_name", [
    "test_legacy_folders_discovered_rust",
    "test_every_legacy_folder_is_a_package_rust",
    "test_every_test_method_has_a_source_comment_rust",
    "test_every_source_reference_resolves_rust",
    "test_every_legacy_file_pins_rust_backend_rust",
    "test_no_unstructured_skips_rust",
    "test_every_legacy_test_is_selected_by_emulator_marker_rust",
])
def test_retained_factory_copies_pass_migration_enforcement_rust(monkeypatch, check_name):
    monkeypatch.setattr(enforcer, "_TESTS_DIR", ROOT / "tests" / "from_connection_string")
    getattr(enforcer.LegacyMigrationEnforcerTests(check_name), check_name)()
