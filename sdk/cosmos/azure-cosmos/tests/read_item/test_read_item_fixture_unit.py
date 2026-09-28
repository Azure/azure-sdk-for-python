# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned read-test fixtures must clean up even when setup or assertions fail."""

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("surface,filename,classname,method", [
    ("sync", "test_crud.py", "TestCRUDOperations", "test_get_resource_with_dictionary_and_object"),
    ("aio", "test_crud_async.py", "TestCRUDOperationsAsync", "test_get_resource_with_dictionary_and_object_async"),
])
def test_copied_dictionary_read_statements_match_original(surface, filename, classname, method):
    def statements(path):
        module = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == classname)
        function = next(node for node in cls.body if getattr(node, "name", None) == method)
        start = next(
            index for index, node in enumerate(function.body)
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "created_item"
        )
        return function.body[start:]

    copied = statements(ROOT / "tests" / "read_item" / surface / "legacy" / filename)
    original = statements(ROOT / "tests" / filename)[:len(copied)]
    assert [ast.dump(node) for node in copied] == [ast.dump(node) for node in original]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_imports_checkout_in_fresh_process():
    script = ROOT / "scripts" / "v5" / "run_read_item_parity.py"
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import inspect, runpy, sys; "
            "namespace = runpy.run_path(sys.argv[1]); "
            "print(inspect.getfile(namespace['CosmosClient']))",
            str(script),
        ],
        cwd=ROOT.parent, capture_output=True, text=True, check=True, timeout=30,
    )
    assert Path(result.stdout.strip()).resolve() == ROOT / "azure" / "cosmos" / "cosmos_client.py"


@pytest.mark.parametrize(
    "failure", [None, "database", "container", "assertion", "delete", "close", "assertion_and_delete"],
)
def test_rust_fixture_cleanup(monkeypatch, failure):
    module = _load(
        "owned_read_fixture",
        ROOT / "tests" / "read_item" / "sync" / "legacy" / "test_none_options.py",
    )
    events = []
    client = MagicMock()
    database = client.create_database.return_value
    container = database.create_container.return_value
    container.read_item.side_effect = lambda item, **kwargs: {"id": item}

    def delete(database_id):
        events.append("delete")
        if failure in ("delete", "assertion_and_delete"):
            raise RuntimeError("delete failed")

    def close():
        events.append("close")
        if failure == "close":
            raise RuntimeError("close failed")

    client.delete_database.side_effect = delete
    client.close.side_effect = close
    if failure == "database":
        client.create_database.side_effect = RuntimeError("database failed")
    if failure == "container":
        database.create_container.side_effect = RuntimeError("container failed")
    if failure in ("assertion", "assertion_and_delete"):
        container.read_item.side_effect = lambda *args, **kwargs: {"id": "wrong"}
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = module.TestNoneOptions("test_container_read_item_none_options")
    result = unittest.TestResult()
    case.run(result)

    assert result.testsRun == 1
    assert result.wasSuccessful() is (failure is None)
    assert events == (["close"] if failure == "database" else ["delete", "close"])
    if failure != "database":
        client.delete_database.assert_called_once_with(case._db_id)
    if failure in ("assertion", "assertion_and_delete"):
        assert len(result.failures) == 1
    if failure in ("delete", "assertion_and_delete"):
        assert len(result.errors) == 1
        assert "delete failed" in result.errors[0][1]


@pytest.mark.parametrize("data_client_fails", [False, True])
def test_original_fixture_closes_acquired_clients(monkeypatch, data_client_fails):
    module = _load("original_read_fixture", ROOT / "tests" / "test_none_options.py")
    key_client, data_client = MagicMock(), MagicMock()
    monkeypatch.setattr(module.cosmos_client, "CosmosClient", MagicMock(return_value=key_client))
    factory = MagicMock(return_value=data_client)
    if data_client_fails:
        factory.side_effect = RuntimeError("data client failed")
    monkeypatch.setattr(module.test_config.TestConfig, "create_data_client", factory)
    case = module.TestNoneOptions("test_container_read_item_none_options")
    try:
        if data_client_fails:
            with pytest.raises(RuntimeError, match="data client failed"):
                case.setUp()
        else:
            case.setUp()
    finally:
        case.doCleanups()
    key_client.close.assert_called_once()
    assert data_client.close.call_count == (0 if data_client_fails else 1)


@pytest.mark.parametrize("filename,classname,method", [
    ("test_headers.py", "TestHeadersAsync", "test_container_read_item_throughput_bucket_async"),
    ("test_none_options.py", "TestNoneOptionsAsync", "test_container_read_item_none_options_async"),
])
@pytest.mark.parametrize("failure", [None, "database", "container", "delete"])
def test_async_read_fixture_cleanup(monkeypatch, filename, classname, method, failure):
    module = _load("async_owned_read_fixture", ROOT / "tests" / "read_item" / "aio" / "legacy" / filename)
    events = []
    client, database, container = MagicMock(), MagicMock(), MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.create_database = AsyncMock(return_value=database)
    database.create_container = AsyncMock(return_value=container)
    container.create_item = AsyncMock(side_effect=lambda body, **kwargs: body)
    container.read_item = AsyncMock(side_effect=lambda item, **kwargs: {"id": item})

    async def delete(database_id):
        events.append("delete")
        if failure == "delete":
            raise RuntimeError("delete failed")

    async def close():
        events.append("close")

    client.delete_database = AsyncMock(side_effect=delete)
    client.close = AsyncMock(side_effect=close)
    if failure == "database":
        client.create_database.side_effect = RuntimeError("database failed")
    if failure == "container":
        database.create_container.side_effect = RuntimeError("container failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = getattr(module, classname)(method)
    result = unittest.TestResult()
    case.run(result)
    assert result.wasSuccessful() is (failure is None)
    assert events == (["close"] if failure == "database" else ["delete", "close"])
    if failure == "delete":
        assert "delete failed" in result.errors[0][1]


@pytest.mark.parametrize("failure", [None, "database", "container", "pytest", "pytest_error", "delete"])
def test_runner_owns_original_resources(monkeypatch, failure):
    monkeypatch.setattr(sys, "path", list(sys.path))
    runner = _load("read_parity_runner", ROOT / "scripts" / "v5" / "run_read_item_parity.py")
    import test_config

    config = test_config.TestConfig
    previous_ids = (config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID)
    client = MagicMock()
    client.__enter__.return_value = client
    monkeypatch.setattr(runner, "CosmosClient", MagicMock(return_value=client))
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    # main mutates process configuration; monkeypatch restores it after this test.
    for name in ("COSMOS_BACKEND", "COSMOS_TEST_DATA_AUTH_MODE", "COSMOS_PARITY_CAPTURE_OP"):
        monkeypatch.setenv(name, "before")
    monkeypatch.chdir(ROOT)
    seen = []

    def execute(options):
        assert "--noconftest" in options
        assert "common.parity_capture_plugin" in options
        assert options[-1] == str(ROOT / "tests" / "test_none_options.py") + runner.METHOD
        assert config.TEST_DATABASE_ID.startswith("read_parity_core_")
        assert config.TEST_DATABASE_ID != previous_ids[0]
        assert config.TEST_SINGLE_PARTITION_CONTAINER_ID == "orders"
        seen.append(config.TEST_DATABASE_ID)
        if failure == "pytest_error":
            raise RuntimeError("pytest_error failed")
        return 1 if failure == "pytest" else 0

    monkeypatch.setattr(runner.pytest, "main", execute)
    if failure == "database":
        client.create_database.side_effect = RuntimeError("database failed")
    if failure == "container":
        client.create_database.return_value.create_container.side_effect = RuntimeError("container failed")
    if failure == "delete":
        client.delete_database.side_effect = RuntimeError("delete failed")
    if failure in ("database", "container", "pytest_error", "delete"):
        with pytest.raises(RuntimeError, match=f"{failure} failed"):
            runner.main(["--backend", "core-python"])
    else:
        assert runner.main(["--backend", "core-python"]) == (1 if failure == "pytest" else 0)

    owned_id = client.create_database.call_args.args[0]
    assert owned_id != previous_ids[0]
    if failure == "database":
        client.delete_database.assert_not_called()
    else:
        client.delete_database.assert_called_once_with(owned_id)
    client.__exit__.assert_called_once()
    assert (config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID) == previous_ids
    assert len(seen) == (0 if failure in ("database", "container") else 1)
