# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Only approved duplicate token tests retire; grouped split coverage stays."""

import ast
from pathlib import Path

import pytest

from common import test_legacy_migration_enforcer_unit as enforcer
from common._retired_test_sources import (
    RETIRED_SESSION_TOKEN_SOURCES,
    RETIRED_SESSION_TOKEN_SUPPORT_SOURCES,
    RETIRED_TEST_SOURCES,
    RETIRED_THROUGHPUT_SOURCES,
)
from get_latest_session_token._fixtures import create_split_ranges


ROOT = Path(__file__).resolve().parents[2]
TOKEN_TESTS = ROOT / "tests" / "get_latest_session_token"


def test_only_approved_nine_methods_and_21_cases_retired_rust():
    approved = {
        "tests/test_session_token_helpers.py::TestSessionTokenHelpers": (
            "test_get_session_token_update",
            "test_many_session_tokens_update_same_range",
            "test_many_session_tokens_update",
            "test_simulated_splits_merges",
            "test_invalid_feed_range",
        ),
        "tests/test_partition_split_scenarios.py::TestPartitionSplitScenarios": (
            "test_latest_session_token_hpk", "test_latest_session_token_logical_hpk",
        ),
        "tests/test_partition_split_scenarios_async.py::TestPartitionSplitScenariosAsync": (
            "test_latest_session_token_hpk", "test_latest_session_token_logical_hpk",
        ),
    }
    assert set(RETIRED_SESSION_TOKEN_SOURCES) == {
        f"{source}.{method}" for source, methods in approved.items() for method in methods
    }
    assert len(RETIRED_SESSION_TOKEN_SOURCES) == 9
    assert len(set(RETIRED_SESSION_TOKEN_SOURCES.values())) == 9
    assert len(create_split_ranges()) == 13
    assert len(RETIRED_SESSION_TOKEN_SOURCES) - 1 + len(create_split_ranges()) == 21
    assert not set(RETIRED_SESSION_TOKEN_SOURCES).intersection(RETIRED_THROUGHPUT_SOURCES)
    assert RETIRED_TEST_SOURCES == {**RETIRED_THROUGHPUT_SOURCES, **RETIRED_SESSION_TOKEN_SOURCES}
    assert len(RETIRED_TEST_SOURCES) == 42
    assert not (ROOT / "tests" / "test_session_token_helpers.py").exists()


@pytest.mark.parametrize("reference,replacement", RETIRED_SESSION_TOKEN_SOURCES.items())
def test_retired_method_resolves_to_exact_retained_rust_test_rust(reference, replacement):
    original_file, qualified = reference.split("::")
    original = ROOT / original_file
    if original.exists():
        assert not enforcer._class_method_exists(
            ast.parse(original.read_text(encoding="utf-8")), *qualified.rsplit(".", 1)
        )
    filename, qualified = replacement.split("::")
    retained = ROOT / filename
    assert retained.is_relative_to(TOKEN_TESTS)
    assert "real_split" not in filename
    text = retained.read_text(encoding="utf-8")
    methods = {
        f"{cls}.{method.name}": method
        for cls, method in enforcer._iter_test_functions(ast.parse(text))
    }
    method = methods[qualified]
    assert enforcer._source_ref(method, text.splitlines()) == reference
    assert text.count('_backend="rust"') == 1
    assert any(
        isinstance(node, ast.Assert) or (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "raises"
        )
        for node in ast.walk(method)
    )


@pytest.mark.parametrize("asynchronous", [False, True])
def test_original_grouped_split_and_required_write_helpers_remain_rust(asynchronous):
    suffix = "_async" if asynchronous else ""
    path = ROOT / "tests" / f"test_partition_split_scenarios{suffix}.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    cls = "TestPartitionSplitScenariosAsync" if asynchronous else "TestPartitionSplitScenarios"
    assert [(name, method.name) for name, method in enforcer._iter_test_functions(tree)] == [
        (cls, f"test_change_feed_session_token_and_read_items_after_split{suffix}")
    ]
    for helper in ("create_items_logical_pk", "create_items_physical_pk"):
        assert enforcer._class_method_exists(tree, cls, helper + suffix)
    assert enforcer._class_method_exists(tree, cls, "asyncSetUp" if asynchronous else "setUpClass")


def test_retired_split_data_has_owned_provenance_not_an_extra_test_rust():
    assert RETIRED_SESSION_TOKEN_SUPPORT_SOURCES == {
        "tests/test_session_token_helpers.py::create_split_ranges": (
            "tests/get_latest_session_token/_fixtures.py::create_split_ranges"
        ),
    }
    reference, replacement = next(iter(RETIRED_SESSION_TOKEN_SUPPORT_SOURCES.items()))
    assert reference not in RETIRED_TEST_SOURCES
    filename, name = replacement.split("::")
    text = (ROOT / filename).read_text(encoding="utf-8")
    method = next(node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name == name)
    assert enforcer._source_ref(method, text.splitlines()) == reference


@pytest.mark.parametrize("failure", [
    "unapproved-file", "unapproved-method", "missing-replacement", "missing-method", "wrong-class",
])
def test_token_retirement_does_not_hide_unknown_or_broken_sources_rust(monkeypatch, tmp_path, failure):
    reference, replacement = next(iter(RETIRED_SESSION_TOKEN_SOURCES.items()))
    if failure == "unapproved-file":
        reference = "tests/test_not_retired.py::TestOriginal.test_missing"
    elif failure == "unapproved-method":
        reference = "tests/test_session_token_helpers.py::TestSessionTokenHelpers.test_not_approved"
    elif failure in ("missing-method", "wrong-class"):
        filename, qualified = replacement.split("::")
        path = tmp_path / filename
        path.parent.mkdir(parents=True)
        cls, method = qualified.rsplit(".", 1)
        if failure == "missing-method":
            method = "test_not_the_replacement"
        else:
            cls = "TestWrongClass"
        path.write_text(f"class {cls}:\n    def {method}(self):\n        assert True\n", encoding="utf-8")
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
    check = enforcer.LegacyMigrationEnforcerTests("test_every_source_reference_resolves_rust")
    with pytest.raises(AssertionError, match="lineage no longer resolves"):
        check.test_every_source_reference_resolves_rust()


@pytest.mark.parametrize("check_name", [
    "test_legacy_folders_discovered_rust",
    "test_every_legacy_folder_is_a_package_rust",
    "test_every_test_method_has_a_source_comment_rust",
    "test_every_source_reference_resolves_rust",
    "test_every_legacy_file_pins_rust_backend_rust",
    "test_no_unstructured_skips_rust",
    "test_every_legacy_test_is_selected_by_emulator_marker_rust",
])
def test_retained_token_copies_pass_migration_enforcement_rust(monkeypatch, check_name):
    monkeypatch.setattr(enforcer, "_TESTS_DIR", TOKEN_TESTS)
    getattr(enforcer.LegacyMigrationEnforcerTests(check_name), check_name)()
