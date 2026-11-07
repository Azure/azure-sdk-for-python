# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Protect shared settings, Rust provisioning, and the legacy-retirement boundary."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from azure.cosmos import exceptions
from config import clients, resources
from config.settings import TestSettings, unique_database_id


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("auth", ["key", "aad"])
@pytest.mark.parametrize("endpoint", [None, "https://regional.example.invalid/"])
def test_client_factory_selects_rust_and_preserves_auth_rust(monkeypatch, async_mode, auth, endpoint):
    settings = SimpleNamespace(
        host="https://account.example.invalid/", masterKey="test-key", data_auth_mode=auth, is_emulator=False
    )
    credential = object()
    credential_factory = Mock(return_value=credential)
    monkeypatch.setattr(clients, "_aad_credential", credential_factory)
    constructor = Mock()
    monkeypatch.setattr(clients, "AsyncCosmosClient" if async_mode else "CosmosClient", constructor)
    factory = clients.create_data_client_async_for_endpoint if async_mode else clients.create_data_client_for_endpoint
    result = factory(endpoint, settings=settings, no_response_on_write=True)
    constructor.assert_called_once_with(
        endpoint or settings.host,
        credential if auth == "aad" else "test-key",
        no_response_on_write=True,
        _backend="rust",
    )
    assert result is constructor.return_value
    result.create_database.assert_not_called()
    if auth == "aad":
        credential_factory.assert_called_once_with(async_mode)
    else:
        credential_factory.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
def test_emulator_aad_mode_keeps_existing_key_behavior_rust(monkeypatch, async_mode):
    settings = SimpleNamespace(host="local", masterKey="test-key", data_auth_mode="aad", is_emulator=True)
    credentials = Mock(side_effect=AssertionError("must not acquire an AAD credential"))
    monkeypatch.setattr(clients, "_aad_credential", credentials)
    constructor = Mock()
    monkeypatch.setattr(clients, "AsyncCosmosClient" if async_mode else "CosmosClient", constructor)
    factory = clients.create_data_client_async if async_mode else clients.create_data_client
    factory(settings=settings)
    constructor.assert_called_once_with("local", "test-key", _backend="rust")


def test_setup_uses_key_auth_and_never_falls_back_rust(monkeypatch):
    constructor = Mock(side_effect=RuntimeError("Rust unavailable"))
    monkeypatch.setattr(clients, "CosmosClient", constructor)
    settings = SimpleNamespace(host="local", masterKey="test-key", data_auth_mode="aad")
    with pytest.raises(RuntimeError, match="Rust unavailable"):
        clients.create_setup_client(settings=settings)
    constructor.assert_called_once_with("local", "test-key", _backend="rust")


def test_explicit_local_comparison_selection_is_forwarded_rust(monkeypatch):
    constructor = Mock()
    monkeypatch.setattr(clients, "CosmosClient", constructor)
    clients.create_data_client(_backend="core-python")
    assert constructor.call_args.kwargs["_backend"] == "core-python"


def test_invalid_authentication_mode_is_not_silently_key_auth_rust():
    settings = SimpleNamespace(data_auth_mode="unknown")
    with pytest.raises(ValueError, match="Unknown COSMOS_TEST_DATA_AUTH_MODE"):
        clients.create_data_client_for_endpoint("local", settings=settings)


def test_legacy_config_inherits_one_set_of_resource_identifiers_rust():
    import test_config

    assert issubclass(test_config.TestConfig, TestSettings)
    for name in (
        "TEST_DATABASE_ID", "TEST_SINGLE_PARTITION_CONTAINER_ID", "TEST_MULTI_PARTITION_CONTAINER_ID",
        "TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID", "TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID",
        "TEST_CONTAINER_PREFIX_PARTITION_KEY_PATH",
    ):
        assert name not in test_config.TestConfig.__dict__
        assert getattr(test_config.TestConfig, name) is getattr(TestSettings, name)
    assert test_config.unique_database_id is unique_database_id
    assert unique_database_id("one") != unique_database_id("one")


@pytest.mark.parametrize("helper,id_name,throughput_name,paths", [
    ("create_single_partition_container_if_not_exist", "TEST_SINGLE_PARTITION_CONTAINER_ID",
     "THROUGHPUT_FOR_1_PARTITION", ["/pk"]),
    ("create_multi_partition_container_if_not_exist", "TEST_MULTI_PARTITION_CONTAINER_ID",
     "THROUGHPUT_FOR_5_PARTITIONS", ["/pk"]),
    ("create_single_partition_prefix_pk_container_if_not_exist", "TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID",
     "THROUGHPUT_FOR_1_PARTITION", ["/pk1", "/pk2"]),
    ("create_multi_partition_prefix_pk_container_if_not_exist", "TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID",
     "THROUGHPUT_FOR_5_PARTITIONS", ["/pk1", "/pk2"]),
])
def test_resource_helpers_use_supplied_client_and_shared_settings_rust(helper, id_name, throughput_name, paths):
    client = Mock()
    result = getattr(resources, helper)(client)
    client.create_database_if_not_exists.assert_called_once_with(
        TestSettings.TEST_DATABASE_ID, offer_throughput=TestSettings.THROUGHPUT_FOR_1_PARTITION
    )
    create = client.create_database_if_not_exists.return_value.create_container_if_not_exists
    assert create.call_args.kwargs["id"] == getattr(TestSettings, id_name)
    assert create.call_args.kwargs["offer_throughput"] == getattr(TestSettings, throughput_name)
    assert create.call_args.kwargs["partition_key"]["paths"] == paths
    assert result is create.return_value


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409])
def test_setup_retries_do_not_hide_permanent_errors_rust(monkeypatch, status):
    error = exceptions.CosmosHttpResponseError(status_code=status, message="test")
    operation = Mock(side_effect=error)
    sleep = Mock()
    monkeypatch.setattr(resources.time, "sleep", sleep)
    with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
        resources.retry_control_plane(operation)
    assert caught.value is error
    operation.assert_called_once_with()
    sleep.assert_not_called()


def test_transient_setup_retry_is_bounded_rust(monkeypatch):
    error = exceptions.CosmosHttpResponseError(status_code=429, message="test")
    monkeypatch.setattr(resources, "CONTROL_PLANE_MAX_ATTEMPTS", 3)
    sleep = Mock()
    monkeypatch.setattr(resources.time, "sleep", sleep)
    operation = Mock(side_effect=error)
    with pytest.raises(exceptions.CosmosHttpResponseError):
        resources.retry_control_plane(operation)
    assert operation.call_count == 3
    assert sleep.call_count == 2


@pytest.mark.parametrize("status", [404, 403])
def test_cleanup_ignores_only_already_deleted_database_rust(status):
    client = Mock()
    client.delete_database.side_effect = exceptions.CosmosHttpResponseError(status_code=status, message="test")
    if status == 404:
        resources.try_delete_database_with_id(client, "owned-db")
    else:
        with pytest.raises(exceptions.CosmosHttpResponseError):
            resources.try_delete_database_with_id(client, "owned-db")
    client.delete_database.assert_called_once_with("owned-db")


@pytest.fixture
def setup_module_under_test():
    spec = importlib.util.spec_from_file_location("_configuration_setup", ROOT / "tests" / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("failure", [None, "database", "container", "cleanup"])
def test_setup_cleanup_closes_client_even_after_partial_failure_rust(monkeypatch, setup_module_under_test, failure):
    setup = setup_module_under_test
    client = Mock()
    monkeypatch.setattr(setup.clients, "create_setup_client", Mock(return_value=client))
    owned = Mock()
    monkeypatch.setattr(setup, "resources", owned)
    session = SimpleNamespace(
        config=SimpleNamespace(option=SimpleNamespace(collectonly=False, continue_on_collection_errors=False)),
        testsfailed=0, items=[SimpleNamespace(path=Path("test_live.py"))],
    )
    if failure in ("database", "container"):
        failing_call = (
            owned.create_database_if_not_exist if failure == "database"
            else owned.create_multi_partition_container_if_not_exist
        )
        failing_call.side_effect = RuntimeError(f"{failure} failed")
        with pytest.raises(RuntimeError, match=f"{failure} failed"):
            setup.pytest_collection_finish(session)
    else:
        setup.pytest_collection_finish(session)
    setup.clients.create_setup_client.assert_called_once_with()
    assert setup._live_resources_initialized is (failure != "database")
    if failure == "cleanup":
        owned.try_delete_database.side_effect = RuntimeError("cleanup failed")
        with pytest.raises(RuntimeError, match="cleanup failed"):
            setup.pytest_sessionfinish(session, 1)
    else:
        setup.pytest_sessionfinish(session, 0)
    if failure == "database":
        owned.try_delete_database.assert_not_called()
    else:
        owned.try_delete_database.assert_called_once_with(client)
    client.close.assert_called_once_with()
    assert setup.cosmos_sync_client is None
    assert not setup._live_resources_initialized
    setup.pytest_unconfigure(None)
    client.close.assert_called_once_with()


@pytest.mark.parametrize("include_legacy", [False, True])
def test_legacy_account_lookup_only_runs_for_selected_originals_rust(
    monkeypatch, setup_module_under_test, include_legacy,
):
    legacy = SimpleNamespace(TestConfig=object(), initialize_legacy_account_info=Mock())
    monkeypatch.setitem(sys.modules, "test_config", legacy)
    selected = SimpleNamespace(module=SimpleNamespace())
    session = SimpleNamespace(
        items=[selected],
        config=SimpleNamespace(option=SimpleNamespace(include_legacy_tests=include_legacy)),
    )
    setup_module_under_test._initialize_legacy_account_info(session)
    legacy.initialize_legacy_account_info.assert_not_called()
    selected.module.test_config = legacy
    setup_module_under_test._initialize_legacy_account_info(session)
    if include_legacy:
        legacy.initialize_legacy_account_info.assert_called_once_with()
    else:
        legacy.initialize_legacy_account_info.assert_not_called()


def test_legacy_resource_methods_delegate_with_legacy_overrides_rust(monkeypatch):
    import test_config

    class LocalConfig(test_config.TestConfig):
        TEST_DATABASE_ID = "owned-override"

    create = Mock()
    monkeypatch.setattr(resources, "create_database_if_not_exist", create)
    client = object()
    LocalConfig.create_database_if_not_exist(client)
    create.assert_called_once_with(client, settings=LocalConfig)


def test_settings_import_does_not_load_sdk_or_create_credentials_rust(tmp_path):
    code = """
import sys
from config.settings import TestSettings
assert 'azure.cosmos' not in sys.modules
assert 'devtools_testutils.azure_recorded_testcase' not in sys.modules
assert 'test_config' not in sys.modules
assert TestSettings.TEST_DATABASE_ID
"""
    environment = dict(os.environ, PYTHONPATH=str(ROOT / "tests"))
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, env=environment,
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("selections,blocked", [
    ([
        "tests/create_item", "tests/execute_item_batch", "tests/from_connection_string",
        "tests/get_database_client", "tests/list_databases", "tests/query_databases",
        "tests/query_items", "tests/response_hook",
    ], ("test_config",)),
    (["tests/fault_injection", "tests/toxiproxy"], (
        "test_config", "_client_transport", "_fault_injection_transport",
        "common.fault_resources",
    )),
])
def test_maintained_copies_collect_without_legacy_configuration_rust(tmp_path, selections, blocked):
    code = f"""
import importlib.abc
import sys

class BlockLegacyConfig(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {blocked!r}:
            raise AssertionError('Maintained tests imported legacy infrastructure: ' + fullname)

sys.meta_path.insert(0, BlockLegacyConfig())
import pytest
result = pytest.main([
    '--collect-only', '-q', '-p', 'no:cacheprovider',
    *{selections!r},
])
assert not set({blocked!r}).intersection(sys.modules)
raise SystemExit(result)
"""
    environment = dict(os.environ, PYTHONPATH=str(ROOT / "tests") + os.pathsep + str(ROOT))
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, env=environment,
        capture_output=True, text=True, timeout=90, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
