# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exact Python/native request protocol, without credentials or service requests."""
from common.typed_requests import key_from_legacy_header, legacy_partition_key_from_request
from common.typed_requests import wire_headers, settings_options, legacy_settings
from copy import deepcopy
import inspect
from dataclasses import replace
from itertools import permutations

import pytest

from azure.cosmos._backend.contracts import PreparedRequest, PreparedQuery
from azure.cosmos._backend.rust import build_binding_request_from_page as sync_page
from azure.cosmos.aio._backend.rust import build_binding_request_from_page as async_page
from azure.cosmos._helpers import _request_item
from azure.cosmos._helpers._document import serialize_document
from common.typed_requests import legacy_preparation as prepare_request_headers
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings
from azure.cosmos._backend.request_settings import RequestSettings
from common.test_connection_free_items_unit import Backend, AsyncBackend, invoke
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op", ["create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item"])
def test_every_point_operation_has_only_headers_and_explicit_options(async_mode, op):
    backend = AsyncBackend() if async_mode else Backend()
    options = {
        "partitionKey": "p", "disableAutomaticIdGeneration": True,
        "initialHeaders": {"x-customer": "value"},
    }
    before = deepcopy(options)
    invoke((AsyncItemHelper if async_mode else ItemHelper)(backend), op,
           request_options=options, no_response=False,
           pre_trigger_include=["a", "b"], excluded_locations=["West US"],
           availability_strategy=False)
    request = backend.events[-1]
    assert wire_headers(request) == {
        "x-customer": "value",
        "x-ms-documentdb-pre-trigger-include": "a,b",
    }
    assert settings_options(request) == {
        "responsePayloadOnWriteDisabled": False,
        "excludedLocations": ["West US"],
        "availabilityStrategy": "disabled",
    }
    assert legacy_partition_key_from_request(request) == '["p"]'
    assert backend.events.count("metadata") == 0
    assert options == before


@pytest.mark.parametrize("operation", ["create_item", "upsert_item", "replace_item", "patch_item"])
def test_write_builders_require_snapshots_and_normalized_options(operation):
    parameters = inspect.signature(getattr(_request_item, f"build_{operation}_request")).parameters
    snapshot = "body_bytes" if operation == "patch_item" else "document"
    assert {snapshot, "request_options"} <= parameters.keys()
    assert not {"body", "patch_operations", "kwargs", "compact_utf8", "enable_automatic_id_generation"} & parameters.keys()
    for name in (snapshot, "request_options"):
        assert parameters[name].default is inspect.Parameter.empty


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_page_adapter_preserves_separate_options_without_a_deadline(adapter):
    page = PreparedQuery(
        op="read_all_items", container_link="dbs/d/colls/c",
        headers={"x-customer": "value"}, settings=legacy_settings({"excludedLocations": ["West US"]}),
        continuation="token", max_item_count=2,
    )
    request = adapter(page)
    assert wire_headers(request) == {"x-customer": "value", "x-ms-continuation": "token", "x-ms-max-item-count": "2"}
    assert settings_options(request) == settings_options(page)
    assert settings_options(request) is not settings_options(page)
    assert not hasattr(request, "deadline")
    assert not hasattr(page, "deadline")


def test_unknown_options_do_not_become_headers_or_vanish():
    with pytest.raises(TypeError, match="unknownFutureOption"):
        build_request_headers_and_settings({"unknownFutureOption": True, "partitionKey": "p", "timeout": 2})


@pytest.mark.parametrize("condition_type,header", [
    ("IfMatch", "if-match"), ("IfNoneMatch", "if-none-match"),
])
@pytest.mark.parametrize("header_case", [str.lower, str.upper, str.title])
@pytest.mark.parametrize("source_order", list(permutations(("initial", "access", "direct"))))
@pytest.mark.parametrize("through_builder", [False, True])
def test_conditional_header_sources_resolve_case_insensitively_in_input_order(
    condition_type, header, header_case, source_order, through_builder
):
    sources = {
        "initial": ("initialHeaders", {header_case(header): '"initial"'}),
        "access": ("accessCondition", {"type": condition_type, "condition": "*"}),
        "direct": (header_case(header), '"expected-etag"'),
    }
    options = dict(sources[source] for source in source_order)
    before = deepcopy(options)
    if through_builder:
        request = _request_item.build_replace_item_request(
            container_link="dbs/Contoso/colls/Orders",
            document=serialize_document(
                {"id": "order-42", "customerId": "customer-17"}, operation="replace_item"
            ),
            item_id="order-42", partition_key_value="customer-17",
            container_rid="rid", request_options=options,
        )
        headers = wire_headers(request)
        assert settings_options(request) == {}
    else:
        headers, request_options = prepare_request_headers(options)
        assert request_options == {}
    expected = {"initial": '"initial"', "access": "*", "direct": '"expected-etag"'}[source_order[-1]]
    assert [(key, value) for key, value in headers.items() if key.lower() == header] == [(header, expected)]
    assert options == before


@pytest.mark.parametrize("method", [
    "create_item", "read_item", "delete_item", "upsert_item", "replace_item", "patch_item",
    "create_database", "read_database", "delete_database",
    "read_container", "delete_container", "replace_container",
    "list_databases", "list_containers", "read_offer", "replace_offer",
])
@pytest.mark.parametrize("async_mode", [False, True])
def test_native_every_extraction_family_reads_request_options_before_io(monkeypatch, method, async_mode):
    native = pytest.importorskip("azure.cosmos._rust")
    monkeypatch.setenv("COSMOS_WIRE_STRICT", "1")
    request = PreparedRequest(
        op=method, container_link="dbs/d" if method == "list_containers" else "dbs/d/colls/c", item_id="item",
        body_bytes=b'{"id":"item"}', partition_key=key_from_legacy_header('["p"]'),
        headers={"x-customer": "value"},
    )
    settings = RequestSettings()
    object.__setattr__(settings, "timeout_seconds", True)
    request = replace(request, settings=settings)
    entrypoint = getattr(native, method + ("_async" if async_mode else ""))
    with pytest.raises(TypeError, match="timeout_seconds"):
        entrypoint("unused-handle", request)


@pytest.mark.parametrize("consumed", ["partitionKey", "disableAutomaticIdGeneration"])
def test_native_consumed_options_have_no_dead_allowlist(monkeypatch, consumed):
    with pytest.raises(TypeError, match=consumed):
        RequestSettings(**{consumed: True})


def test_native_rejects_old_private_request_shape(monkeypatch):
    native = pytest.importorskip("azure.cosmos._rust")
    from types import SimpleNamespace
    old = SimpleNamespace(container_link="dbs/d/colls/c", protocol_version=3, partition_key=key_from_legacy_header('["p"]'), headers={}, item_id="item")
    with pytest.raises(TypeError, match="typed settings"):
        native.read_item("unused-handle", old)


def test_native_driver_handle_exports_and_keyword_contract():
    native = pytest.importorskip("azure.cosmos._rust")
    assert not hasattr(native, "init_client")
    assert not hasattr(native, "close_client")
    acquire = inspect.signature(native.acquire_driver_handle).parameters
    assert tuple(acquire) == ("endpoint", "master_key", "config", "credential")
    assert acquire["endpoint"].default is inspect.Parameter.empty
    assert all(acquire[name].default is None for name in ("master_key", "config", "credential"))
    assert tuple(inspect.signature(native.release_driver_handle).parameters) == ("driver_handle",)
    with pytest.raises(ValueError, match="acquire_driver_handle requires either"):
        native.acquire_driver_handle(
            endpoint="https://unused.invalid", master_key=None, config=None, credential=None
        )
    assert native.release_driver_handle(driver_handle="unused-protocol-test-handle") is None
