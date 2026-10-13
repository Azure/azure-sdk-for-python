# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline checks for legacy query selection, copying, and cleanup."""

import ast
import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]
COPY = ROOT / "tests" / "query_items" / "sync" / "legacy" / "test_query.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("operation,filename,method,query_test,surface", [
    ("read_item", "test_none_options.py", "::TestNoneOptions::test_container_read_item_none_options", None, "sync"),
    ("create_item", "test_none_options.py", "::TestNoneOptions::test_container_create_item_none_options", None, "sync"),
    ("replace_item", "test_none_options.py", "::TestNoneOptions::test_replace_item_none_options", None, "sync"),
    ("upsert_item", "test_none_options.py", "::TestNoneOptions::test_upsert_item_none_options", None, "sync"),
    ("delete_item", "test_none_options.py", "::TestNoneOptions::test_delete_item_none_options", None, "sync"),
    ("query_items", "test_query.py", "::TestQuery::test_query_items_with_parameters_none", None, "sync"),
    ("query_items", "test_query.py", "::TestQuery::test_query_pagination_with_max_item_count", "ordering", "sync"),
    ("query_items", "test_query.py", "::TestQuery::test_offset_limit", "offset", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_offset_limit_async", "offset", "aio"),
    ("query_items", "test_query.py", "::TestQuery::test_distinct", "distinct", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_distinct_async", "distinct", "aio"),
])
def test_owned_runner_selects_original_or_copy(monkeypatch, backend, operation, filename, method, query_test, surface):
    monkeypatch.chdir(ROOT)
    monkeypatch.syspath_prepend(str(ROOT / "tests"))
    for name in ("COSMOS_BACKEND", "COSMOS_TEST_DATA_AUTH_MODE", "COSMOS_PARITY_CAPTURE_OP"):
        monkeypatch.setenv(name, "")
    runner = load_module("_filter_owned_runner", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    monkeypatch.setenv("COSMOS_PARITY_CAPTURE_BACKEND_LABEL", "wrong")
    config = SimpleNamespace(
        TEST_DATABASE_ID="previous-db",
        TEST_SINGLE_PARTITION_CONTAINER_ID="previous-single",
        TEST_MULTI_PARTITION_CONTAINER_ID="previous-multi",
    )
    monkeypatch.setitem(sys.modules, "test_config", SimpleNamespace(TestConfig=config))
    client = MagicMock()
    client.__enter__.return_value = client
    monkeypatch.setattr(runner, "CosmosClient", MagicMock(return_value=client))
    selections = []
    monkeypatch.setattr(runner.pytest, "main", lambda options: selections.append(options) or 0)

    args = ["--backend", backend]
    if operation != "read_item":
        args += ["--op", operation]
    if query_test is not None:
        args += ["--query-test", query_test]
    if surface != "sync":
        args += ["--surface", surface]
    assert runner.main(args) == 0
    options = selections[0]
    folder = ROOT / "tests"
    if backend == "rust":
        folder = folder / operation / surface / "legacy"
    assert str(folder / filename) + method in options
    if operation == "upsert_item":
        assert str(folder / "test_crud.py") + "::TestCRUDOperations::test_document_upsert" in options
    assert "--noconftest" in options
    assert "-s" in options
    assert "common.parity_capture_plugin" in options
    assert runner.os.environ["COSMOS_BACKEND"] == backend
    assert runner.os.environ["COSMOS_PARITY_CAPTURE_OP"] == operation
    assert "COSMOS_PARITY_CAPTURE_BACKEND_LABEL" not in runner.os.environ
    assert config.TEST_DATABASE_ID == "previous-db"
    if backend == "core-python":
        client.delete_database.assert_called_once()
    else:
        client.create_database.assert_not_called()


@pytest.mark.parametrize("method_name,start,stop", [
    ("test_query_items_with_parameters_none", 2, -1),
    ("test_query_pagination_with_max_item_count", 2, -1),
    ("test_offset_limit", 1, -1),
    ("_validate_offset_limit", 0, None),
    ("_validate_distinct_offset_limit", 0, None),
    ("_validate_distinct", 0, None),
])
def test_filter_copy_preserves_original_query_body(method_name, start, stop):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "TestQuery")
        method = next(
            node for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == method_name
        )
        # Only container setup and deletion differ; all queries and assertions match.
        return [ast.dump(node) for node in method.body[start:stop]]

    assert body(ROOT / "tests" / "test_query.py") == body(COPY)


def test_query_selector_rejects_other_operations():
    runner = load_module("_query_selector_guard", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    with pytest.raises(SystemExit) as error:
        runner.main(["--backend", "rust", "--query-test", "ordering"])
    assert error.value.code == 2


@pytest.mark.parametrize("options", [
    [],
    ["--op", "query_items"],
    ["--op", "query_items", "--query-test", "ordering"],
    ["--op", "query_items", "--query-test", "top"],
])
def test_async_selector_rejects_unsupported_selections(options):
    runner = load_module("_async_query_selector_guard", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    with pytest.raises(SystemExit) as error:
        runner.main(["--backend", "rust", "--surface", "aio"] + options)
    assert error.value.code == 2


@pytest.mark.parametrize("filename,source_class,copy_class,method_name", [
    ("test_query_async.py", "TestQueryAsync", "TestQueryAsync", "test_offset_limit_async"),
    ("test_config.py", "TestConfig", "_QueryConfig", "_validate_offset_limit"),
    ("test_config.py", "TestConfig", "_QueryConfig", "_validate_distinct_offset_limit"),
])
def test_async_offset_copy_preserves_original_body(filename, source_class, copy_class, method_name):
    def body(path, class_name):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef)
                      and node.name == method_name)
        # Only the test's owned container setup and final deletion are adapted.
        nodes = method.body[2:-1] if method_name.startswith("test_") else method.body
        return [ast.dump(node) for node in nodes]

    assert body(ROOT / "tests" / filename, source_class) == body(
        ROOT / "tests" / "query_items" / "aio" / "legacy" / "test_query_async.py", copy_class
    )


@pytest.mark.parametrize("surface,filename,class_name,method_name,setup_index", [
    ("sync", "test_query.py", "TestQuery", "test_distinct", 3),
    ("aio", "test_query_async.py", "TestQueryAsync", "test_distinct_async", 4),
])
def test_distinct_copy_preserves_body_and_index_policy(surface, filename, class_name, method_name, setup_index):
    def parts(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name == method_name)
        setup = method.body[setup_index].value
        if isinstance(setup, ast.Await):
            setup = setup.value
        keywords = [ast.dump(keyword) for keyword in setup.keywords if keyword.arg != "id"]
        body = method.body[:setup_index] + method.body[setup_index + 1:-1]
        return [ast.dump(node) for node in body], keywords

    assert parts(ROOT / "tests" / filename) == parts(
        ROOT / "tests" / "query_items" / surface / "legacy" / filename
    )


@pytest.mark.parametrize("method_name", [
    "_get_query_result_string", "_validate_distinct", "_pad_with_none", "_get_distinct_docs",
])
def test_shared_distinct_helpers_preserve_original_implementation(method_name):
    def method(path, class_name):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        return ast.dump(next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                             and node.name == method_name))

    assert method(ROOT / "tests" / "test_config.py", "TestConfig") == method(
        ROOT / "tests" / "query_items" / "_legacy_distinct_helpers.py", "DistinctConfig"
    )


def test_async_fixture_cleans_database_when_container_setup_fails(monkeypatch):
    module = load_module(
        "_offset_async_copy_cleanup",
        ROOT / "tests" / "query_items" / "aio" / "legacy" / "test_query_async.py",
    )
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.close = AsyncMock()
    client.delete_database = AsyncMock()
    database = MagicMock()
    database.create_container = AsyncMock(side_effect=RuntimeError("container setup failed"))
    client.create_database = AsyncMock(return_value=database)
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = module.TestQueryAsync("test_offset_limit_async")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == 1
    assert "container setup failed" in result.errors[0][1]
    assert not result.failures
    client.delete_database.assert_awaited_once_with(case._db_id)
    client.close.assert_awaited_once()


@pytest.mark.parametrize("backend", ["core-python", "rust"])
def test_top_runner_uses_same_copy_with_only_backend_changed(monkeypatch, backend):
    monkeypatch.syspath_prepend(str(ROOT / "scripts" / "v5"))
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    for name in ("COSMOS_BACKEND", "COSMOS_TEST_DATA_AUTH_MODE", "COSMOS_PARITY_CAPTURE_OP"):
        monkeypatch.setenv(name, "")
    monkeypatch.setenv("COSMOS_PARITY_CAPTURE_BACKEND_LABEL", "wrong")
    runner = load_module("_top_owned_runner", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    factory = MagicMock()
    monkeypatch.setattr(runner, "CosmosClient", factory)
    source = ROOT / "tests" / "query_items" / "sync" / "legacy" / "test_orderby.py"
    selected_paths = []

    def run(options):
        path, cls, method = options[-1].split("::")
        target = Path(path)
        selected_paths.append(target)
        assert cls == "TestCrossPartitionTopOrderBy"
        assert method == "test_orderby_top_query"
        actual = target.read_text(encoding="utf-8")
        expected = source.read_text(encoding="utf-8")
        if backend == "core-python":
            expected = expected.replace('_backend="rust"', "_backend='core-python'")
        assert actual == expected
        assert "--noconftest" in options
        assert "-s" in options
        assert "common.parity_capture_plugin" in options
        return 0

    monkeypatch.setattr(runner.pytest, "main", run)
    assert runner.main(["--op", "query_items", "--query-test", "top", "--backend", backend]) == 0
    factory.assert_not_called()
    assert selected_paths[0].exists() == (backend == "rust")
    assert runner.os.environ["COSMOS_BACKEND"] == backend
    assert "COSMOS_PARITY_CAPTURE_BACKEND_LABEL" not in runner.os.environ


@pytest.mark.parametrize("method_name", [
    "test_orderby_top_query", "execute_query_and_validate_results",
])
def test_top_copy_preserves_queries_and_public_assertions(method_name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef)
                   and node.name == "TestCrossPartitionTopOrderBy")
        method = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                      and node.name == method_name)
        return [
            ast.dump(node) for node in method.body
            if not any(isinstance(child, ast.Attribute) and child.attr == "_page_iterator_class"
                       for child in ast.walk(node))
        ]

    assert body(ROOT / "tests" / "test_orderby.py") == body(
        ROOT / "tests" / "query_items" / "sync" / "legacy" / "test_orderby.py"
    )


@pytest.mark.parametrize("filename,class_name,method_name,id_attribute", [
    ("test_query.py", "TestQuery", "test_query_items_with_parameters_none", "_db_id"),
    ("test_orderby.py", "TestCrossPartitionTopOrderBy", "test_orderby_top_query", "database_id"),
])
def test_copied_fixture_cleans_database_when_container_setup_fails(
    monkeypatch, filename, class_name, method_name, id_attribute,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module("_filter_copy_cleanup", COPY.with_name(filename))
    client = MagicMock()
    client.create_database.return_value.create_container.side_effect = RuntimeError("container setup failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = getattr(module, class_name)(method_name)
    try:
        with pytest.raises(RuntimeError, match="container setup failed"):
            case.setUp()
    finally:
        assert case.doCleanups()
    client.delete_database.assert_called_once_with(getattr(case, id_attribute))
    client.close.assert_called_once()
