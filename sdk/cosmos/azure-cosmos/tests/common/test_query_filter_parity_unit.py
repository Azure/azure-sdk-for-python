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
COPY = ROOT / "tests" / "query_items" / "sync" / "test_query.py"


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
        folder = folder / operation / "sync"
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
    ("test_query_positional_args", 1, None),
])
def test_sync_query_helpers_preserve_original_body_rust(method_name, start, stop):
    def body(path):
        source = path.read_text(encoding="utf-8")
        if method_name == "test_query_positional_args":
            source = source.replace("self.config.TEST_CONTAINER_PARTITION_KEY", "'pk'")
        module = ast.parse(source)
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
    ["--op", "query_items", "--query-test", "positional"],
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
        ROOT / "tests" / "query_items" / "aio" / "test_query_async.py", copy_class
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

    copied = decorators(ROOT / "tests" / "query_items" / surface / filename)
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
        ROOT / "tests" / "query_items" / "aio" / "test_query_async.py",
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
        ("positional", "test_query_positional_args"),
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
    if surface == "sync" or selection not in ("parameters", "ordering", "positional")
] + [
    ("vector-partition-hook", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_vector_query_partitioned_response_hook"),
    ("vector-partition-hook", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_vector_query_partitioned_response_hook_async"),
    ("vector-cross-hook", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_vector_query_cross_partition_response_hook"),
    ("vector-cross-hook", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_vector_query_cross_partition_response_hook_async"),
    ("vector-large-data", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_vector_query_large_data"),
    ("vector-large-data", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_vector_query_large_data_async"),
    ("vector-buffer", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_vector_search_environment_variables"),
    ("vector-buffer", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_vector_search_environment_variables_async"),
    ("vector-rejection", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_wrong_vector_search_queries"),
    ("vector-rejection", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_wrong_vector_search_queries_async"),
    ("vector-pagination", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_vector_query_pagination"),
    ("vector-pagination", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_vector_query_pagination_async"),
    ("vector-ordering", "sync", "test_query_vector_similarity.py", "TestVectorSimilarityQuery",
     "test_ordering_distances"),
    ("vector-ordering", "aio", "test_query_vector_similarity_async.py", "TestVectorSimilarityQueryAsync",
     "test_ordering_distances_async"),
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
    source = ROOT / "tests" / "query_items" / surface / filename
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
        ROOT / "tests" / "query_items" / "sync" / "test_orderby.py"
    )


@pytest.mark.parametrize("name", [
    "verify_ordering", "test_ordering_distances", "test_vector_query_pagination", "test_wrong_vector_search_queries",
    "test_vector_search_environment_variables", "test_vector_query_large_data",
    "test_vector_query_cross_partition_response_hook",
    "test_vector_query_partitioned_response_hook",
])
def test_vector_ordering_preserves_original_body_rust(name):
    def body(path):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        function = next(node for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and node.name == _method_name(path, name))
        return ast.dump(function.args), [ast.dump(node) for node in function.body]

    filename = "test_query_vector_similarity.py"
    assert body(ROOT / "tests" / filename) == body(COPY.with_name(filename))


@pytest.mark.parametrize("failure_stage", [None, "container", "item"])
@pytest.mark.parametrize("method_name,profile_count", [
    ("test_ordering_distances_rust", 3),
    ("test_vector_query_pagination_rust", 1),
    ("test_vector_query_cross_partition_response_hook_rust", 1),
    ("test_vector_query_partitioned_response_hook_rust", 1),
])
def test_vector_ordering_fixture_preserves_profiles_and_cleans_up_rust(
    monkeypatch, failure_stage, method_name, profile_count,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module("_vector_ordering_copy", COPY.with_name("test_query_vector_similarity.py"))
    setup_client, query_client = MagicMock(), MagicMock()
    factory = MagicMock(side_effect=[setup_client, query_client])
    monkeypatch.setattr(module, "CosmosClient", factory)
    database = setup_client.create_database.return_value
    create_container = database.create_container
    create_item = create_container.return_value.create_item
    if failure_stage == "container":
        create_container.side_effect = RuntimeError("container failed")
    elif failure_stage == "item":
        create_item.side_effect = RuntimeError("item failed")
    case = module.TestVectorSimilarityQuery(method_name)
    try:
        if failure_stage is None:
            case.setUp()
            assert create_container.call_count == profile_count
            assert create_item.call_count == 10 * profile_count
            for call, index_type, distance in zip(
                create_container.call_args_list,
                ("quantizedFlat", "flat", "diskANN"),
                ("cosine", "euclidean", "dotproduct"),
            ):
                assert call.kwargs["offer_throughput"] == module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS
                assert call.kwargs["indexing_policy"] == module.test_config.get_vector_indexing_policy(index_type)
                assert call.kwargs["vector_embedding_policy"] == module.test_config.get_vector_embedding_policy(
                    distance, "float32", 128
                )
            assert [call.args[0] for call in create_item.call_args_list] == (
                module.vector_test_data.get_vector_items() * profile_count
            )
        else:
            with pytest.raises(RuntimeError, match=f"{failure_stage} failed"):
                case.setUp()
    finally:
        assert case.doCleanups()
    assert [call.kwargs["_backend"] for call in factory.call_args_list] == ["core-python", "rust"]
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    query_client.close.assert_called_once()


@pytest.mark.parametrize("surface,method_name,expected_rows,expected_hooks,scope", [
    ("sync", "test_vector_query_cross_partition_response_hook_rust", 5, 2, {"enable_cross_partition_query": True}),
    ("sync", "test_vector_query_partitioned_response_hook_rust", 4, 1, {"partition_key": "1"}),
    ("aio", "test_vector_query_partitioned_response_hook_async_rust", 4, 1, {"partition_key": "1"}),
    ("aio", "test_vector_query_cross_partition_response_hook_async_rust", 5, 2, {}),
])
@pytest.mark.parametrize("row_delta,hook_delta,query_error", [
    (0, 0, False),
    (0, -1, False),
    (0, 1, False),
    (-1, 0, False),
    (1, 0, False),
    (0, -1, True),
])
def test_vector_hook_copies_preserve_exact_assertions_and_cleanup_rust(
    monkeypatch, surface, method_name, expected_rows, expected_hooks, scope, row_delta, hook_delta, query_error,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    suffix = "_async" if surface == "aio" else ""
    path = ROOT / "tests" / "query_items" / surface / f"test_query_vector_similarity{suffix}.py"
    module = load_module("_vector_hook_copy", path)
    setup_client, query_client = MagicMock(), MagicMock()
    if surface == "aio":
        query_client.__aenter__ = AsyncMock(return_value=query_client)
        query_client.close = AsyncMock()
        monkeypatch.setattr(module, "CosmosSyncClient", MagicMock(return_value=setup_client))
        monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=query_client))
    else:
        monkeypatch.setattr(module, "CosmosClient", MagicMock(side_effect=[setup_client, query_client]))
    container = query_client.get_database_client.return_value.get_container_client.return_value

    def query(**kwargs):
        assert set(kwargs) == {"query", "response_hook"} | set(scope)
        assert kwargs["query"].startswith(f"SELECT TOP {expected_rows} ")
        for key, value in scope.items():
            assert kwargs[key] == value
            assert type(kwargs[key]) is type(value)
        assert isinstance(kwargs["response_hook"], module.test_config.ResponseHookCaller)

        def respond():
            for _ in range(expected_hooks + hook_delta):
                kwargs["response_hook"]({}, {})
            if query_error:
                raise RuntimeError("query failed")

        if surface == "aio":
            async def rows():
                respond()
                for _ in range(expected_rows + row_delta):
                    yield None
            return rows()
        respond()
        return [None] * (expected_rows + row_delta)

    container.query_items.side_effect = query
    class_name = "TestVectorSimilarityQueryAsync" if surface == "aio" else "TestVectorSimilarityQuery"
    case = getattr(module, class_name)(method_name)
    result = unittest.TestResult()
    case.run(result)
    assert len(result.errors) == int(query_error)
    assert len(result.failures) == int(not query_error and (row_delta != 0 or hook_delta != 0))
    if query_error:
        assert "query failed" in result.errors[0][1]
    container.query_items.assert_called_once()
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    if surface == "aio":
        query_client.close.assert_awaited_once()
    else:
        query_client.close.assert_called_once()


@pytest.mark.parametrize("failure_stage", [None, "container", "query"])
@pytest.mark.parametrize("method_name", [
    "test_wrong_vector_search_queries_rust", "test_vector_search_environment_variables_rust",
])
def test_vector_rejection_fixture_preserves_empty_container_and_cleanup_rust(monkeypatch, failure_stage, method_name):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    module = load_module("_vector_rejection_copy", COPY.with_name("test_query_vector_similarity.py"))
    setup_client, query_client = MagicMock(), MagicMock()
    factory = MagicMock(side_effect=[setup_client, query_client])
    monkeypatch.setattr(module, "CosmosClient", factory)
    database = setup_client.create_database.return_value
    if failure_stage == "container":
        database.create_container.side_effect = RuntimeError("container failed")

    def exercise(case):
        assert case.created_large_container is (
            query_client.get_database_client.return_value.get_container_client.return_value
        )
        if failure_stage == "query":
            raise RuntimeError("query failed")

    monkeypatch.setattr(module.TestVectorSimilarityQuery, method_name, exercise)
    case = module.TestVectorSimilarityQuery(method_name)
    result = unittest.TestResult()
    case.run(result)
    assert not result.failures
    assert len(result.errors) == (0 if failure_stage is None else 1)
    if failure_stage is not None:
        assert f"{failure_stage} failed" in result.errors[0][1]
    database.create_container.assert_called_once()
    options = database.create_container.call_args.kwargs
    assert options["offer_throughput"] == module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS
    assert options["partition_key"] == module.PartitionKey(path="/pk")
    assert options["indexing_policy"] == module.test_config.get_vector_indexing_policy("quantizedFlat")
    assert options["vector_embedding_policy"] == module.test_config.get_vector_embedding_policy(
        "cosine", "float32", 2
    )
    database.create_container.return_value.create_item.assert_not_called()
    assert [call.kwargs["_backend"] for call in factory.call_args_list] == ["core-python", "rust"]
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    query_client.close.assert_called_once()


@pytest.mark.parametrize("previous", [None, "17"])
@pytest.mark.parametrize("failure_stage", [None, "first", "second"])
@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_vector_buffer_copy_restores_environment_after_queries_rust(monkeypatch, previous, failure_stage, surface):
    name = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    if previous is None:
        monkeypatch.delenv(name, raising=False)
    else:
        monkeypatch.setenv(name, previous)
    suffix = "_async" if surface == "aio" else ""
    path = ROOT / "tests" / "query_items" / surface / f"test_query_vector_similarity{suffix}.py"
    module = load_module("_vector_buffer_copy", path)
    setup_client, query_client = MagicMock(), MagicMock()
    if surface == "aio":
        query_client.__aenter__ = AsyncMock(return_value=query_client)
        query_client.close = AsyncMock()
        monkeypatch.setattr(module, "CosmosSyncClient", MagicMock(return_value=setup_client))
        monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=query_client))
    else:
        monkeypatch.setattr(module, "CosmosClient", MagicMock(side_effect=[setup_client, query_client]))
    container = query_client.get_database_client.return_value.get_container_client.return_value
    observed = []

    def query(**kwargs):
        assert set(kwargs) == ({"query"} if surface == "aio" else {"query", "enable_cross_partition_query"})
        if surface == "sync":
            assert kwargs["enable_cross_partition_query"] is True
        assert kwargs["query"].startswith("SELECT TOP 10 ")
        observed.append(module.os.environ[name])
        stage = "first" if len(observed) == 1 else "second"

        def consume():
            if stage == failure_stage:
                raise RuntimeError(f"{stage} failed")
            if stage == "first":
                raise ValueError(
                    "Executing a vector search query with more items than the max is not allowed. "
                    "Please ensure you are using a limit smaller than the max, or change the max."
                )
            return []

        if surface == "aio":
            async def rows():
                for item in consume():
                    yield item
            return rows()
        return consume()

    container.query_items.side_effect = query
    class_name = "TestVectorSimilarityQueryAsync" if surface == "aio" else "TestVectorSimilarityQuery"
    case = getattr(module, class_name)(f"test_vector_search_environment_variables{suffix}_rust")
    result = unittest.TestResult()
    case.run(result)
    assert not result.failures
    assert len(result.errors) == (0 if failure_stage is None else 1)
    if failure_stage is not None:
        assert f"{failure_stage} failed" in result.errors[0][1]
    assert observed == (["1"] if failure_stage == "first" else ["1", "50000"])
    assert module.os.environ.get(name) == previous
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    if surface == "aio":
        query_client.close.assert_awaited_once()
    else:
        query_client.close.assert_called_once()


@pytest.mark.parametrize("failure_stage", [None, "container", "item", "query"])
def test_vector_large_data_fixture_routes_only_queries_to_selected_backend_rust(monkeypatch, failure_stage):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    name = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    monkeypatch.delenv(name, raising=False)
    module = load_module("_vector_large_data_copy", COPY.with_name("test_query_vector_similarity.py"))
    setup_client, query_client = MagicMock(), MagicMock()
    factory = MagicMock(side_effect=[setup_client, query_client])
    monkeypatch.setattr(module, "CosmosClient", factory)
    database = setup_client.create_database.return_value
    seed_container = database.create_container.return_value
    query_container = query_client.get_database_client.return_value.get_container_client.return_value
    original_create_item = query_container.create_item
    if failure_stage == "container":
        database.create_container.side_effect = RuntimeError("container failed")
    elif failure_stage == "item":
        seed_container.create_item.side_effect = RuntimeError("item failed")
    if failure_stage == "query":
        query_container.query_items.side_effect = RuntimeError("query failed")
    else:
        query_container.query_items.side_effect = [
            [None] * count for count in (1000, 1000, 750, 750, 500, 500)
        ]

    case = module.TestVectorSimilarityQuery("test_vector_query_large_data_rust")
    result = unittest.TestResult()
    case.run(result)
    assert not result.failures
    assert len(result.errors) == (0 if failure_stage is None else 1)
    if failure_stage is not None:
        assert f"{failure_stage} failed" in result.errors[0][1]
    database.create_container.assert_called_once()
    options = database.create_container.call_args.kwargs
    assert options["offer_throughput"] == module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS
    assert options["partition_key"] == module.PartitionKey(path="/pk")
    assert options["indexing_policy"] == module.test_config.get_vector_indexing_policy("quantizedFlat")
    assert options["vector_embedding_policy"] == module.test_config.get_vector_embedding_policy(
        "cosine", "float32", 2
    )
    assert query_container.create_item is original_create_item
    original_create_item.assert_not_called()
    assert name not in module.os.environ
    if failure_stage == "container":
        seed_container.create_item.assert_not_called()
    elif failure_stage == "item":
        seed_container.create_item.assert_called_once()
    else:
        assert seed_container.create_item.call_count == 2000
        embedding_value = 0.0001
        for i, call in enumerate(seed_container.create_item.call_args_list):
            assert call.args == (
                {"id": str(i), "pk": i % 2, "embedding": [embedding_value, embedding_value]},
            )
            assert not call.kwargs
            embedding_value += 0.0001
    assert query_container.query_items.call_count == (
        6 if failure_stage is None else 1 if failure_stage == "query" else 0
    )
    for call in query_container.query_items.call_args_list:
        assert call.kwargs["enable_cross_partition_query"] is True
        assert set(call.kwargs) == {"query", "enable_cross_partition_query"}
    assert [call.kwargs["_backend"] for call in factory.call_args_list] == ["core-python", "rust"]
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    query_client.close.assert_called_once()


@pytest.mark.parametrize("failure_stage", [
    None, "container", "enter", "seed-enter", "item", "query", "first-count", "last-count",
])
def test_async_vector_large_data_preserves_awaited_seeding_queries_and_cleanup_rust(monkeypatch, failure_stage):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    name = "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH"
    monkeypatch.delenv(name, raising=False)
    path = ROOT / "tests" / "query_items" / "aio" / "test_query_vector_similarity_async.py"
    module = load_module("_async_vector_large_data_copy", path)
    setup_client, query_client, seed_client = MagicMock(), MagicMock(), MagicMock()
    for client in (query_client, seed_client):
        client.__aenter__ = AsyncMock(return_value=client)
        client.close = AsyncMock()
    setup_factory = MagicMock(return_value=setup_client)
    query_factory = MagicMock(side_effect=[query_client, seed_client])
    monkeypatch.setattr(module, "CosmosSyncClient", setup_factory)
    monkeypatch.setattr(module, "CosmosClient", query_factory)
    database = setup_client.create_database.return_value
    query_container = query_client.get_database_client.return_value.get_container_client.return_value
    seed_container = seed_client.get_database_client.return_value.get_container_client.return_value
    query_container.create_item = AsyncMock()
    seed_container.create_item = AsyncMock()
    original_create_item = query_container.create_item
    targets = {
        "container": database.create_container,
        "enter": query_client.__aenter__,
        "seed-enter": seed_client.__aenter__,
        "item": seed_container.create_item,
        "query": query_container.query_items,
    }
    if failure_stage in targets:
        targets[failure_stage].side_effect = RuntimeError(f"{failure_stage} failed")
    else:
        async def rows(count):
            for _ in range(count):
                yield None

        counts = [1000, 1000, 750, 750, 500, 500]
        if failure_stage == "first-count":
            counts[0] -= 1
        elif failure_stage == "last-count":
            counts[-1] -= 1
        query_container.query_items.side_effect = [rows(count) for count in counts]
    case = module.TestVectorSimilarityQueryAsync("test_vector_query_large_data_async_rust")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.failures) == int(failure_stage in ("first-count", "last-count"))
    assert len(result.errors) == int(failure_stage in targets)
    if failure_stage in targets:
        assert f"{failure_stage} failed" in result.errors[0][1]
    database.create_container.assert_called_once()
    options = database.create_container.call_args.kwargs
    assert options["partition_key"] == module.PartitionKey(path="/pk")
    assert options["offer_throughput"] == module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS
    assert options["indexing_policy"] == module.test_config.get_vector_indexing_policy("quantizedFlat")
    assert options["vector_embedding_policy"] == module.test_config.get_vector_embedding_policy(
        "cosine", "float32", 2
    )
    database.create_container.return_value.create_item.assert_not_called()
    assert query_container.create_item is original_create_item
    original_create_item.assert_not_called()
    expected_seeds = (
        0 if failure_stage in ("container", "enter", "seed-enter") else 1 if failure_stage == "item" else 2000
    )
    assert seed_container.create_item.call_count == seed_container.create_item.await_count == expected_seeds
    embedding_value = 0.0001
    for i, call in enumerate(seed_container.create_item.await_args_list):
        assert call.args == ({"id": str(i), "pk": i % 2, "embedding": [embedding_value, embedding_value]},)
        assert not call.kwargs
        embedding_value += 0.0001
    assert query_container.query_items.call_count == (
        6 if failure_stage in (None, "last-count") else 1 if failure_stage in ("query", "first-count") else 0
    )
    for call in query_container.query_items.call_args_list:
        assert set(call.kwargs) == {"query"}
    assert name not in module.os.environ
    assert setup_factory.call_args.kwargs["_backend"] == "core-python"
    expected_backends = (
        [] if failure_stage == "container" else ["rust"] if failure_stage == "enter" else ["rust", "core-python"]
    )
    assert [call.kwargs["_backend"] for call in query_factory.call_args_list] == expected_backends
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    assert query_client.close.await_count == int(failure_stage != "container")
    assert seed_client.close.await_count == int(failure_stage not in ("container", "enter"))


@pytest.mark.parametrize("method_name", [
    "test_vector_query_pagination_async", "test_ordering_distances_async",
    "test_vector_query_partitioned_response_hook_async",
    "test_vector_query_cross_partition_response_hook_async",
    "test_wrong_vector_search_queries_async",
    "test_vector_search_environment_variables_async", "test_vector_query_large_data_async",
])
def test_async_vector_pagination_preserves_original_body_and_helper_rust(method_name):
    original = ast.parse((ROOT / "tests" / "test_query_vector_similarity_async.py").read_text(encoding="utf-8"))
    path = ROOT / "tests" / "query_items" / "aio" / "test_query_vector_similarity_async.py"
    copied = ast.parse(path.read_text(encoding="utf-8"))

    def body(tree, name):
        method = next(node for node in ast.walk(tree)
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
        return ast.dump(method.args), [ast.dump(node) for node in method.body]

    assert body(original, method_name) == body(
        copied, method_name + "_rust"
    )
    helper_source = ast.parse(COPY.with_name("test_query_vector_similarity.py").read_text(encoding="utf-8"))
    assert body(original, "verify_ordering") == body(helper_source, "verify_ordering")
    assert any(isinstance(node, ast.ImportFrom)
               and node.module == "query_items.sync.test_query_vector_similarity"
               and any(alias.name == "verify_ordering" for alias in node.names)
               for node in copied.body)


@pytest.mark.parametrize("failure_stage", [None, "container", "item", "enter", "query"])
@pytest.mark.parametrize("method_name,profile_count", [
    ("test_vector_query_pagination_async_rust", 1),
    ("test_ordering_distances_async_rust", 3),
    ("test_vector_query_partitioned_response_hook_async_rust", 1),
    ("test_vector_query_cross_partition_response_hook_async_rust", 1),
    ("test_wrong_vector_search_queries_async_rust", 1),
    ("test_vector_search_environment_variables_async_rust", 1),
])
def test_async_vector_pagination_fixture_preserves_setup_and_cleanup_rust(
    monkeypatch, failure_stage, method_name, profile_count,
):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    path = ROOT / "tests" / "query_items" / "aio" / "test_query_vector_similarity_async.py"
    module = load_module("_async_vector_pagination_copy", path)
    empty_container = method_name in (
        "test_wrong_vector_search_queries_async_rust", "test_vector_search_environment_variables_async_rust",
    )
    expected_failure = None if empty_container and failure_stage == "item" else failure_stage
    setup_client, query_client = MagicMock(), MagicMock()
    query_client.__aenter__ = AsyncMock(return_value=query_client)
    query_client.close = AsyncMock()
    setup_factory = MagicMock(return_value=setup_client)
    query_factory = MagicMock(return_value=query_client)
    monkeypatch.setattr(module, "CosmosSyncClient", setup_factory)
    monkeypatch.setattr(module, "CosmosClient", query_factory)
    database = setup_client.create_database.return_value
    container = database.create_container.return_value
    targets = {
        "container": database.create_container,
        "item": container.create_item,
        "enter": query_client.__aenter__,
    }
    if failure_stage in targets:
        targets[failure_stage].side_effect = RuntimeError(f"{failure_stage} failed")

    async def exercise(case):
        attribute = "created_large_container" if empty_container else "created_quantized_cosine_container"
        assert getattr(case, attribute) is (
            query_client.get_database_client.return_value.get_container_client.return_value
        )
        if failure_stage == "query":
            raise RuntimeError("query failed")

    monkeypatch.setattr(module.TestVectorSimilarityQueryAsync, method_name, exercise)
    case = module.TestVectorSimilarityQueryAsync(method_name)
    result = unittest.TestResult()
    case.run(result)
    assert not result.failures
    assert len(result.errors) == (0 if expected_failure is None else 1)
    if expected_failure is not None:
        assert f"{expected_failure} failed" in result.errors[0][1]
    assert setup_factory.call_args.kwargs["_backend"] == "core-python"
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    if expected_failure not in ("container", "item"):
        assert query_factory.call_args.kwargs["_backend"] == "rust"
        query_client.close.assert_awaited_once()
        assert database.create_container.call_count == profile_count
        assert [call.args[0] for call in container.create_item.call_args_list] == (
            [] if empty_container else module.vector_test_data.get_vector_items() * profile_count
        )
        assert query_client.get_database_client.return_value.get_container_client.call_count == (
            0 if failure_stage == "enter" else profile_count
        )
    for call, index_type, distance in zip(
        database.create_container.call_args_list,
        ("quantizedFlat", "flat", "diskANN"),
        ("cosine", "euclidean", "dotproduct"),
    ):
        options = call.kwargs
        assert options["id"] == index_type
        assert options["partition_key"] == module.PartitionKey(path="/pk")
        assert options["offer_throughput"] == module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS
        assert options["indexing_policy"] == module.test_config.get_vector_indexing_policy(index_type)
        assert options["vector_embedding_policy"] == module.test_config.get_vector_embedding_policy(
            distance, "float32", 2 if empty_container else 128
        )


@pytest.mark.parametrize("scenario", [
    "expected", "alternate-sort-message", "first-success", "first-type", "first-message",
    "second-success", "second-type", "second-status", "second-message",
])
def test_async_vector_rejection_preserves_error_contracts_and_cleanup_rust(monkeypatch, scenario):
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    path = ROOT / "tests" / "query_items" / "aio" / "test_query_vector_similarity_async.py"
    module = load_module("_async_vector_rejection_copy", path)
    setup_client, query_client = MagicMock(), MagicMock()
    query_client.__aenter__ = AsyncMock(return_value=query_client)
    query_client.close = AsyncMock()
    monkeypatch.setattr(module, "CosmosSyncClient", MagicMock(return_value=setup_client))
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=query_client))
    container = query_client.get_database_client.return_value.get_container_client.return_value
    missing_limit = (
        "Executing a vector search query without TOP or LIMIT can consume many RUs very fast and"
        " have long runtimes. Please ensure you are using one of the two filters with your"
        " vector search query."
    )
    sort_message = (
        "Specifying a sorting order (ASC or DESC) with VectorDistance function is not supported."
        if scenario == "alternate-sort-message" else "One of the input values is invalid."
    )
    errors = [
        ValueError(missing_limit),
        module.exceptions.CosmosHttpResponseError(status_code=400, message=sort_message),
    ]
    if scenario.endswith("-success"):
        errors[0 if scenario.startswith("first-") else 1] = None
    elif scenario.endswith("-type"):
        errors[0 if scenario.startswith("first-") else 1] = RuntimeError("unexpected error type")
    elif scenario == "first-message":
        errors[0] = ValueError("wrong validation message")
    elif scenario == "second-status":
        errors[1] = module.exceptions.CosmosHttpResponseError(status_code=500, message=sort_message)
    elif scenario == "second-message":
        errors[1] = module.exceptions.CosmosHttpResponseError(status_code=400, message="wrong service message")
    queries = []

    def query(**kwargs):
        assert set(kwargs) == {"query"}
        sql = kwargs["query"]
        assert "SELECT c.text, VectorDistance(" in sql
        assert "TOP " not in sql and "LIMIT " not in sql
        assert sql.endswith(" ASC") == bool(queries)
        error = errors[len(queries)]
        queries.append(sql)

        async def rows():
            if error is not None:
                raise error
            yield None

        return rows()

    container.query_items.side_effect = query
    case = module.TestVectorSimilarityQueryAsync("test_wrong_vector_search_queries_async_rust")
    result = unittest.TestResult()
    case.run(result)
    assert len(result.failures) == int(scenario in ("first-message", "second-status", "second-message"))
    assert len(result.errors) == int(scenario.endswith(("-success", "-type")))
    assert len(queries) == (1 if scenario.startswith("first-") else 2)
    setup_client.create_database.return_value.create_container.return_value.create_item.assert_not_called()
    setup_client.delete_database.assert_called_once_with(case.database_id)
    setup_client.close.assert_called_once()
    query_client.close.assert_awaited_once()


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
        ROOT / "tests" / "query_items" / surface / f"test_query_feed_range_multipartition{suffix}.py",
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
        ROOT / "tests" / "query_items" / "aio" / "test_query_feed_range_async.py",
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
    path = ROOT / "tests" / "query_items" / surface / f"test_query_feed_range_discovery{suffix}.py"
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
    config = ast.parse((ROOT / "tests" / "config" / "settings.py").read_text(encoding="utf-8"))
    config_class = next(node for node in config.body if isinstance(node, ast.ClassDef) and node.name == "TestSettings")
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
    path = ROOT / "tests" / "query_items" / surface / f"test_query_feed_range_discovery{suffix}.py"
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
