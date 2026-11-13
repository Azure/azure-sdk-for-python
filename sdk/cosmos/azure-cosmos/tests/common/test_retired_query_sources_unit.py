# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retire only duplicate originals; retain all owned query regression cases."""

import ast
from collections import Counter
from pathlib import Path

import pytest

from common import test_migration_enforcer_unit as enforcer
from common._retired_test_sources import (
    RETIRED_QUERY_SOURCE_MARKERS,
    RETIRED_QUERY_SOURCES,
    RETIRED_TEST_SOURCES,
)


ROOT = Path(__file__).resolve().parents[2]
QUERY_TESTS = ROOT / "tests" / "query_items"


def test_query_retirement_matches_all_33_retired_sources_rust():
    references = []
    for path in QUERY_TESTS.glob("*/test_*.py"):
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
    assert RETIRED_QUERY_SOURCE_MARKERS.keys() == RETIRED_QUERY_SOURCES.keys()


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
    methods = {f"{cls}.{method.name}": method for cls, method in enforcer._iter_test_functions(ast.parse(text))}
    assert copied_qualified == qualified + "_rust"
    assert enforcer._source_ref(methods[copied_qualified], text.splitlines()) == reference
    assert text.count('_backend="rust"') >= 1
    copied_class = next(
        node
        for node in ast.parse(text).body
        if isinstance(node, ast.ClassDef) and node.name == copied_qualified.rsplit(".", 1)[0]
    )
    expected = RETIRED_QUERY_SOURCE_MARKERS[reference]
    assert enforcer._lane_markers_from(copied_class.decorator_list) == expected
    assert not enforcer._lane_markers_from(methods[copied_qualified].decorator_list)
    assert (
        enforcer._effective_lane_markers(ast.parse(text), copied_class.name, methods[copied_qualified].name) == expected
    )


@pytest.mark.parametrize(
    "markers",
    [
        (),
        ("cosmosEmulator",),
        ("cosmosQuery", "cosmosAADQuery"),
        ("cosmosCircuitBreaker", "cosmosQuery", "cosmosAADQuery", "cosmosEmulator"),
    ],
)
def test_retired_query_markers_cannot_validate_against_the_replacement_rust(monkeypatch, tmp_path, markers):
    reference = "tests/test_query.py::TestQuery.test_query_items_with_parameters_none"
    filename, qualified = RETIRED_QUERY_SOURCES[reference].split("::")
    class_name, method_name = qualified.rsplit(".", 1)
    replacement = tmp_path / filename
    replacement.parent.mkdir(parents=True)
    replacement.write_text(
        "import pytest\n"
        + "".join(f"@pytest.mark.{marker}\n" for marker in markers)
        + f"class {class_name}:\n"
        + f"    def {method_name}(self):\n"
        + f"        # Source: {reference}\n"
        + "        pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(enforcer, "_PKG_ROOT", tmp_path)
    monkeypatch.setattr(enforcer, "_legacy_test_files", lambda: [replacement])
    check = enforcer.LegacyMigrationEnforcerTests("test_every_copy_keeps_original_lane_markers_rust")
    with pytest.raises(AssertionError, match="lane markers differ"):
        check.test_every_copy_keeps_original_lane_markers_rust()


@pytest.mark.parametrize(
    "filename,class_name,method_name,markers",
    [
        (
            "sync/test_query.py",
            "TestQueryRegressions",
            "test_continuation_token_limit_preserves_broad_scope_and_resume_rust",
            {"cosmosEmulator"},
        ),
        (
            "sync/test_query.py",
            "TestQueryRegressions",
            "test_cross_partition_disabled_without_partition_key_matches_core_python_rust",
            {"cosmosEmulator"},
        ),
        (
            "aio/test_query_async.py",
            "TestQueryRegressionsAsync",
            "test_continuation_token_limit_preserves_broad_scope_and_resume_async_rust",
            {"cosmosEmulator"},
        ),
        (
            "aio/test_query_async.py",
            "TestQueryRegressionsAsync",
            "test_cross_partition_disabled_without_partition_key_matches_core_python_async_rust",
            {"cosmosEmulator"},
        ),
        (
            "aio/test_query_feed_range_multipartition_async.py",
            "TestFeedRangeMultiPartitionRegressionsAsync",
            "test_prefix_partition_key_query_cross_partition_disabled_async_rust",
            {"cosmosQuery"},
        ),
    ],
)
def test_additional_query_regressions_keep_their_own_lanes_rust(filename, class_name, method_name, markers):
    text = (QUERY_TESTS / filename).read_text(encoding="utf-8")
    tree = ast.parse(text)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    method = next(
        node
        for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name
    )
    assert enforcer._source_ref(method, text.splitlines()).startswith("(new)")
    assert enforcer._lane_markers_from(cls.decorator_list) == markers
    assert not enforcer._lane_markers_from(method.decorator_list)
    assert enforcer._effective_lane_markers(tree, class_name, method_name) == markers


@pytest.mark.parametrize(
    "message,accepted",
    [
        ("Expected String, but got Number.", True),
        ("Expected Number, but got String.", True),
        ("Unexpected query error.", False),
        (None, False),
    ],
)
def test_retained_orderby_error_assertion_checks_both_core_python_messages_rust(monkeypatch, message, accepted):
    from query_items.sync import test_orderby

    case = test_orderby.TestCrossPartitionTopOrderBy("test_orderby_query_noncomparable_orderby_item_rust")
    case.document_definitions = []

    def execute_query(*_args):
        if message is not None:
            raise ValueError(message)

    monkeypatch.setattr(case, "execute_query_and_validate_results", execute_query)
    # Exercise only the assertion offline; the service test's Gap 30 skip stays in place.
    monkeypatch.setattr(test_orderby.pytest, "skip", lambda *_args, **_kwargs: None)
    if accepted:
        case.test_orderby_query_noncomparable_orderby_item_rust()
    else:
        with pytest.raises(AssertionError):
            case.test_orderby_query_noncomparable_orderby_item_rust()


@pytest.mark.parametrize("surface,suffix", [("sync", ""), ("aio", "_async")])
def test_retained_cross_partition_replay_does_not_add_enable_flag_rust(surface, suffix):
    path = QUERY_TESTS / surface / f"test_query{suffix}.py"
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


@pytest.mark.parametrize(
    "check_name",
    [
        "test_migrated_folders_discovered_rust",
        "test_every_migrated_folder_is_a_package_rust",
        "test_every_test_method_has_a_source_comment_rust",
        "test_every_source_reference_resolves_rust",
        "test_every_migrated_file_pins_rust_backend_rust",
        "test_no_unstructured_skips_rust",
        "test_every_copy_keeps_original_lane_markers_rust",
    ],
)
def test_retained_query_copies_pass_migration_enforcement_rust(monkeypatch, check_name):
    monkeypatch.setattr(enforcer, "_TESTS_DIR", QUERY_TESTS)
    getattr(enforcer.LegacyMigrationEnforcerTests(check_name), check_name)()
