# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retire only duplicate originals; retain all owned query regression cases."""

import ast
from collections import Counter
from pathlib import Path

import pytest

from common import test_legacy_migration_enforcer_unit as enforcer
from common._retired_test_sources import RETIRED_QUERY_SOURCES, RETIRED_TEST_SOURCES


ROOT = Path(__file__).resolve().parents[2]
QUERY_TESTS = ROOT / "tests" / "query_items"


def test_query_retirement_matches_all_33_retired_sources_rust():
    references = []
    for path in QUERY_TESTS.glob("*/legacy/test_*.py"):
        text = path.read_text(encoding="utf-8")
        for _, method in enforcer._iter_test_functions(ast.parse(text)):
            reference = enforcer._source_ref(method, text.splitlines())
            if reference in RETIRED_QUERY_SOURCES:
                references.append(reference)
    assert len(references) == len(set(references)) == len(RETIRED_QUERY_SOURCES) == 33
    assert set(references) == set(RETIRED_QUERY_SOURCES)
    assert len(set(RETIRED_QUERY_SOURCES.values())) == 33
    assert Counter(ref.split("::")[0] for ref in references) == {
        "tests/test_query.py": 12,
        "tests/test_query_async.py": 10,
        "tests/test_none_options.py": 1,
        "tests/test_none_options_async.py": 1,
        "tests/test_orderby.py": 1,
        "tests/test_query_feed_range.py": 3,
        "tests/test_query_feed_range_async.py": 3,
        "tests/test_query_feed_range_multipartition.py": 1,
        "tests/test_query_feed_range_multipartition_async.py": 1,
    }
    assert all(RETIRED_TEST_SOURCES[ref] == target for ref, target in RETIRED_QUERY_SOURCES.items())


@pytest.mark.parametrize("reference,replacement", RETIRED_QUERY_SOURCES.items())
def test_only_original_method_is_removed_and_exact_copy_remains_rust(reference, replacement):
    original_file, qualified = reference.split("::")
    original = ROOT / original_file
    assert original.is_file()
    original_tree = ast.parse(original.read_text(encoding="utf-8"))
    assert not enforcer._class_method_exists(original_tree, *qualified.rsplit(".", 1))
    assert list(enforcer._iter_test_functions(original_tree))

    filename, copied_qualified = replacement.split("::")
    retained = ROOT / filename
    assert retained.is_relative_to(QUERY_TESTS)
    text = retained.read_text(encoding="utf-8")
    methods = {
        f"{cls}.{method.name}": method
        for cls, method in enforcer._iter_test_functions(ast.parse(text))
    }
    assert copied_qualified == qualified + "_rust"
    assert enforcer._source_ref(methods[copied_qualified], text.splitlines()) == reference
    assert text.count('_backend="rust"') >= 1
    copied_class = next(
        node for node in ast.parse(text).body
        if isinstance(node, ast.ClassDef) and node.name == copied_qualified.rsplit(".", 1)[0]
    )
    marker = "cosmosQuery" if "feed_range_multipartition" in filename else "cosmosEmulator"
    assert any(ast.unparse(decorator) == f"pytest.mark.{marker}" for decorator in copied_class.decorator_list)


@pytest.mark.parametrize("surface,suffix", [("sync", ""), ("aio", "_async")])
def test_retained_cross_partition_replay_does_not_add_enable_flag_rust(surface, suffix):
    path = QUERY_TESTS / surface / "legacy" / f"test_query{suffix}.py"
    method = next(
        node for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == f"test_cross_partition_query_with_continuation_token{suffix}_rust"
    )
    assert not any(
        isinstance(node, ast.keyword) and node.arg == "enable_cross_partition_query"
        for node in ast.walk(method)
    )


@pytest.mark.parametrize("failure", [
    "unapproved-file", "unapproved-method", "missing-replacement", "missing-method", "wrong-class",
])
def test_query_retirement_does_not_hide_unknown_or_broken_sources_rust(monkeypatch, tmp_path, failure):
    reference, replacement = next(iter(RETIRED_QUERY_SOURCES.items()))
    if failure == "unapproved-file":
        reference = "tests/test_not_retired.py::TestOriginal.test_missing"
    elif failure == "unapproved-method":
        reference = "tests/test_query.py::TestQuery.test_not_approved"
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
])
def test_retained_query_copies_pass_migration_enforcement_rust(monkeypatch, check_name):
    monkeypatch.setattr(enforcer, "_TESTS_DIR", QUERY_TESTS)
    getattr(enforcer.LegacyMigrationEnforcerTests(check_name), check_name)()
