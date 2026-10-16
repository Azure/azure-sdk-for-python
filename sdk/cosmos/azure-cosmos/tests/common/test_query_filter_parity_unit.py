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
    ("query_items", "test_query.py", "::TestQuery::test_partition_scoped_count_is_index_only", "count", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_partition_scoped_count_is_index_only_async", "count", "aio"),
    ("query_items", "test_query.py", "::TestQuery::test_value_max_query_results", "max", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_value_max_query_results_async", "max", "aio"),
    ("query_items", "test_query.py", "::TestQuery::test_populate_query_metrics", "metrics", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_populate_query_metrics_async", "metrics", "aio"),
    ("query_items", "test_query.py", "::TestQuery::test_populate_index_metrics", "index-metrics", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_populate_index_metrics_async", "index-metrics", "aio"),
    ("query_items", "test_query.py", "::TestQuery::test_populate_query_advice", "advice", "sync"),
    ("query_items", "test_query_async.py", "::TestQueryAsync::test_populate_query_advice_async", "advice", "aio"),
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
    def run(options):
        if backend == "core-python" and (operation == "upsert_item" or query_test in ("count", "max")):
            assert config.TEST_MULTI_PARTITION_CONTAINER_ID == config.TEST_SINGLE_PARTITION_CONTAINER_ID == "orders"
        selections.append(options)
        return 0

    monkeypatch.setattr(runner.pytest, "main", run)

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
    assert config.TEST_SINGLE_PARTITION_CONTAINER_ID == "previous-single"
    assert config.TEST_MULTI_PARTITION_CONTAINER_ID == "previous-multi"
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
    ("test_partition_scoped_count_is_index_only", 1, None),
    ("test_value_max_query_results", 1, None),
    ("test_populate_query_metrics", 1, -1),
    ("test_populate_index_metrics", 1, -1),
    ("test_populate_query_advice", 1, -1),
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


@pytest.mark.parametrize("method_name", [
    "test_partition_scoped_count_is_index_only_async", "test_value_max_query_results_async",
])
def test_async_count_and_max_copy_preserves_original_body(method_name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "TestQueryAsync")
        method = next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef)
                      and node.name == method_name)
        # Only the container lookup is adapted to the owned fixture.
        return [ast.dump(node) for node in method.body[1:]]

    assert body(ROOT / "tests" / "test_query_async.py") == body(
        ROOT / "tests" / "query_items" / "aio" / "legacy" / "test_query_async.py"
    )


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
    ("test_query_async.py", "TestQueryAsync", "TestQueryAsync", "test_populate_query_metrics_async"),
    ("test_query_async.py", "TestQueryAsync", "TestQueryAsync", "test_populate_index_metrics_async"),
    ("test_query_async.py", "TestQueryAsync", "TestQueryAsync", "test_populate_query_advice_async"),
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


@pytest.mark.parametrize("surface,filename,class_name,method_name", [
    ("sync", "test_query.py", "TestQuery", "test_populate_query_advice"),
    ("aio", "test_query_async.py", "TestQueryAsync", "test_populate_query_advice_async"),
])
def test_advice_copy_retains_original_skip_with_environment_category(surface, filename, class_name, method_name):
    def decorators(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name == method_name)
        return method.decorator_list

    original = decorators(ROOT / "tests" / filename)
    copied = decorators(ROOT / "tests" / "query_items" / surface / "legacy" / filename)
    assert len(original) == len(copied) == 1
    assert ast.unparse(original[0].func) == ast.unparse(copied[0].func) == "pytest.mark.skip"
    original_reason = next(keyword.value for keyword in original[0].keywords if keyword.arg == "reason")
    copied_reason = next(keyword.value for keyword in copied[0].keywords if keyword.arg == "reason")
    assert copied_reason.value == "environment-gap: " + original_reason.value
    copied_reason.value = original_reason.value
    assert ast.dump(copied[0]) == ast.dump(original[0])


@pytest.mark.parametrize("failure_stage", [None, "container", "udf", "item"])
def test_deployed_udf_fixture_uses_core_setup_and_always_cleans_database(monkeypatch, failure_stage):
    from query_items import _udf_fixture

    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    client = MagicMock()
    client.__enter__.return_value = client
    client.client_connection._backend.name = "core-python"
    client.client_connection.Create.return_value = {"id": "reviewBand"}
    database = client.create_database.return_value
    container = database.create_container.return_value
    factory = MagicMock(return_value=client)
    monkeypatch.setattr(_udf_fixture, "CosmosClient", factory)
    calls = {
        "container": database.create_container,
        "udf": client.client_connection.Create,
        "item": container.create_item,
    }
    if failure_stage is not None:
        calls[failure_stage].side_effect = RuntimeError("setup failed")
        with pytest.raises(RuntimeError, match="setup failed"):
            with _udf_fixture.deployed_review_band():
                pytest.fail("failed setup must not yield a fixture")
    else:
        with _udf_fixture.deployed_review_band() as database_id:
            assert database_id == client.create_database.call_args.args[0]
            client.delete_database.assert_not_called()
            parent = f"dbs/{database_id}/colls/orders"
            client.client_connection.Create.assert_called_once_with(
                {"id": "reviewBand", "body": _udf_fixture.REVIEW_BAND},
                "/" + parent + "/udfs/",
                "udfs",
                parent,
                None,
            )
            assert container.create_item.call_count == 3
    assert factory.call_args.kwargs["_backend"] == "core-python"
    client.delete_database.assert_called_once_with(client.create_database.call_args.args[0])
    client.__exit__.assert_called_once()


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
@pytest.mark.parametrize("query_test,surface,filename,class_name,method_name", [
    ("top", "sync", "test_orderby.py", "TestCrossPartitionTopOrderBy", "test_orderby_top_query"),
    ("sum", "sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_value_sum_across_full_feed_range_still_sums"),
    ("sum", "aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_value_sum_across_full_feed_range_still_sums_async"),
    ("avg", "sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_with_avg_aggregate_single_partition_feed_range_succeeds"),
    ("avg", "aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async"),
    ("min", "sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_value_min_across_full_feed_range_returns_scalar"),
    ("min", "aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_value_min_across_full_feed_range_returns_scalar_async"),
])
def test_adapted_runner_uses_same_copy_with_only_backend_changed(
    monkeypatch, backend, query_test, surface, filename, class_name, method_name,
):
    monkeypatch.syspath_prepend(str(ROOT / "scripts" / "v5"))
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    for name in ("COSMOS_BACKEND", "COSMOS_TEST_DATA_AUTH_MODE", "COSMOS_PARITY_CAPTURE_OP"):
        monkeypatch.setenv(name, "")
    monkeypatch.setenv("COSMOS_PARITY_CAPTURE_BACKEND_LABEL", "wrong")
    runner = load_module("_top_owned_runner", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    factory = MagicMock()
    monkeypatch.setattr(runner, "CosmosClient", factory)
    source = ROOT / "tests" / "query_items" / surface / "legacy" / filename
    selected_paths = []

    def run(options):
        path, cls, method = options[-1].split("::")
        target = Path(path)
        selected_paths.append(target)
        assert cls == class_name
        assert method == method_name
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
    assert runner.main([
        "--op", "query_items", "--query-test", query_test, "--surface", surface, "--backend", backend,
    ]) == 0
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
    ("test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_value_sum_across_full_feed_range_still_sums", "database_id"),
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


@pytest.mark.parametrize("surface,filename,class_name,method_name", [
    ("sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_value_sum_across_full_feed_range_still_sums"),
    ("aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_value_sum_across_full_feed_range_still_sums_async"),
    ("sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_value_min_across_full_feed_range_returns_scalar"),
    ("aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_value_min_across_full_feed_range_returns_scalar_async"),
])
def test_sum_and_min_copy_preserves_original_query_body(surface, filename, class_name, method_name):
    def parts(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name == method_name)
        # Keep the docstring and all query/validation statements; adapt only container lookup.
        return [ast.dump(node) for node in method.body[:1] + method.body[2:]]

    assert parts(ROOT / "tests" / filename) == parts(
        ROOT / "tests" / "query_items" / surface / "legacy" / filename
    )


@pytest.mark.parametrize("name", ["create_range", "create_feed_range_in_dict"])
def test_sum_range_helpers_preserve_original_implementation(name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        return ast.dump(next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == name))

    assert body(ROOT / "tests" / "test_config.py") == body(
        ROOT / "tests" / "query_items" / "_legacy_feed_range_helpers.py"
    )


@pytest.mark.parametrize("surface,filename,class_name,method_name", [
    ("sync", "test_query_feed_range.py", "TestQueryFeedRange",
     "test_query_with_avg_aggregate_single_partition_feed_range_succeeds"),
    ("aio", "test_query_feed_range_async.py", "TestQueryFeedRangeAsync",
     "test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async"),
])
def test_avg_copy_preserves_original_query_body(surface, filename, class_name, method_name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name == method_name)
        # Only the two container lookups change to owned provisioning.
        return [
            ast.dump(node) for node in method.body
            if not (isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id in ("container", "single_container")
                for target in node.targets
            ))
        ]

    assert body(ROOT / "tests" / filename) == body(
        ROOT / "tests" / "query_items" / surface / "legacy" / filename
    )


def test_async_sum_fixture_cleans_database_when_container_setup_fails(monkeypatch):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module(
        "_sum_async_copy_cleanup",
        ROOT / "tests" / "query_items" / "aio" / "legacy" / "test_query_feed_range_async.py",
    )
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.close = AsyncMock()
    client.delete_database = AsyncMock()
    database = MagicMock()
    database.create_container = AsyncMock(side_effect=RuntimeError("container setup failed"))
    client.create_database = AsyncMock(return_value=database)
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = module.TestQueryFeedRangeAsync("test_query_value_sum_across_full_feed_range_still_sums_async")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == 1
    assert "container setup failed" in result.errors[0][1]
    assert not result.failures
    client.delete_database.assert_awaited_once_with(case.database_id)
    client.close.assert_awaited_once()
