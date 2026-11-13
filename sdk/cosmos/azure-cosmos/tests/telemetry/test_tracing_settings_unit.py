# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Customer tracing settings stay in Python and apply to owned attempt spans."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

pytest.importorskip("opentelemetry.sdk.trace")
# pylint: disable=wrong-import-position
from azure.core.settings import settings
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.pipeline.policies import DistributedTracingPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.cosmos import CosmosClient, _telemetry
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common.rust_telemetry_payload import v2
from telemetry.test_rust_telemetry_unit import (
    recording_setup,
)  # pylint: disable=unused-import

# pylint: enable=wrong-import-position


def test_core_python_namer_receives_actual_request_and_per_call_override(recording):
    request = HttpRequest(
        "GET",
        "https://alpha-bank.invalid/dbs/sales/colls/orders/docs/order-42",
        headers={"x-bank-operation": "read-order"},
    )
    default = Mock(return_value="default-name")
    observed = []

    def name(actual_request):
        observed.append(actual_request)
        assert actual_request.headers["x-bank-operation"] == "read-order"
        return "orders-" + actual_request.method.lower()

    policy = DistributedTracingPolicy(network_span_namer=default)
    pipeline_request = PipelineRequest(request, PipelineContext(None, network_span_namer=name))
    policy.on_request(pipeline_request)
    try:
        assert observed == [request]
        assert observed[0] is request
        default.assert_not_called()
    finally:
        policy.end_span(pipeline_request)
    spans = recording.exporter.get_finished_spans()
    assert len(spans) == 1 and spans[0].name == "orders-get"


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def native(request, recording, monkeypatch):  # pylint: disable=unused-argument
    asynchronous = request.param
    defaults = {"bank.component": "orders", "bank.labels": ["default"]}
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        "https://alpha-bank.invalid",
        "ZmFrZQ==",
        _backend="rust",
        tracing_attributes=defaults,
    )
    h = SimpleNamespace(
        client=client,
        defaults=defaults,
        container=client.get_database_client("sales").get_container_client("orders"),
        asynchronous=asynchronous,
        calls=[],
        status=200,
    )
    monkeypatch.setattr(
        client._adapter,
        "_ensure_driver_handle",
        (AsyncMock(return_value="handle") if asynchronous else Mock(return_value="handle")),
    )

    def respond(handle, prepared, *, include_attempts=False, timeout_seconds=None):
        assert handle == "handle"
        h.calls.append((prepared, include_attempts, timeout_seconds))
        body = {"id": prepared.item_id} if h.status == 200 else {"message": "missing"}
        response = h.status, 0, {}, json.dumps(body).encode(), "diagnostic summary"
        end = time.time_ns()
        payload = v2({
            "schema_version": 2,
            "complete": True,
            "incomplete_reasons": [],
            "request_count": 1,
            "retained_request_count": 1,
            "error": None,
            "attempts": [
                {
                    "start_ns": end - 1,
                    "end_ns": end,
                    "driver_status_code": h.status,
                    "execution_context": "initial",
                }
            ],
        })
        return (response, payload) if include_attempts else response

    async def respond_async(*args, **kwargs):
        await asyncio.sleep(0)
        return respond(*args, **kwargs)

    monkeypatch.setattr(
        async_binding if asynchronous else sync_binding,
        "_binding_function_for_op",
        lambda _: respond_async if asynchronous else respond,
    )

    def read(**kwargs):
        result = h.container.read_item("order-42", partition_key="customer-17", **kwargs)
        return asyncio.run(result) if asynchronous else result

    h.read = read
    try:
        yield h
    finally:
        result = client.close()
        if asynchronous:
            asyncio.run(result)


def assert_attributes(recording, expected, operation_expected=None):
    spans = recording.exporter.get_finished_spans()
    assert len(spans) == 2
    operation = next(span for span in spans if span.name == "ContainerProxy.read_item")
    attempt = next(span for span in spans if span.name == "cosmosdb.request")
    assert attempt.parent.span_id == operation.context.span_id
    for span, labels in (
        (operation, expected if operation_expected is None else operation_expected),
        (attempt, expected),
    ):
        assert {key: value for key, value in span.attributes.items() if key.startswith("bank.")} == labels
    assert _telemetry._OPERATION.get() is None


def test_constructor_attributes_are_snapshotted_request_defaults(native, recording):
    native.defaults["bank.component"] = "mutated"
    native.defaults["bank.labels"].append("mutated")
    assert native.read() == {"id": "order-42"}
    assert_attributes(
        recording,
        {"bank.component": "orders", "bank.labels": ("default",)},
        operation_expected={},
    )
    prepared = native.calls[0][0]
    assert not any(name.startswith("bank.") for name in prepared.headers)


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"tracing_attributes": {}}, {}),
        (
            {"tracing_attributes": {"bank.component": "fraud"}},
            {"bank.component": "fraud"},
        ),
        (
            {"tracing_options": {"attributes": {"bank.component": "fraud"}}},
            {"bank.component": "fraud", "bank.labels": ("default",)},
        ),
        (
            {
                "tracing_attributes": {"bank.component": "orders", "bank.call": "42"},
                "tracing_options": {"attributes": {"bank.component": "fraud"}},
            },
            {"bank.component": "fraud", "bank.call": "42"},
        ),
    ],
)
def test_per_call_precedence_does_not_mutate_client_defaults(native, recording, kwargs, expected):
    before = deepcopy(kwargs)
    native.read(**kwargs)
    operation_expected = {
        **kwargs.get("tracing_attributes", {}),
        **kwargs.get("tracing_options", {}).get("attributes", {}),
    }
    assert_attributes(recording, expected, operation_expected)
    assert kwargs == before
    recording.exporter.clear()
    native.read()
    assert_attributes(
        recording,
        {"bank.component": "orders", "bank.labels": ("default",)},
        operation_expected={},
    )


def test_hook_mutation_does_not_change_attempt_attributes(native, recording):
    attributes = {"bank.labels": ["original"]}

    def hook(_headers, _body):
        attributes["bank.labels"].append("mutated")
        attributes["bank.extra"] = "late"

    native.read(tracing_attributes=attributes, response_hook=hook)
    assert attributes["bank.labels"] == ["original", "mutated"]
    assert_attributes(recording, {"bank.labels": ("original",)})


def test_attribute_snapshot_failure_preserves_read_and_reports_missing_attempts(native, recording, caplog):
    class UncopyableLabel(str):
        def __deepcopy__(self, memo):
            raise RuntimeError("PRIVATE")

    assert native.read(tracing_attributes={"bank.call": UncopyableLabel("42")}) == {"id": "order-42"}
    assert not native.calls[0][1]
    spans = recording.exporter.get_finished_spans()
    assert len(spans) == 1 and spans[0].name == "ContainerProxy.read_item"
    assert "could not snapshot tracing attributes" in caplog.text
    assert "PRIVATE" not in caplog.text


@pytest.mark.parametrize("enabled", [False, True])
def test_per_call_enablement_still_controls_operation_and_attempts(native, recording, enabled):
    settings.tracing_enabled = not enabled
    native.read(tracing_options={"enabled": enabled, "attributes": {"bank.call": "42"}})
    assert native.calls[0][1] is enabled
    if enabled:
        assert_attributes(
            recording,
            {
                "bank.component": "orders",
                "bank.labels": ("default",),
                "bank.call": "42",
            },
            operation_expected={"bank.call": "42"},
        )
    else:
        assert not recording.exporter.get_finished_spans()


def test_error_attempt_retains_attributes_and_actual_driver_facts(native, recording):
    native.status = 404
    with pytest.raises(CosmosResourceNotFoundError, match="missing"):
        native.read(
            tracing_attributes={
                "bank.call": "42",
                "db.response.status_code": "200",
                "azure.cosmosdb.request.execution_context": "invented",
            }
        )
    assert_attributes(recording, {"bank.call": "42"})
    attempt = next(span for span in recording.exporter.get_finished_spans() if span.name == "cosmosdb.request")
    assert attempt.attributes["db.response.status_code"] == "404"
    assert attempt.attributes["azure.cosmosdb.request.execution_context"] == "initial"


def test_concurrent_calls_keep_their_own_attribute_values(native, recording):
    def read(label):
        return native.read(tracing_attributes={"bank.call": label})

    async def reads():
        return await asyncio.gather(
            *(
                native.container.read_item(
                    "order-42",
                    partition_key="customer-17",
                    tracing_attributes={"bank.call": label},
                )
                for label in ("first", "second")
            )
        )

    if native.asynchronous:
        results = asyncio.run(reads())
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(read, ("first", "second")))
    assert results == [{"id": "order-42"}, {"id": "order-42"}]
    spans = recording.exporter.get_finished_spans()
    operations = {span.context.span_id: span for span in spans if span.name == "ContainerProxy.read_item"}
    attempts = [span for span in spans if span.name == "cosmosdb.request"]
    assert len(operations) == len(attempts) == 2
    assert {span.attributes["bank.call"] for span in operations.values()} == {
        "first",
        "second",
    }
    for attempt in attempts:
        assert attempt.attributes["bank.call"] == operations[attempt.parent.span_id].attributes["bank.call"]


def test_core_python_operation_does_not_inherit_rust_attribute_defaults(recording):
    owner = SimpleNamespace(
        _item_context=SimpleNamespace(
            adapter=SimpleNamespace(name="core-python"),
            tracing_attributes={"bank.component": "not-a-legacy-operation-default"},
        )
    )

    @_telemetry.trace_operation(binding_operation="read_item")
    def read(_owner, **kwargs):
        return kwargs

    options = {"tracing_attributes": {"bank.call": "legacy"}}
    assert read(owner, **options) == options
    spans = recording.exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["bank.call"] == "legacy"
    assert "bank.component" not in spans[0].attributes
