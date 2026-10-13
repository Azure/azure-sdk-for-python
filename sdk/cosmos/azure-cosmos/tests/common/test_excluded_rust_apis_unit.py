# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Removed APIs stay absent; Rust-only exclusions leave legacy behavior intact."""
import asyncio
import importlib
import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.scripts import ScriptsProxy
from azure.cosmos.aio._scripts import ScriptsProxy as AsyncScriptsProxy
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._backend.client_config import build_client_config
from azure.cosmos._backend.request_settings import ItemSettings, ResourceSettings
from azure.cosmos._availability_strategy_config import CrossRegionHedgingStrategy
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings
from common.test_connection_free_items_unit import Backend, AsyncBackend


def finish(result):
    return asyncio.run(result) if inspect.isawaitable(result) else result


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def api(request):
    asynchronous = request.param
    backend = AsyncBackend() if asynchronous else Backend()
    connection = MagicMock()
    connection._backend = backend
    context = ItemClientContext(backend)
    container = (AsyncContainerProxy if asynchronous else ContainerProxy)(
        connection, "dbs/sales", "orders", _item_context=context,
    )
    database = (AsyncDatabaseProxy if asynchronous else DatabaseProxy)(
        connection, "sales", _item_context=context,
    )
    return SimpleNamespace(
        asynchronous=asynchronous, backend=backend, connection=connection,
        container=container, database=database,
    )


ITEM_CALLS = [
    ("create_item", {"body": {"id": "order-42", "customerId": "customer-17"}}),
    ("upsert_item", {"body": {"id": "order-42", "customerId": "customer-17"}}),
    ("replace_item", {"item": "order-42", "body": {"id": "order-42"}}),
    ("read_item", {"item": "order-42", "partition_key": "customer-17"}),
    ("delete_item", {"item": "order-42", "partition_key": "customer-17"}),
    ("patch_item", {
        "item": "order-42", "partition_key": "customer-17",
        "patch_operations": [{"op": "set", "path": "/status", "value": "approved"}],
    }),
    ("query_items", {"query": "SELECT * FROM c"}),
    ("read_all_items", {}),
    ("execute_item_batch", {"batch_operations": [], "partition_key": "customer-17"}),
    ("delete_all_items_by_partition_key", {"partition_key": "customer-17"}),
]

EXCLUDED_OPTIONS = [
    {"pre_trigger_include": "validateOrder"},
    {"post_trigger_include": None},
    {"request_options": {"preTriggerInclude": ["validateOrder"]}},
    {"feed_options": {"postTriggerInclude": "auditOrder"}},
    {"initial_headers": {"X-MS-DOCUMENTDB-PRE-TRIGGER-INCLUDE": "validateOrder"}},
    {"request_options": {"initialHeaders": {"x-ms-documentdb-post-trigger-include": "auditOrder"}}},
    {"availability_strategy": {"threshold_ms": 100, "threshold_steps_ms": 50}},
    {"request_options": {"availabilityStrategy": {"threshold_steps_ms": None}}},
]


@pytest.mark.parametrize("method,arguments", ITEM_CALLS)
@pytest.mark.parametrize("options", EXCLUDED_OPTIONS)
def test_excluded_options_never_send_or_fall_back(api, method, arguments, options):
    with pytest.raises(TypeError, match="not supported"):
        finish(getattr(api.container, method)(**arguments, **options))
    assert api.backend.events == []
    assert api.connection.mock_calls == []


@pytest.mark.parametrize("options", [
    {"preTriggerInclude": None},
    {"postTriggerInclude": []},
    {"x-ms-documentdb-pre-trigger-include": "validateOrder"},
    {"initialHeaders": {"X-MS-DOCUMENTDB-POST-TRIGGER-INCLUDE": "auditOrder"}},
    {"availabilityStrategy": {"threshold_steps_ms": 50}},
    {"availabilityStrategy": CrossRegionHedgingStrategy({"threshold_steps_ms": 50})},
])
def test_internal_preparation_also_rejects_excluded_options(options):
    with pytest.raises(TypeError, match="not supported"):
        build_request_headers_and_settings(options)


@pytest.mark.parametrize("field", ["pre_triggers", "post_triggers"])
def test_typed_settings_no_longer_advertise_triggers(field):
    with pytest.raises(TypeError, match=field):
        ItemSettings(**{field: ("validateOrder",)})


@pytest.mark.parametrize("header", [
    "X-MS-DOCUMENTDB-PRE-TRIGGER-INCLUDE", "x-ms-documentdb-post-trigger-include",
])
def test_client_headers_cannot_reintroduce_triggers(header):
    with pytest.raises(TypeError, match="triggers are excluded"):
        build_client_config(headers={header: "validateOrder"})


def test_scripts_navigation_and_direct_construction_are_excluded(api):
    with pytest.raises(NotImplementedError, match="ContainerProxy.scripts"):
        _ = api.container.scripts
    with pytest.raises(NotImplementedError, match="ScriptsProxy"):
        if api.asynchronous:
            AsyncScriptsProxy(api.container, api.connection, api.container.container_link)
        else:
            ScriptsProxy(api.connection, api.container.container_link, False)
    assert api.backend.events == []
    assert api.connection.mock_calls == []


@pytest.mark.parametrize("method", [
    "get_user_client", "list_users", "query_users", "create_user",
    "upsert_user", "replace_user", "delete_user", "_get_user_link",
])
@pytest.mark.parametrize("legacy", [False, True])
def test_user_management_is_removed_on_both_backends(api, method, legacy):
    if legacy:
        backend = ASYNC_LEGACY_BACKEND if api.asynchronous else LEGACY_BACKEND
        api.connection._backend = backend
        api.database._item_context = ItemClientContext(backend)
    with pytest.raises(AttributeError, match=method):
        getattr(api.database, method)
    assert api.connection.mock_calls == []
    assert api.backend.events == []


@pytest.mark.parametrize("module,names", [
    ("azure.cosmos", ("UserProxy", "Permission", "PermissionMode")),
    ("azure.cosmos.aio", ("UserProxy",)),
    ("azure.cosmos.documents", ("PermissionMode",)),
    ("azure.cosmos.database", ("UserProxy",)),
    ("azure.cosmos.aio._database", ("UserProxy",)),
])
def test_user_permission_types_are_not_exported(module, names):
    public_module = importlib.import_module(module)
    for name in names:
        assert not hasattr(public_module, name)
        assert name not in getattr(public_module, "__all__", ())


def test_user_permission_constants_are_removed():
    from azure.cosmos.http_constants import HttpHeaders, ResourceType

    assert not hasattr(ResourceType, "User")
    assert not hasattr(ResourceType, "Permission")
    assert not hasattr(HttpHeaders, "ResourceTokenExpiry")


@pytest.mark.parametrize("module", [
    "azure.cosmos.user", "azure.cosmos.aio._user", "azure.cosmos.permission",
])
def test_user_permission_modules_are_removed(module):
    with pytest.raises(ModuleNotFoundError) as error:
        importlib.import_module(module)
    assert error.value.name == module


@pytest.mark.parametrize("module", [
    "azure.cosmos._cosmos_client_connection",
    "azure.cosmos.aio._cosmos_client_connection_async",
])
def test_legacy_user_permission_operations_are_removed(module):
    connection = importlib.import_module(module).CosmosClientConnection
    for resource in ("User", "Permission"):
        for operation in ("Create", "Upsert", "Read", "Replace", "Delete"):
            assert not hasattr(connection, operation + resource)
        for operation in ("Read", "Query"):
            assert not hasattr(connection, operation + resource + "s")
    assert not hasattr(connection, "_GetDatabaseIdWithPathForUser")
    assert not hasattr(connection, "_GetUserIdWithPathForPermission")
    assert callable(connection.DeleteDatabase)


def test_permission_token_expiry_is_not_a_typed_setting():
    with pytest.raises(TypeError, match="resource_token_expiry_seconds"):
        ResourceSettings(resource_token_expiry_seconds=60)


@pytest.mark.parametrize("option", ["resource_token_expiry_seconds", "resourceTokenExpirySeconds"])
def test_permission_token_expiry_is_not_a_rust_request_option(option):
    with pytest.raises(TypeError, match="Unknown Rust request option"):
        build_request_headers_and_settings({option: 60})


def test_legacy_scripts_and_trigger_arguments_are_preserved(api):
    legacy = ASYNC_LEGACY_BACKEND if api.asynchronous else LEGACY_BACKEND
    api.connection._backend = legacy
    api.container._item_context = ItemClientContext(legacy)
    api.database._item_context = ItemClientContext(legacy)
    api.container._get_properties = MagicMock(return_value={"partitionKey": {}})
    assert api.container.scripts is not None
    strategy = CrossRegionHedgingStrategy({"threshold_ms": 100, "threshold_steps_ms": 50})
    assert strategy.threshold_steps_ms == 50


@pytest.mark.parametrize("asynchronous", [False, True])
def test_rust_client_rejects_steps_but_legacy_client_keeps_them(asynchronous, monkeypatch):
    module = "azure.cosmos.aio._cosmos_client" if asynchronous else "azure.cosmos.cosmos_client"
    connection = MagicMock()
    monkeypatch.setattr(module + ".CosmosClientConnection", connection)
    cls = AsyncCosmosClient if asynchronous else CosmosClient
    options = {"availability_strategy": {"threshold_ms": 100, "threshold_steps_ms": 50}}
    with pytest.raises(TypeError, match="threshold_steps_ms"):
        cls("https://example.invalid", "ZmFrZQ==", _backend="rust", **options)
    connection.assert_not_called()
    client = cls("https://example.invalid", "ZmFrZQ==", _backend="core-python", **options)
    assert client._adapter.name == "core-python"
    assert connection.call_args.kwargs["availability_strategy"] == options["availability_strategy"]


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def client_constructor(request, monkeypatch):
    asynchronous = request.param
    module = "azure.cosmos.aio._cosmos_client" if asynchronous else "azure.cosmos.cosmos_client"
    connection = MagicMock()
    monkeypatch.setattr(module + ".CosmosClientConnection", connection)
    return SimpleNamespace(
        cls=AsyncCosmosClient if asynchronous else CosmosClient,
        module=module, connection=connection,
    )


def construct_client(cls, connection_string, **kwargs):
    if connection_string:
        return cls.from_connection_string(
            "AccountEndpoint=https://example.invalid;AccountKey=ZmFrZQ==", **kwargs,
        )
    return cls("https://example.invalid", "ZmFrZQ==", **kwargs)


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("credential_factory", [
    lambda: {"dbs/sales/colls/orders": "removed-token"},
    lambda: {"resourceTokens": {"dbs/sales": "removed-token"}},
    lambda: {"permissionFeed": [{"resource": "dbs/sales", "_token": "removed-token"}]},
    lambda: {"masterKey": "ZmFrZQ==", "resourceTokens": None},
    lambda: {"masterKey": "ZmFrZQ==", "permissionFeed": []},
    lambda: [{"resource": "dbs/sales", "_token": "removed-token"}],
    lambda: ({"resource": "dbs/sales", "_token": "removed-token"},),
    lambda: ({"resource": "dbs/sales", "_token": "removed-token"} for _ in range(1)),
    lambda: {},
    lambda: [],
])
def test_removed_credentials_fail_before_backend_or_connection_creation(
    client_constructor, backend, credential_factory, monkeypatch,
):
    factory_name = "make_async_backend" if client_constructor.cls is AsyncCosmosClient else "make_backend"
    factory = MagicMock()
    monkeypatch.setattr(client_constructor.module + "." + factory_name, factory)
    with pytest.raises(ValueError, match="Resource-token|resource-token"):
        client_constructor.cls(
            "https://example.invalid", credential_factory(), _backend=backend,
        )
    factory.assert_not_called()
    client_constructor.connection.assert_not_called()


@pytest.mark.parametrize("module", [
    "azure.cosmos._cosmos_client_connection",
    "azure.cosmos.aio._cosmos_client_connection_async",
])
@pytest.mark.parametrize("field,value", [("resourceTokens", None), ("permissionFeed", [])])
def test_removed_auth_fields_cannot_be_used_by_direct_connections(module, field, value):
    connection_module = importlib.import_module(module)
    assert field not in connection_module.CredentialDict.__annotations__
    with pytest.raises(ValueError, match="resource-token"):
        connection_module.CosmosClientConnection(
            "https://example.invalid", {"masterKey": "ZmFrZQ==", field: value},
        )


def test_resource_token_header_selection_is_removed():
    from azure.cosmos import auth

    assert not hasattr(auth, "__get_authorization_token_using_resource_token")
    connection = SimpleNamespace(master_key=None)
    assert auth._get_authorization_header(
        connection, "get", "dbs/sales", "dbs/sales", True, "dbs", {},
    ) is None


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("credential", ["ZmFrZQ==", {"masterKey": "ZmFrZQ=="}])
def test_account_key_forms_remain_supported(client_constructor, backend, credential):
    client = client_constructor.cls("https://example.invalid", credential, _backend=backend)
    try:
        assert client_constructor.connection.call_args.kwargs["auth"] == {"masterKey": "ZmFrZQ=="}
        assert client._adapter.name == backend
    finally:
        finish(client._adapter.close())


@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("async_credential", [False, True])
def test_entra_credentials_remain_supported_without_fetching_a_token(
    client_constructor, backend, async_credential,
):
    class Credential:
        def get_token(self, *scopes, **kwargs):
            raise AssertionError("Construction must not fetch a token")

    class AsyncCredential:
        async def get_token(self, *scopes, **kwargs):
            raise AssertionError("Construction must not fetch a token")

    credential = AsyncCredential() if async_credential else Credential()
    client = client_constructor.cls("https://example.invalid", credential, _backend=backend)
    try:
        assert client_constructor.connection.call_args.kwargs["auth"]["clientSecretCredential"] is credential
    finally:
        finish(client._adapter.close())


@pytest.mark.parametrize("connection_string", [False, True], ids=["direct", "connection-string"])
@pytest.mark.parametrize("options", EXCLUDED_OPTIONS + [
    {"threshold_steps_ms": None},
    {"preTriggerInclude": []},
    {"headers": {"x-ms-documentdb-post-trigger-include": "auditOrder"}},
])
def test_constructor_rejects_excluded_inputs_before_backend_creation(
    client_constructor, connection_string, options, monkeypatch,
):
    factory_name = "make_async_backend" if client_constructor.cls is AsyncCosmosClient else "make_backend"
    factory = MagicMock()
    monkeypatch.setattr(client_constructor.module + "." + factory_name, factory)
    with pytest.raises(TypeError, match="not supported"):
        construct_client(
            client_constructor.cls, connection_string, _backend="rust", **options,
        )
    factory.assert_not_called()
    client_constructor.connection.assert_not_called()


@pytest.mark.parametrize("connection_string", [False, True], ids=["direct", "connection-string"])
@pytest.mark.parametrize("backend", ["rust", "core-python"])
def test_supported_constructor_preserves_backend_and_threshold(
    client_constructor, connection_string, backend,
):
    strategy = {"threshold_ms": 100}
    client = construct_client(
        client_constructor.cls, connection_string, _backend=backend,
        availability_strategy=strategy,
    )
    assert client._adapter.name == backend
    assert client._item_context.defaults.hedging_threshold_ms == (
        100 if backend == "rust" else None
    )
    assert client_constructor.connection.call_args.kwargs["availability_strategy"] == strategy
    client_constructor.connection.assert_called_once()


@pytest.mark.parametrize("connection_string", [False, True], ids=["direct", "connection-string"])
@pytest.mark.parametrize("options", EXCLUDED_OPTIONS)
def test_legacy_constructor_preserves_excluded_options(
    client_constructor, connection_string, options,
):
    client = construct_client(
        client_constructor.cls, connection_string, _backend="core-python", **options,
    )
    assert client._adapter.name == "core-python"
    for name, value in options.items():
        assert client_constructor.connection.call_args.kwargs[name] == value


@pytest.mark.parametrize("connection_string", [False, True], ids=["direct", "connection-string"])
def test_constructor_exclusions_follow_environment_and_explicit_override(
    client_constructor, connection_string, monkeypatch,
):
    monkeypatch.setenv("COSMOS_BACKEND", "rust")
    with pytest.raises(TypeError, match="pre_trigger_include"):
        construct_client(client_constructor.cls, connection_string, pre_trigger_include=None)
    client_constructor.connection.assert_not_called()
    client = construct_client(
        client_constructor.cls, connection_string,
        _backend="core-python", pre_trigger_include=None,
    )
    assert client._adapter.name == "core-python"
