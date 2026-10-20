# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline checks for owned query selection, retained helpers, and cleanup."""

import ast
import asyncio
import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]
COPY = ROOT / "tests" / "query_items" / "sync" / "legacy" / "test_query.py"


def _method_name(path, name):
    if path.parent != ROOT / "tests" and name.startswith("test_"):
        return name + "_rust"
    return name


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("operation,filename,method", [
    ("read_item", "test_none_options.py", "::TestNoneOptions::test_container_read_item_none_options"),
    ("create_item", "test_none_options.py", "::TestNoneOptions::test_container_create_item_none_options"),
    ("replace_item", "test_none_options.py", "::TestNoneOptions::test_replace_item_none_options"),
    ("upsert_item", "test_none_options.py", "::TestNoneOptions::test_upsert_item_none_options"),
    ("delete_item", "test_none_options.py", "::TestNoneOptions::test_delete_item_none_options"),
])
def test_owned_item_runner_selects_original_or_copy_rust(monkeypatch, backend, operation, filename, method):
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
        if backend == "core-python" and operation == "upsert_item":
            assert config.TEST_MULTI_PARTITION_CONTAINER_ID == config.TEST_SINGLE_PARTITION_CONTAINER_ID == "orders"
        selections.append(options)
        return 0

    monkeypatch.setattr(runner.pytest, "main", run)

    args = ["--backend", backend]
    if operation != "read_item":
        args += ["--op", operation]
    assert runner.main(args) == 0
    options = selections[0]
    folder = ROOT / "tests"
    if backend == "rust":
        folder = folder / operation / "sync" / "legacy"
    suffix = "_rust" if backend == "rust" else ""
    assert str(folder / filename) + method + suffix in options
    if operation == "upsert_item":
        assert str(folder / "test_crud.py") + "::TestCRUDOperations::test_document_upsert" + suffix in options
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
    ("_validate_offset_limit", 0, None),
    ("_validate_distinct_offset_limit", 0, None),
    ("_validate_distinct", 0, None),
])
def test_sync_query_helpers_preserve_original_body_rust(method_name, start, stop):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "TestQuery")
        method = next(
            node for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == _method_name(path, method_name)
        )
        return [ast.dump(node) for node in method.body[start:stop]]

    assert body(ROOT / "tests" / "test_query.py") == body(COPY)


def test_query_selector_rejects_other_operations_rust():
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
def test_async_selector_rejects_unsupported_selections_rust(options):
    runner = load_module("_async_query_selector_guard", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    with pytest.raises(SystemExit) as error:
        runner.main(["--backend", "rust", "--surface", "aio"] + options)
    assert error.value.code == 2


@pytest.mark.parametrize("filename,source_class,copy_class,method_name", [
    ("test_config.py", "TestConfig", "_QueryConfig", "_validate_offset_limit"),
    ("test_config.py", "TestConfig", "_QueryConfig", "_validate_distinct_offset_limit"),
])
def test_async_query_helpers_preserve_original_body_rust(filename, source_class, copy_class, method_name):
    def body(path, class_name):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef)
                      and node.name == _method_name(path, method_name))
        return [ast.dump(node) for node in method.body]

    assert body(ROOT / "tests" / filename, source_class) == body(
        ROOT / "tests" / "query_items" / "aio" / "legacy" / "test_query_async.py", copy_class
    )


@pytest.mark.parametrize("method_name", [
    "_get_query_result_string", "_validate_distinct", "_pad_with_none", "_get_distinct_docs",
])
def test_shared_distinct_helpers_preserve_original_implementation_rust(method_name):
    def method(path, class_name):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        return ast.dump(next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                             and node.name == _method_name(path, method_name)))

    assert method(ROOT / "tests" / "test_config.py", "TestConfig") == method(
        ROOT / "tests" / "query_items" / "_legacy_distinct_helpers.py", "DistinctConfig"
    )


@pytest.mark.parametrize("surface,filename,class_name,method_name", [
    ("sync", "test_query.py", "TestQuery", "test_populate_query_advice"),
    ("aio", "test_query_async.py", "TestQueryAsync", "test_populate_query_advice_async"),
])
def test_advice_copy_retains_environment_skip_rust(surface, filename, class_name, method_name):
    def decorators(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == class_name)
        method = next(node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name == _method_name(path, method_name))
        return method.decorator_list

    copied = decorators(ROOT / "tests" / "query_items" / surface / "legacy" / filename)
    assert len(copied) == 1
    assert ast.unparse(copied[0].func) == "pytest.mark.skip"
    copied_reason = next(keyword.value for keyword in copied[0].keywords if keyword.arg == "reason")
    assert copied_reason.value == "environment-gap: Emulator does not support query advisor yet"


@pytest.mark.parametrize("failure_stage", [None, "container", "udf", "item"])
def test_deployed_udf_fixture_uses_core_setup_and_always_cleans_database_rust(monkeypatch, failure_stage):
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


def test_async_fixture_cleans_database_when_container_setup_fails_rust(monkeypatch):
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
    case = module.TestQueryAsync("test_offset_limit_async_rust")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == 1
    assert "container setup failed" in result.errors[0][1]
    assert not result.failures
    client.delete_database.assert_awaited_once_with(case._db_id)
    client.close.assert_awaited_once()


@pytest.mark.parametrize("backend", ["core-python", "rust"])
@pytest.mark.parametrize("exit_code", [0, 1])
@pytest.mark.parametrize("query_test,surface,filename,class_name,method_name", [
    (selection, surface, f"test_query{suffix}.py", f"TestQuery{class_suffix}", method + suffix)
    for selection, method in (
        ("parameters", "test_query_items_with_parameters_none"),
        ("ordering", "test_query_pagination_with_max_item_count"),
        ("offset", "test_offset_limit"),
        ("distinct", "test_distinct"),
        ("count", "test_partition_scoped_count_is_index_only"),
        ("max", "test_value_max_query_results"),
        ("metrics", "test_populate_query_metrics"),
        ("index-metrics", "test_populate_index_metrics"),
        ("advice", "test_populate_query_advice"),
        ("continuation", "test_paging_with_continuation_token"),
        ("cross-continuation", "test_cross_partition_query_with_continuation_token"),
        ("token-limit", "test_continuation_token_size_limit_query"),
    )
    for surface, suffix, class_suffix in (("sync", "", ""), ("aio", "_async", "Async"))
    if surface == "sync" or selection not in ("parameters", "ordering")
] + [
    ("partition-feed-range", "sync", "test_query_feed_range_discovery.py", "TestQueryFeedRange",
     "test_query_with_feed_range_for_partition_key"),
    ("partition-feed-range", "aio", "test_query_feed_range_discovery_async.py", "TestQueryFeedRangeAsync",
     "test_query_with_feed_range_for_partition_key_async"),
    ("feed-ranges", "sync", "test_query_feed_range_discovery.py", "TestQueryFeedRange",
     "test_query_with_feed_range_for_all_partitions"),
    ("feed-ranges", "aio", "test_query_feed_range_discovery_async.py", "TestQueryFeedRangeAsync",
     "test_query_with_feed_range_for_all_partitions_async"),
    (None, "sync", "test_query.py", "TestQuery", "test_query_items_with_parameters_none"),
    ("none-options", "sync", "test_none_options.py", "TestNoneOptions",
     "test_container_query_items_none_options_partition"),
    ("none-options", "aio", "test_none_options_async.py", "TestNoneOptionsAsync",
     "test_container_query_items_none_options_partition_async"),
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
    ("prefix-continuation", "sync", "test_query_feed_range_multipartition.py", "TestFeedRangeMultiPartition",
     "test_prefix_partition_key_query_pagination_resume"),
    ("prefix-continuation", "aio", "test_query_feed_range_multipartition_async.py", "TestFeedRangeMultiPartitionAsync",
     "test_prefix_partition_key_query_pagination_resume_async"),
])
def test_adapted_runner_uses_same_copy_with_only_backend_changed_rust(
    monkeypatch, backend, exit_code, query_test, surface, filename, class_name, method_name,
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
        assert method == method_name + "_rust"
        actual = target.read_text(encoding="utf-8")
        expected = source.read_text(encoding="utf-8")
        if backend == "core-python":
            assert actual.count("_backend='core-python'") == 1
            actual = actual.replace("_backend='core-python'", '_backend="rust"', 1)
        assert actual == expected
        assert "--noconftest" in options
        assert "-s" in options
        assert "common.parity_capture_plugin" in options
        return exit_code

    monkeypatch.setattr(runner.pytest, "main", run)
    args = ["--op", "query_items", "--surface", surface, "--backend", backend]
    if query_test is not None:
        args += ["--query-test", query_test]
    assert runner.main(args) == exit_code
    factory.assert_not_called()
    assert selected_paths[0].exists() == (backend == "rust")
    assert runner.os.environ["COSMOS_BACKEND"] == backend
    assert "COSMOS_PARITY_CAPTURE_BACKEND_LABEL" not in runner.os.environ


@pytest.mark.parametrize("method_name", [
    "execute_query_and_validate_results",
])
def test_top_copy_preserves_queries_and_public_assertions_rust(method_name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef)
                   and node.name == "TestCrossPartitionTopOrderBy")
        method = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                      and node.name == _method_name(path, method_name))
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
def test_copied_fixture_cleans_database_when_container_setup_fails_rust(
    monkeypatch, filename, class_name, method_name, id_attribute,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module("_filter_copy_cleanup", COPY.with_name(filename))
    client = MagicMock()
    client.create_database.return_value.create_container.side_effect = RuntimeError("container setup failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = getattr(module, class_name)(method_name + "_rust")
    try:
        with pytest.raises(RuntimeError, match="container setup failed"):
            case.setUp()
    finally:
        assert case.doCleanups()
    client.delete_database.assert_called_once_with(getattr(case, id_attribute))
    client.close.assert_called_once()


@pytest.mark.parametrize("name", ["create_range", "create_feed_range_in_dict"])
def test_sum_range_helpers_preserve_original_implementation_rust(name):
    def body(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        return ast.dump(next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == name))

    assert body(ROOT / "tests" / "test_config.py") == body(
        ROOT / "tests" / "query_items" / "_legacy_feed_range_helpers.py"
    )


@pytest.mark.parametrize("surface,suffix", [("sync", ""), ("aio", "_async")])
@pytest.mark.parametrize("failure_stage", ["container", "query"])
def test_prefix_fixture_cleans_owned_database_on_failure_rust(monkeypatch, surface, suffix, failure_stage):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module(
        f"_prefix_cleanup_{surface}",
        ROOT / "tests" / "query_items" / surface / "legacy" / f"test_query_feed_range_multipartition{suffix}.py",
    )
    client, database, container = MagicMock(), MagicMock(), MagicMock()
    if surface == "aio":
        client.__aenter__ = AsyncMock(return_value=client)
        client.close = AsyncMock()
        client.create_database = AsyncMock(return_value=database)
        client.delete_database = AsyncMock()
        database.create_container_if_not_exists = AsyncMock(return_value=container)
        database.delete_container = AsyncMock()
        container.upsert_item = AsyncMock()
    else:
        client.create_database.return_value = database
        database.create_container_if_not_exists.return_value = container
    target = database.create_container_if_not_exists if failure_stage == "container" else container.query_items
    target.side_effect = RuntimeError(f"{failure_stage} failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    class_name = "TestFeedRangeMultiPartitionAsync" if surface == "aio" else "TestFeedRangeMultiPartition"
    case = getattr(module, class_name)(f"test_prefix_partition_key_query_pagination_resume{suffix}_rust")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == 1
    assert f"{failure_stage} failed" in result.errors[0][1]
    assert not result.failures
    if surface == "aio":
        client.delete_database.assert_awaited_once_with(case.database_id)
        client.close.assert_awaited_once()
    else:
        client.delete_database.assert_called_once_with(case.database_id)
        client.close.assert_called_once()


def test_async_sum_fixture_cleans_database_when_container_setup_fails_rust(monkeypatch):
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
    case = module.TestQueryFeedRangeAsync("test_query_value_sum_across_full_feed_range_still_sums_async_rust")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == 1
    assert "container setup failed" in result.errors[0][1]
    assert not result.failures
    client.delete_database.assert_awaited_once_with(case.database_id)
    client.close.assert_awaited_once()


@pytest.mark.parametrize("surface,suffix", [("sync", ""), ("aio", "_async")])
@pytest.mark.parametrize("scope", ["all_partitions", "partition_key"])
def test_feed_range_copies_preserve_original_bodies_helpers_and_profiles_rust(surface, suffix, scope):
    original = ast.parse((ROOT / "tests" / f"test_query_feed_range{suffix}.py").read_text(encoding="utf-8"))
    path = ROOT / "tests" / "query_items" / surface / "legacy" / f"test_query_feed_range_discovery{suffix}.py"
    copied = ast.parse(path.read_text(encoding="utf-8"))
    method_name = f"test_query_with_feed_range_for_{scope}{suffix}"

    def function(tree, name):
        return next(node for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)

    old_method = function(original, method_name)
    new_method = function(copied, method_name + "_rust")
    assert ast.dump(old_method.args) == ast.dump(new_method.args)
    assert [ast.dump(node) for node in old_method.body] == [ast.dump(node) for node in new_method.body]
    assert [ast.dump(node) for node in old_method.decorator_list] == [
        ast.dump(node) for node in new_method.decorator_list
    ]
    for name in (f"add_all_pk_values_to_set{suffix}", "get_container"):
        assert ast.dump(function(original, name)) == ast.dump(function(copied, name))

    module = load_module(f"_ranges_profiles_{surface}", path)
    config = ast.parse((ROOT / "tests" / "test_config.py").read_text(encoding="utf-8"))
    config_class = next(node for node in config.body if isinstance(node, ast.ClassDef) and node.name == "TestConfig")
    values = {
        target.id: node.value for node in config_class.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }
    assert module.TEST_CONTAINERS_IDS == ["single", "multi"]
    assert module.TEST_OFFER_THROUGHPUTS == [
        ast.literal_eval(values["THROUGHPUT_FOR_1_PARTITION"]),
        ast.literal_eval(values["THROUGHPUT_FOR_5_PARTITIONS"]),
    ]
    assert module.PARTITION_KEY == ast.literal_eval(values["TEST_CONTAINER_PARTITION_KEY"])
    for name in ("PK_VALUES", "RUN_MARKER_FIELD"):
        original_value = next(node.value for node in original.body if isinstance(node, ast.Assign)
                              and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
        assert getattr(module, name) == ast.literal_eval(original_value)


@pytest.mark.parametrize("surface,suffix", [("sync", ""), ("aio", "_async")])
@pytest.mark.parametrize("container_id,throughput", [("single", 400), ("multi", 30000)])
@pytest.mark.parametrize("failure_stage", ["container", "seed", "query", "cleanup"])
def test_all_ranges_owned_fixture_cleans_up_and_surfaces_failures_rust(
    monkeypatch, capsys, surface, suffix, container_id, throughput, failure_stage,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    path = ROOT / "tests" / "query_items" / surface / "legacy" / f"test_query_feed_range_discovery{suffix}.py"
    module = load_module(f"_ranges_cleanup_{surface}", path)
    client, database, container = MagicMock(), MagicMock(), MagicMock()
    if surface == "aio":
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.create_database = AsyncMock(return_value=database)
        client.delete_database = AsyncMock()
        database.create_container = AsyncMock(return_value=container)
        container.upsert_item = AsyncMock()
    else:
        client.__enter__.return_value = client
        client.create_database.return_value = database
        database.create_container.return_value = container
    if failure_stage != "query":
        target = {
            "container": database.create_container,
            "seed": container.upsert_item,
            "cleanup": client.delete_database,
        }[failure_stage]
        target.side_effect = RuntimeError(f"{failure_stage} failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))

    if surface == "aio":
        request = SimpleNamespace(instance=SimpleNamespace(data_db=None))

        async def exercise():
            fixture = module.setup_and_teardown_async.__wrapped__(request, container_id)
            with pytest.raises(RuntimeError, match=f"{failure_stage} failed"):
                await anext(fixture)
                if failure_stage == "query":
                    print("FAILED", end="")
                    await fixture.athrow(RuntimeError("query failed"))
                else:
                    await fixture.aclose()

        asyncio.run(exercise())
        assert request.instance.data_db is None
        client.delete_database.assert_awaited_once_with(client.create_database.call_args.args[0])
        client.__aexit__.assert_awaited_once()
    else:
        fixture = module.setup.__wrapped__(container_id)
        with pytest.raises(RuntimeError, match=f"{failure_stage} failed"):
            next(fixture)
            if failure_stage == "query":
                print("FAILED", end="")
                fixture.throw(RuntimeError("query failed"))
            else:
                fixture.close()
        client.delete_database.assert_called_once_with(client.create_database.call_args.args[0])
        client.__exit__.assert_called_once()
    assert database.create_container.call_args.kwargs["id"] == container_id
    assert database.create_container.call_args.kwargs["offer_throughput"] == throughput
    if failure_stage == "query":
        assert "FAILED\nDeleted owned" in capsys.readouterr().out
