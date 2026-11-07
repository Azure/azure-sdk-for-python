# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline preservation and owned-fixture checks for the hybrid-search query copies."""

import ast
import copy
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]
ENV_NAME = "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS"
METHODS = {
    "hybrid-rejection": "test_wrong_hybrid_search_queries",
    "hybrid-buffer": "test_hybrid_search_env_variables",
    "hybrid-queries": "test_hybrid_search_queries",
    "hybrid-pagination": "test_hybrid_search_query_pagination",
    "hybrid-cross-hook": "test_hybrid_search_cross_partition_query_response_hook",
    "hybrid-partition-hook": "test_hybrid_search_partitioned_query_response_hook",
    "hybrid-weighted-rrf": "test_hybrid_search_weighted_reciprocal_rank_fusion",
    "hybrid-weighted-rejection": "test_invalid_hybrid_search_queries_weighted_reciprocal_rank_fusion",
    "hybrid-weighted-equivalence": "test_weighted_vs_non_weighted_reciprocal_rank_fusion",
    "hybrid-weight-count": "test_weighted_reciprocal_rank_fusion_with_missing_or_extra_weights",
    "hybrid-weighted-hook": "test_weighted_reciprocal_rank_fusion_with_response_hook",
    "hybrid-parameters": "test_hybrid_search_query_with_params_equivalence",
    "hybrid-weighted-parameters-hook": "test_weighted_rrf_hybrid_search_with_params_and_response_hook",
    "hybrid-vector-parameters": "test_hybrid_and_non_hybrid_param_queries_equivalence",
    "hybrid-global-scope": "test_hybrid_search_with_full_text_score_scope_global",
    "hybrid-local-scope": "test_hybrid_search_with_full_text_score_scope_local",
    "hybrid-local-partition": "test_hybrid_search_with_full_text_score_scope_local_partition_key",
    "hybrid-invalid-scope": "test_hybrid_search_with_invalid_full_text_score_scope",
    "hybrid-rrf-local-scope": "test_hybrid_search_rrf_with_full_text_score_scope_local",
    "hybrid-scope-equivalence": "test_hybrid_search_local_vs_global_scope_both_return_results",
    "hybrid-weighted-local-scope": "test_weighted_rrf_with_full_text_score_scope_local",
    "hybrid-parameters-scope": "test_hybrid_search_parameterized_with_full_text_score_scope",
}


def _paths(surface):
    suffix = "_async" if surface == "aio" else ""
    filename = f"test_query_hybrid_search{suffix}.py"
    return ROOT / "tests" / filename, ROOT / "tests" / "query_items" / surface / filename


def _class_name(surface):
    return "TestFullTextHybridSearchQuery" + ("Async" if surface == "aio" else "")


def _load(path):
    spec = importlib.util.spec_from_file_location("_hybrid_unit_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tree_class(text):
    tree = ast.parse(text)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    return tree, cls


def _methods(cls):
    return {
        node.name: node for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    }


def _raw_method(text, method):
    start = min([method.lineno] + [node.lineno for node in method.decorator_list])
    return "".join(text.splitlines(keepends=True)[start - 1:method.end_lineno])


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_every_original_method_and_marker_is_preserved(surface):
    original, copied = _paths(surface)
    original_text, copied_text = [path.read_text(encoding="utf-8") for path in (original, copied)]
    original_tree, original_class = _tree_class(original_text)
    copied_tree, copied_class = _tree_class(copied_text)
    original_methods, copied_methods = _methods(original_class), _methods(copied_class)
    assert len(original_methods) == len(copied_methods) == 22
    assert list(copied_methods) == [name + "_rust" for name in original_methods]
    for name, original_method in original_methods.items():
        copied_method = copied_methods[name + "_rust"]
        normalized = copy.deepcopy(copied_method)
        normalized.name = name
        assert ast.dump(normalized) == ast.dump(original_method)
        assert _raw_method(copied_text, copied_method).replace(
            f"def {name}_rust(", f"def {name}(", 1
        ) == _raw_method(original_text, original_method)
    assert [ast.dump(node) for node in copied_class.decorator_list] == [
        ast.dump(node) for node in original_class.decorator_list
    ]
    assert [ast.unparse(node) for node in original_class.decorator_list] == [
        "pytest.mark.cosmosAADQuery", "pytest.mark.cosmosSearchQuery"
    ]
    for tree in (original_tree, copied_tree):
        assert not [
            node for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(isinstance(child, ast.Name) and child.id == "pytestmark" for child in ast.walk(node))
        ]
    assert all(not method.decorator_list for method in original_methods.values())
    assert not any(
        isinstance(node, ast.Import) and any(alias.name == "test_config" for alias in node.names)
        for node in copied_tree.body
    )


def _original_policy_helpers():
    tree = ast.parse((ROOT / "tests" / "test_config.py").read_text(encoding="utf-8"))
    names = {"get_full_text_indexing_policy", "get_full_text_policy"}
    helpers = ast.Module(body=[
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names
    ], type_ignores=[])
    namespace = {}
    exec(compile(helpers, "<original-full-text-policies>", "exec"), namespace)
    return SimpleNamespace(**{name: namespace[name] for name in names})


@pytest.mark.parametrize("name", ["get_full_text_indexing_policy", "get_full_text_policy"])
def test_shared_full_text_policy_helpers_match_original(name):
    from common import _test_helpers

    assert getattr(_test_helpers, name)("/text") == getattr(_original_policy_helpers(), name)("/text")


def _class_fixture(monkeypatch, surface):
    module = _load(_paths(surface)[1])
    cls = type("OwnedHybridFixture", (getattr(module, _class_name(surface)),), {})
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    # Isolate lifecycle tests from helper availability, checked separately above.
    monkeypatch.setattr(module, "test_config", _original_policy_helpers())
    key_client, query_client = MagicMock(), MagicMock()
    key_container = key_client.create_database.return_value.create_container.return_value
    query_container = query_client.get_database_client.return_value.get_container_client.return_value
    events = []
    key_client.close.side_effect = lambda: events.append("key-close")
    query_client.close.side_effect = lambda: events.append("query-close")
    key_client.delete_database.side_effect = lambda *_: events.append("delete")
    factory = MagicMock(side_effect=[key_client, query_client])
    if surface == "sync":
        monkeypatch.setattr(module.cosmos_client, "CosmosClient", factory)
    else:
        monkeypatch.setattr(module, "CosmosSyncClient", factory)
    return SimpleNamespace(
        module=module, cls=cls, key=key_client, query=query_client,
        container=key_container, query_container=query_container, factory=factory, events=events,
    )


@pytest.mark.parametrize("surface", ["sync", "aio"])
@pytest.mark.parametrize("stage", [None, "database", "container", "seed"])
def test_class_setup_uses_original_data_policies_and_cleans_after_failure(monkeypatch, capsys, surface, stage):
    fixture = _class_fixture(monkeypatch, surface)
    stages = {
        "database": fixture.key.create_database,
        "container": fixture.key.create_database.return_value.create_container,
        "seed": fixture.container.create_item,
    }
    if stage:
        stages[stage].side_effect = RuntimeError("setup failed")
    try:
        if stage:
            with pytest.raises(RuntimeError, match="setup failed"):
                fixture.cls.setUpClass()
        else:
            fixture.cls.setUpClass()
            data = fixture.module.hybrid_search_data.get_hybrid_search_items()
            expected = data.get("items")
            for index, item in enumerate(expected):
                item["id"] = str(index)
                item["pk"] = str((index % 2) + 1)
            assert [call.args[0] for call in fixture.container.create_item.call_args_list] == expected
            create = fixture.key.create_database.return_value.create_container
            options = create.call_args.kwargs
            assert set(options) == {
                "id", "partition_key", "offer_throughput", "indexing_policy", "full_text_policy"
            }
            assert options["partition_key"]["paths"] == ["/pk"]
            assert options["offer_throughput"] == fixture.module.settings.TestSettings.THROUGHPUT_FOR_2_PARTITIONS == 12000
            assert options["indexing_policy"] == _original_policy_helpers().get_full_text_indexing_policy("/text")
            assert options["full_text_policy"] == _original_policy_helpers().get_full_text_policy("/text")
            if surface == "sync":
                assert fixture.cls.test_container.read_item is fixture.container.read_item
                assert fixture.cls.test_container.query_items is fixture.query_container.query_items
                fixture.cls.test_container.read_item("50", "1")
                fixture.container.read_item.assert_called_once_with("50", "1")
    finally:
        fixture.cls.doClassCleanups()
    assert not fixture.cls.tearDown_exceptions
    assert fixture.factory.call_args_list[0].kwargs["_backend"] == "core-python"
    fixture.key.close.assert_called_once()
    if stage == "database":
        fixture.key.delete_database.assert_not_called()
    else:
        fixture.key.delete_database.assert_called_once_with(fixture.cls.database_id)
        assert fixture.events[-2:] == ["delete", "key-close"]
        output = capsys.readouterr().out
        assert f"database: {fixture.cls.database_id}" in output
        assert "Deleted owned" in output
    if surface == "sync" and stage is None:
        assert fixture.factory.call_args_list[1].kwargs["_backend"] == "rust"
        fixture.query.close.assert_called_once()
        assert fixture.events == ["query-close", "delete", "key-close"]


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_cleanup_error_is_not_silenced_and_setup_client_still_closes(monkeypatch, capsys, surface):
    fixture = _class_fixture(monkeypatch, surface)
    fixture.key.delete_database.side_effect = RuntimeError("delete failed")
    fixture.cls.setUpClass()
    fixture.cls.doClassCleanups()
    assert len(fixture.cls.tearDown_exceptions) == 1
    assert str(fixture.cls.tearDown_exceptions[0][1]) == "delete failed"
    fixture.key.close.assert_called_once()
    assert "Deleted owned" not in capsys.readouterr().out


def test_query_client_setup_failure_still_deletes_owned_database(monkeypatch):
    fixture = _class_fixture(monkeypatch, "sync")
    fixture.query.get_database_client.side_effect = RuntimeError("query setup failed")
    try:
        with pytest.raises(RuntimeError, match="query setup failed"):
            fixture.cls.setUpClass()
    finally:
        fixture.cls.doClassCleanups()
    assert not fixture.cls.tearDown_exceptions
    assert fixture.events == ["query-close", "delete", "key-close"]


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_class_resource_is_reused_for_multiple_test_methods(monkeypatch, surface):
    fixture = _class_fixture(monkeypatch, surface)
    fixture.cls.test_first = lambda self: None
    fixture.cls.test_second = lambda self: None
    if surface == "aio":
        async def no_async_setup(self):
            pass
        fixture.cls.asyncSetUp = no_async_setup
    result = unittest.TestResult()
    unittest.TestSuite([fixture.cls("test_first"), fixture.cls("test_second")]).run(result)
    assert result.testsRun == 2 and result.wasSuccessful()
    fixture.key.create_database.assert_called_once()
    fixture.key.create_database.return_value.create_container.assert_called_once()
    fixture.key.delete_database.assert_called_once()
    fixture.key.close.assert_called_once()


def _async_client():
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.close = AsyncMock()
    client.get_database_client.return_value.get_container_client.return_value.read_item = AsyncMock(
        return_value={"vector": [1, 2, 3]}
    )
    return client


@pytest.mark.parametrize("failure", [None, "query-enter", "lookup-enter", "lookup-container"])
def test_async_lookups_are_awaited_core_python_and_clients_always_close(monkeypatch, failure):
    module = _load(_paths("aio")[1])
    cls = getattr(module, _class_name("aio"))
    case = cls("test_hybrid_search_queries_async_rust")
    case.database_id, case.TEST_CONTAINER_ID = "owned-db", "owned-container"
    query, lookup = _async_client(), _async_client()
    factory = MagicMock(side_effect=[query, lookup])
    monkeypatch.setattr(module, "CosmosClient", factory)
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    if failure == "query-enter":
        query.__aenter__.side_effect = RuntimeError("query-enter")
    elif failure == "lookup-enter":
        lookup.__aenter__.side_effect = RuntimeError("lookup-enter")
    elif failure == "lookup-container":
        lookup.get_database_client.side_effect = RuntimeError("lookup-container")
    query_container = query.get_database_client.return_value.get_container_client.return_value
    original_read = query_container.read_item
    async def exercise():
        assert await case.test_container.read_item("50", "1") == {"vector": [1, 2, 3]}
        lookup_container = lookup.get_database_client.return_value.get_container_client.return_value
        lookup_container.read_item.assert_awaited_once_with("50", "1")
        original_read.assert_not_called()
        assert case.test_container.query_items is query_container.query_items

    setattr(case, case._testMethodName, exercise)
    result = unittest.TestResult()
    case.run(result)
    if failure:
        assert len(result.errors) == 1
        assert f"RuntimeError: {failure}" in result.errors[0][1]
        assert not result.failures
    else:
        assert result.wasSuccessful(), result.errors + result.failures
    assert [call.kwargs["_backend"] for call in factory.call_args_list] == (
        ["rust"] if failure == "query-enter" else ["rust", "core-python"]
    )
    assert query_container.read_item is original_read
    query.close.assert_awaited_once()
    if failure != "query-enter":
        lookup.close.assert_awaited_once()


@pytest.mark.parametrize("surface", ["sync", "aio"])
@pytest.mark.parametrize("previous", [None, "", "73"])
@pytest.mark.parametrize("failure", [False, True])
def test_original_env_test_restores_exact_prior_value_even_on_failure(monkeypatch, surface, previous, failure):
    module = _load(_paths(surface)[1])
    cls = getattr(module, _class_name(surface))
    method = "test_hybrid_search_env_variables" + ("_async" if surface == "aio" else "") + "_rust"
    case = cls(method)
    if previous is None:
        monkeypatch.delenv(ENV_NAME, raising=False)
    else:
        monkeypatch.setenv(ENV_NAME, previous)
    case.test_container = MagicMock()
    case.test_container.query_items.side_effect = RuntimeError("query failed") if failure else ValueError(
        "Executing a hybrid search query with more items than the max is not allowed. "
        "Please ensure you are using a limit smaller than the max, or change the max."
    )
    def check_original_finally():
        assert os.environ[ENV_NAME] == "1000"

    original_setup = case.setUp
    def setup():
        original_setup()
        case.addCleanup(check_original_finally)

    case.setUp = setup
    if surface == "aio":
        case.asyncSetUp = AsyncMock()
    result = unittest.TestResult()
    case.run(result)
    if failure:
        assert len(result.errors) == 1
        assert "RuntimeError: query failed" in result.errors[0][1]
        assert not result.failures
    else:
        assert result.wasSuccessful(), result.errors + result.failures
    assert os.environ.get(ENV_NAME) == previous
    assert (ENV_NAME in os.environ) == (previous is not None)


def test_pytest_collection_retains_original_markers_without_running_fixtures(monkeypatch):
    import azure.cosmos
    import azure.cosmos.cosmos_client as cosmos_client
    import azure.cosmos.aio as cosmos_aio

    forbidden = MagicMock(side_effect=AssertionError("collection must not create clients"))
    monkeypatch.setattr(azure.cosmos, "CosmosClient", forbidden)
    monkeypatch.setattr(cosmos_client, "CosmosClient", forbidden)
    monkeypatch.setattr(cosmos_aio, "CosmosClient", forbidden)
    collected = []

    class Collector:
        def pytest_collection_modifyitems(self, items):
            collected.extend((item.name, sorted(mark.name for mark in item.iter_markers())) for item in items)

    result = pytest.main([
        "--collect-only", "--noconftest", "--import-mode=importlib",
        "-p", "no:cacheprovider", "-q",
        str(_paths("sync")[1]), str(_paths("aio")[1]),
    ], plugins=[Collector()])
    assert result == 0
    assert len(collected) == 44
    assert all(markers == ["cosmosAADQuery", "cosmosSearchQuery"] for _, markers in collected)
    forbidden.assert_not_called()
