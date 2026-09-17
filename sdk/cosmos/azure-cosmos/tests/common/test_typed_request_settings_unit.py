# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Typed request ABI, value/state validation, and Python/native schema agreement."""
from common.typed_requests import key_from_legacy_header
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedQuery
from azure.cosmos._backend.request_settings import (
    RequestSettings, ItemSettings, QuerySettings, HedgingSettings,
    native_settings_contract_error, request_settings_schema,
)
from azure.cosmos._backend.rust import build_binding_request_from_page as sync_page
from azure.cosmos.aio._backend.rust import build_binding_request_from_page as async_page
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings


def test_settings_are_validated_and_immutable():
    settings = RequestSettings(no_response=False, excluded_locations=())
    assert settings.no_response is False
    assert settings.excluded_locations == ()
    assert RequestSettings().excluded_locations is None
    with pytest.raises(FrozenInstanceError):
        settings.no_response = True
    with pytest.raises(TypeError):
        RequestSettings(unrecognized_option=True)


def test_mutable_inputs_are_snapshotted():
    triggers, exclusions = ["validate"], ["West US"]
    _, settings = build_request_headers_and_settings({"preTriggerInclude": triggers, "excludedLocations": exclusions})
    triggers.append("changed")
    exclusions.clear()
    assert settings.item.pre_triggers == ("validate",)
    assert settings.excluded_locations == ("West US",)


@pytest.mark.parametrize("async_mode", [False, True])
def test_incompatible_schema_fails_before_driver_acquisition(monkeypatch, async_mode):
    import asyncio
    from azure.cosmos._backend import rust as sync_rust
    from azure.cosmos.aio._backend import rust as async_rust

    module = async_rust if async_mode else sync_rust
    monkeypatch.setattr(module, "_REQUEST_CONTRACT_ERROR", "Rebuild for typed settings")
    backend_type = module.AsyncRustBackend if async_mode else module.RustBackend
    backend = backend_type("https://unused.invalid", master_key="ZmFrZQ==")

    async def check_async():
        try:
            with pytest.raises(RuntimeError, match="Rebuild"):
                await backend._ensure_driver_handle()
            assert backend._driver_handle is None
        finally:
            await backend.close()

    if async_mode:
        asyncio.run(check_async())
    else:
        try:
            with pytest.raises(RuntimeError, match="Rebuild"):
                backend._ensure_driver_handle()
            assert backend._driver_handle is None
        finally:
            backend.close()


def test_missing_settings_schema_does_not_block_legacy_imports():
    import subprocess
    import sys

    native = pytest.importorskip("azure.cosmos._rust")
    result = subprocess.run(
        [sys.executable, "-c", """
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("azure.cosmos._rust", sys.argv[1])
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
del native.request_settings_schema
sys.modules["azure.cosmos._rust"] = native
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend import rust
from azure.cosmos.aio._backend import rust as async_rust
assert "rebuild" in rust._REQUEST_CONTRACT_ERROR
assert "rebuild" in async_rust._REQUEST_CONTRACT_ERROR
""", native.__file__],
        check=False, capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("kwargs", [
    {"priority": "Urgent"}, {"throughput_bucket": True}, {"throughput_bucket": -1},
    {"no_response": "false"}, {"timeout_seconds": True}, {"timeout_seconds": float("nan")},
    {"timeout_seconds": 0}, {"excluded_locations": []}, {"excluded_locations": (1,)},
    {"session_token": 42}, {"timeout_seconds": 10**500},
])
def test_invalid_values_fail_before_native_execution(kwargs):
    with pytest.raises((TypeError, ValueError)):
        RequestSettings(**kwargs)


@pytest.mark.parametrize("strict", ["0", "1"])
def test_unknown_options_are_never_silently_dropped(monkeypatch, strict):
    monkeypatch.setenv("COSMOS_WIRE_STRICT", strict)
    with pytest.raises(TypeError, match="Unknown Rust request option"):
        build_request_headers_and_settings({"misspelled_option": 1})


@pytest.mark.parametrize("value,expected", [
    (None, None), (False, HedgingSettings(False)), (True, HedgingSettings(True, 500)),
    (SimpleNamespace(threshold_ms=250), HedgingSettings(True, 250)),
])
def test_hedging_retains_inherit_disabled_and_enabled(value, expected):
    headers, settings = build_request_headers_and_settings({"availabilityStrategy": value})
    assert settings.hedging == expected
    assert headers == {}


def test_customer_headers_and_typed_service_values_remain_separate():
    headers, settings = build_request_headers_and_settings({
        "initialHeaders": {"X-Customer": "value", "IF-MATCH": "old"},
        "accessCondition": {"type": "IfMatch", "condition": "current"},
        "throughputBucket": 7, "preTriggerInclude": ["first", "second"],
        "excludedLocations": [], "responsePayloadOnWriteDisabled": False, "sessionToken": "session",
    })
    assert headers == {"x-customer": "value"}
    assert settings.item == ItemSettings(if_match="current", pre_triggers=("first", "second"))
    assert settings.throughput_bucket == 7
    assert settings.no_response is False
    assert settings.excluded_locations == ()
    assert settings.session_token == "session"


def test_later_raw_condition_retains_existing_point_precedence():
    headers, settings = build_request_headers_and_settings({
        "accessCondition": {"type": "IfMatch", "condition": "typed"},
        "initialHeaders": {"IF-MATCH": "later"},
    })
    assert headers == {"if-match": "later"}
    assert settings.item.if_match is None


@pytest.mark.parametrize("condition", [None, 42, False])
def test_invalid_condition_is_not_silently_omitted(condition):
    with pytest.raises(TypeError, match="string condition"):
        build_request_headers_and_settings({"accessCondition": {"type": "IfMatch", "condition": condition}})
    with pytest.raises(TypeError, match="string condition"):
        build_request_headers_and_settings({"accessCondition": {"type": "IfMatch"}})


@pytest.mark.parametrize("wire,field", [
    ("x-ms-activity-id", "activity_id"), ("x-ms-session-token", "session_token"),
])
@pytest.mark.parametrize("initial_first", [False, True])
def test_explicit_activity_and_session_win_over_nested_headers(wire, field, initial_first):
    values = [(wire, "explicit"), ("initialHeaders", {wire.upper(): "nested"})]
    headers, settings = build_request_headers_and_settings(dict(reversed(values) if initial_first else values))
    assert headers == {}
    assert getattr(settings, field) == "explicit"


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_page_adapter_keeps_typed_settings_without_an_invocation_deadline(adapter):
    settings = RequestSettings(timeout_seconds=0.25, query=QuerySettings(enable_scan=True))
    page = PreparedQuery(
        op="read_all_items", container_link="dbs/d/colls/c", settings=settings,
        continuation="token", max_item_count=0, headers={"x-app": "caller"},
    )
    request = adapter(page)
    assert request.headers == {"x-app": "caller"}
    assert request.settings == replace(settings, query=replace(settings.query, continuation="token", max_item_count=0))
    assert not hasattr(request, "deadline")
    assert not hasattr(request, "request_options")
    assert page.settings is settings


def test_native_schema_has_no_unconsumed_python_fields():
    native = pytest.importorskip("azure.cosmos._rust")
    assert native_settings_contract_error(native) is None
    expected = request_settings_schema()
    assert {k: set(v) for k, v in native.request_settings_schema().items()} == {k: set(v) for k, v in expected.items()}
    assert native_settings_contract_error(SimpleNamespace()) is not None
    expected["RequestSettings"] += ("new_unconsumed_field",)
    assert native_settings_contract_error(SimpleNamespace(request_settings_schema=lambda: expected)) is not None


@pytest.mark.parametrize("method", [
    "create_item", "read_item", "replace_item", "upsert_item", "delete_item", "patch_item",
    "create_database", "read_database", "delete_database", "create_container", "read_container",
    "delete_container", "replace_container", "read_offer", "replace_offer", "list_databases", "list_containers",
])
@pytest.mark.parametrize("is_async", [False, True])
def test_every_native_reader_rejects_an_incompatible_schema_before_io(method, is_async):
    native = pytest.importorskip("azure.cosmos._rust")
    request = PreparedRequest(
        method, "dbs/d" if method == "list_containers" else "dbs/d/colls/c",
        b'{"id":"i"}', key_from_legacy_header('["p"]'), item_id="i",
    )
    # Deliberately bypass the frozen record to exercise the native trust boundary.
    object.__setattr__(request, "settings", SimpleNamespace(protocol_version=1))
    with pytest.raises(ValueError, match="protocol version"):
        getattr(native, method + ("_async" if is_async else ""))("unused-typed-settings-handle", request)
