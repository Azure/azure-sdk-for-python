# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Typed metadata, pure extraction, and public response-state ownership."""
from common.typed_requests import legacy_partition_key_from_request

import asyncio
import inspect
from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import ServiceResponseError
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._backend._binding_conversions import build_container_metadata
from azure.cosmos._backend.contracts import ContainerMetadata
from azure.cosmos._backend.errors import BackendProtocolError
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders
from azure.cosmos._helpers._pk_extract import extract_partition_key_value
from azure.cosmos._helpers.item_helper import ItemHelper
from azure.cosmos.aio._helpers.item_helper import AsyncItemHelper
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError
from azure.cosmos.partition_key import _Empty, _Undefined


@pytest.mark.parametrize(
    "raw",
    [
        None,
        (),
        (200, 0, {}, b'{"_rid":"rid"}'),
        ("", ("/pk",), "Hash", None),
        (12, (), None, None),
        ("rid", ["/pk"], "Hash", None),
        ("rid", (1,), "Hash", None),
        ("rid", ("",), "Hash", None),
        ("rid", (), "Hash", None),
        ("rid", ("/pk",), None, None),
        ("rid", ("/pk",), "unknown", None),
        ("rid", ("/pk",), "Hash", 1),
    ],
)
def test_invalid_native_metadata_is_a_protocol_error(raw):
    with pytest.raises(BackendProtocolError):
        build_container_metadata(raw)


@pytest.mark.parametrize("kind", ["Hash", "MultiHash", "Range"])
@pytest.mark.parametrize("system_key", [None, False, True])
def test_metadata_preserves_kind_and_system_key_knowledge(kind, system_key):
    result = build_container_metadata(("rid", ("/pk",), kind, system_key))
    assert result == ContainerMetadata("rid", ("/pk",), kind, system_key)
    with pytest.raises(FrozenInstanceError):
        result.rid = "changed"


@pytest.mark.parametrize(
    "kind,paths,body,expected",
    [
        ("Hash", ("/pk",), {"pk": "customerA"}, "customerA"),
        ("Hash", ("/address/city",), {"address": {"city": "Seattle"}}, "Seattle"),
        ("MultiHash", ("/a", "/b"), {"a": "x", "b": "y"}, ["x", "y"]),
        ("MultiHash", ("/a", "/b"), {"a": "x"}, ["x", None]),
        ("MultiHash", ("/pk",), {"pk": "x"}, ["x"]),
        ("Range", ("/pk",), {"pk": "x"}, "x"),
    ],
)
def test_extraction_uses_kind_not_path_count(kind, paths, body, expected):
    assert (
        extract_partition_key_value(ContainerMetadata("rid", paths, kind), body)
        == expected
    )


@pytest.mark.parametrize(
    "flag,expected", [(True, _Empty), (False, _Undefined), (None, _Undefined)]
)
def test_missing_partition_key_preserves_existing_system_key_behavior(flag, expected):
    metadata = ContainerMetadata("rid", ("/pk",), "Hash", flag)
    assert isinstance(extract_partition_key_value(metadata, {"id": "item"}), expected)


def test_absent_definition_is_explicit():
    metadata = build_container_metadata(("rid", (), None, None))
    assert isinstance(extract_partition_key_value(metadata, {"pk": "ignored"}), _Empty)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def metadata_case(request, monkeypatch):
    asynchronous = request.param
    module = async_rust if asynchronous else sync_rust
    state = ClientLastResponseHeaders(
        CaseInsensitiveDict({"etag": "previous", "x-ms-request-charge": "7"})
    )
    original_headers = state.last_response_headers
    context = SimpleNamespace(
        raw=("rid", ("/pk",), "Hash", None),
        asynchronous=asynchronous,
        state=state,
        original_headers=original_headers,
        metadata_error=None,
        write_error=None,
    )

    def metadata(*_args, **_kwargs):
        assert state.last_response_headers is original_headers
        if context.metadata_error is not None:
            raise context.metadata_error
        return context.raw

    def create(_handle, prepared, **_kwargs):
        context.prepared = prepared
        assert state.last_response_headers is original_headers
        if context.metadata_error is not None:
            raise context.metadata_error
        if context.write_error is not None:
            raise context.write_error
        return (
            201,
            0,
            {"etag": "item", "x-ms-request-charge": "3"},
            b'{"id":"item"}',
            None,
        )

    wrap = AsyncMock if asynchronous else MagicMock
    binding = SimpleNamespace()
    getter = wrap(side_effect=metadata)
    setattr(
        binding,
        "get_container_metadata_async" if asynchronous else "get_container_metadata",
        getter,
    )
    setattr(
        binding,
        "create_item_async" if asynchronous else "create_item",
        wrap(side_effect=create),
    )
    context.item_call = getattr(
        binding, "create_item_async" if asynchronous else "create_item"
    )
    monkeypatch.setattr(module, "_rust_module", binding)
    backend = (async_rust.AsyncRustBackend if asynchronous else sync_rust.RustBackend)(
        "https://metadata.invalid",
        master_key="ZmFrZQ==",
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", wrap(return_value="handle"))
    helper = (AsyncItemHelper if asynchronous else ItemHelper)(
        backend, response_state=state
    )

    def run(value):
        return asyncio.run(value) if inspect.isawaitable(value) else value

    context.get = lambda: run(backend.get_container_metadata("dbs/db/colls/c"))
    from common.request_preparation import call_create_item_helper
    context.create = lambda **kwargs: run(
        call_create_item_helper(
            helper,
            container_link="dbs/db/colls/c",
            body={"id": "item", "pk": "key"},
            **kwargs,
        )
    )
    context.run, context.helper, context.backend, context.getter, context.module = (
        run,
        helper,
        backend,
        getter,
        module,
    )
    yield context
    run(backend.close())


def test_metadata_success_does_not_parse_json_or_a_response(metadata_case, monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("Metadata is not a document response")

    monkeypatch.setattr(
        "azure.cosmos._helpers._response_parse.process_backend_response", forbidden
    )
    monkeypatch.setattr(
        "azure.cosmos._backend._binding_conversions.build_backend_response", forbidden
    )
    monkeypatch.setattr("json.loads", forbidden)
    assert metadata_case.get() == ContainerMetadata("rid", ("/pk",), "Hash")
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


def test_each_call_observes_current_driver_metadata_without_a_python_cache(
    metadata_case,
):
    assert metadata_case.get().rid == "rid"
    metadata_case.raw = ("recreated-rid", ("/tenant",), "Hash", None)
    assert metadata_case.get().rid == "recreated-rid"
    assert metadata_case.getter.call_count == 2


def test_point_operation_uses_one_item_call_and_only_publishes_item_headers(
    metadata_case,
):
    metadata_case.create()
    assert metadata_case.getter.call_count == 0
    assert metadata_case.item_call.call_count == 1
    assert "x-ms-cosmos-intended-collection-rid" not in metadata_case.prepared.headers
    assert legacy_partition_key_from_request(metadata_case.prepared) is None
    assert metadata_case.state.last_response_headers["etag"] == "item"


@pytest.mark.parametrize(
    "key,header",
    [
        ("explicit", '["explicit"]'),
        (None, "[null]"),
        (_Undefined(), "[{}]"),
        (_Empty(), "[]"),
    ],
)
def test_explicit_key_overrides_extraction(metadata_case, key, header):
    metadata_case.create(request_options={"partitionKey": key})
    assert legacy_partition_key_from_request(metadata_case.prepared) == header
    assert metadata_case.getter.call_count == 0


@pytest.mark.parametrize(
    "op",
    [
        "create_item",
        "upsert_item",
        "replace_item",
        "read_item",
        "delete_item",
        "patch_item",
    ],
)
def test_all_point_operations_enter_only_the_item_binding(
    metadata_case, op, monkeypatch
):
    case = metadata_case
    method = op + ("_async" if case.asynchronous else "")
    monkeypatch.setattr(case.module._rust_module, method, case.item_call, raising=False)
    arguments = {"container_link": "dbs/db/colls/c", "item_id": "item"}
    if op in ("create_item", "upsert_item", "replace_item"):
        arguments["body"] = {"id": "item", "pk": "key"}
    else:
        arguments["request_options"] = {"partitionKey": "key"}
    if op == "patch_item":
        arguments["patch_operations"] = [{"op": "incr", "path": "/n", "value": 1}]
    from common.request_preparation import call_item_helper
    case.run(call_item_helper(case.helper, op, **arguments))
    case.item_call.assert_called_once()
    case.getter.assert_not_called()
    assert "x-ms-cosmos-intended-collection-rid" not in case.prepared.headers


@pytest.mark.parametrize("status", [400, 404, 429])
def test_metadata_errors_keep_details_without_publishing_headers(metadata_case, status):
    raw = (
        status,
        1002,
        {
            "etag": "metadata-error",
            "x-ms-retry-after-ms": "25",
            "x-ms-request-charge": "1",
        },
        b'{"message":"lookup failed"}',
        '{"request_count":1}',
    )
    metadata_case.metadata_error = metadata_case.module._DRIVER_RESPONSE_ERROR(raw)
    expected = CosmosResourceNotFoundError if status == 404 else CosmosHttpResponseError
    with pytest.raises(expected) as raised:
        metadata_case.create()
    error = raised.value
    assert error.status_code == status
    assert error.sub_status == 1002
    assert "lookup failed" in str(error)
    assert error.response.headers["etag"] == "metadata-error"
    assert error.response.headers["x-ms-retry-after-ms"] == "25"
    assert (
        error.response.headers["x-ms-cosmos-sdk-diagnostics"] == '{"request_count":1}'
    )
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


@pytest.mark.parametrize("phase", ["metadata", "write"])
def test_transport_failure_does_not_clear_previous_headers(metadata_case, phase):
    error = metadata_case.module._DRIVER_TRANSPORT_ERROR("transport failed")
    if phase == "metadata":
        metadata_case.metadata_error = error
    else:
        metadata_case.write_error = error
    with pytest.raises(ServiceResponseError):
        metadata_case.create()
    assert metadata_case.state.last_response_headers is metadata_case.original_headers


def test_metadata_cancellation_preserves_headers_and_drains_work(metadata_case):
    if not metadata_case.asynchronous:
        pytest.skip("Async cancellation contract")

    async def run():
        started, stopped = asyncio.Event(), asyncio.Event()

        async def pending(*_args, **_kwargs):
            started.set()
            try:
                await asyncio.Future()
            finally:
                stopped.set()

        metadata_case.item_call.side_effect = pending
        from common.request_preparation import call_create_item_helper
        task = asyncio.create_task(
            call_create_item_helper(
                metadata_case.helper,
                container_link="dbs/db/colls/c",
                body={"id": "item", "pk": "key"},
                timeout=1,
            )
        )
        await asyncio.wait_for(started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stopped.is_set()
        assert (
            metadata_case.state.last_response_headers is metadata_case.original_headers
        )

    asyncio.run(run())
