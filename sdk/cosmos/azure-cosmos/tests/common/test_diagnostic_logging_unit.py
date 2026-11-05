# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Native diagnostic summaries use Python logging without HTTP-parity claims."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.core.settings import settings
from azure.core.pipeline import PipelineContext, PipelineRequest, PipelineResponse
from azure.core.pipeline.transport import HttpRequest
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos import _telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos._diagnostic_logging import DiagnosticLogging
from azure.cosmos._cosmos_http_logging_policy import CosmosHttpLoggingPolicy
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from read_all_items.test_read_all_items_contract_unit import feed  # pylint: disable=unused-import
from test_cosmos_http_logging_policy import FilterStatusCode

SUMMARY = "activity=example duration=8ms requests=2 charge=1RU"
HEADER = "x-ms-cosmos-sdk-diagnostics"


class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


def make_logger():
    logger = logging.Logger("alpha-bank", logging.DEBUG)
    capture = Capture()
    logger.addHandler(capture)
    logger.propagate = False
    return logger, capture


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def native(request, monkeypatch):
    asynchronous = request.param
    logger, capture = make_logger()
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type(
        "https://alpha-bank.invalid",
        "ZmFrZQ==",
        _backend="rust",
        logger=logger,
        enable_diagnostics_logging=True,
    )
    backend = client._adapter
    module = async_binding if asynchronous else sync_binding
    h = SimpleNamespace(
        client=client,
        backend=backend,
        asynchronous=asynchronous,
        logger=logger,
        capture=capture,
        calls=[],
        summary=SUMMARY,
        status=200,
        failure=None,
        tracing_payload=None,
    )
    h.container = client.get_database_client("sales").get_container_client("orders")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        AsyncMock(return_value="handle") if asynchronous else Mock(return_value="handle"),
    )

    def response(handle, prepared, **kwargs):
        assert handle == "handle"
        assert not kwargs.get("include_attempts") or h.tracing_payload is not None
        h.calls.append(prepared)
        if h.failure:
            raise h.failure
        body = (
            {"id": prepared.item_id, "customerId": "customer-17"} if h.status == 200 else {"message": "Order not found"}
        )
        result = h.status, 0, {"x-ms-request-charge": "1"}, json.dumps(body).encode(), h.summary
        return (result, h.tracing_payload) if kwargs.get("include_attempts") else result

    async def response_async(*args, **kwargs):
        await asyncio.sleep(0)
        return response(*args, **kwargs)

    monkeypatch.setattr(module, "_binding_function_for_op", lambda _: response_async if asynchronous else response)
    enabled = settings.tracing_enabled()
    settings.tracing_enabled = False

    def read(item="order-42", **kwargs):
        result = h.container.read_item(item, partition_key="customer-17", **kwargs)
        return asyncio.run(result) if asynchronous else result

    def configure(**kwargs):
        context = replace(client._item_context, diagnostic_logging=DiagnosticLogging(**kwargs))
        client._item_context = h.container._item_context = context

    h.read, h.configure = read, configure
    try:
        yield h
    finally:
        settings.tracing_enabled = enabled
        result = client.close()
        if asynchronous:
            asyncio.run(result)


@pytest.mark.parametrize(
    "diagnostics,debug,expected",
    [(False, False, []), (True, False, [logging.INFO]), (False, True, [logging.DEBUG]), (True, True, [logging.INFO])],
)
def test_native_logging_controls_and_header_identity_rust(native, diagnostics, debug, expected):
    native.configure(
        logger=native.logger,
        enable_diagnostics_logging=diagnostics,
        logging_enable=debug,
    )
    result = native.read()
    assert result.get_response_headers()[HEADER] == SUMMARY
    assert [record.levelno for record in native.capture.records] == expected
    for record in native.capture.records:
        assert record.diagnostics == result.get_response_headers()[HEADER]
        assert record.operation_type == "read_item"
        assert record.status_code == 200
        assert record.sub_status_code == 0
        assert record.getMessage() == f"Cosmos read_item response status=200 diagnostics={SUMMARY}"
    assert len(native.calls) == 1
    assert _telemetry._OPERATION.get() is None


def test_native_constructor_logger_and_per_call_override_rust(native):
    alternate, capture = make_logger()
    native.read(logger=alternate)
    assert not native.capture.records
    assert [record.diagnostics for record in capture.records] == [SUMMARY]
    native.read()
    assert [record.diagnostics for record in native.capture.records] == [SUMMARY]


def test_summary_logging_and_attempt_tracing_coexist_rust(native, monkeypatch):
    sdk = pytest.importorskip("opentelemetry.sdk.trace")
    from opentelemetry import trace
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from azure.core import instrumentation

    provider = sdk.TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: provider)
    instrumentation._get_tracer_cached.cache_clear()
    implementation = settings.tracing_implementation()
    settings.tracing_enabled, settings.tracing_implementation = True, None
    native.tracing_payload = {
        "schema_version": 1,
        "complete": True,
        "incomplete_reasons": [],
        "request_count": 1,
        "retained_request_count": 1,
        "error": None,
        "attempts": [{"start_ns": 1, "end_ns": 2, "driver_status_code": 200, "execution_context": "initial"}],
    }
    try:
        result = native.read()
        assert result.get_response_headers()[HEADER] == native.capture.records[0].diagnostics == SUMMARY
        assert len(native.capture.records) == 1
        assert sorted(span.name for span in exporter.get_finished_spans()) == [
            "ContainerProxy.read_item",
            "cosmosdb.request",
        ]
    finally:
        settings.tracing_implementation = implementation
        instrumentation._get_tracer_cached.cache_clear()
        provider.shutdown()


def test_native_debug_override_does_not_mutate_client_rust(native):
    native.configure(logger=native.logger, logging_enable=True)
    native.read(logging_enable=False)
    assert not native.capture.records
    native.read()
    assert [record.levelno for record in native.capture.records] == [logging.DEBUG]
    native.capture.records.clear()
    native.configure(logger=native.logger)
    native.read(logging_enable=True)
    native.read()
    assert [record.levelno for record in native.capture.records] == [logging.DEBUG]


def test_native_default_logger_and_level_filter_rust(native, caplog):
    native.configure(enable_diagnostics_logging=True)
    with caplog.at_level(logging.INFO, logger="azure.cosmos.diagnostics"):
        native.read()
    assert [r.diagnostics for r in caplog.records if r.name == "azure.cosmos.diagnostics"] == [SUMMARY]
    native.configure(logger=native.logger, logging_enable=True)
    native.logger.setLevel(logging.INFO)
    native.read()
    assert not native.capture.records


def test_original_status_filter_accepts_native_error_summary_rust(native):
    # Reuse the original functional-test filter, not a summary-specific replacement.
    native.capture.addFilter(FilterStatusCode())
    native.read()
    assert not native.capture.records
    native.status = 404
    with pytest.raises(CosmosResourceNotFoundError) as error:
        native.read()
    assert len(native.capture.records) == 1
    record = native.capture.records[0]
    assert record.status_code == 404
    assert record.diagnostics == error.value.headers[HEADER] == SUMMARY


def test_legacy_and_native_share_error_filter_not_http_record_shape_rust(native):
    legacy_logger, legacy_capture = make_logger()
    legacy_capture.addFilter(FilterStatusCode())
    native.capture.addFilter(FilterStatusCode())
    policy = CosmosHttpLoggingPolicy(logger=legacy_logger, enable_diagnostics_logging=True)
    for status in (200, 404):
        request = PipelineRequest(
            HttpRequest(
                "GET",
                "https://alpha-bank.invalid/dbs/sales/colls/orders/docs/order-42",
                headers={"x-ms-thinclient-proxy-operation-type": "Read", "x-ms-thinclient-proxy-resource-type": "docs"},
            ),
            PipelineContext(None),
        )
        response = SimpleNamespace(
            status_code=status,
            headers={},
            text=lambda: '{"message":"Order not found"}',
        )
        policy.on_request(request)
        policy.on_response(request, PipelineResponse(request.http_request, response, request.context))
        native.status = status
        if status == 404:
            with pytest.raises(CosmosResourceNotFoundError):
                native.read()
        else:
            native.read()
    # The approved summary contract keeps filtering, not legacy HTTP record counts.
    assert [(r.levelno, r.status_code) for r in legacy_capture.records] == [(logging.INFO, 404)] * 2
    assert [(r.levelno, r.status_code) for r in native.capture.records] == [(logging.INFO, 404)]
    assert legacy_capture.records[0].operation_type == "Read"
    assert native.capture.records[0].operation_type == "read_item"


@pytest.mark.parametrize("status", [200, 404])
def test_handler_failure_preserves_native_result_rust(native, status, caplog):
    class BrokenHandler(logging.Handler):
        def emit(self, record):
            raise RuntimeError("customer output failed")

    native.logger.handlers = [BrokenHandler()]
    native.status = status
    with caplog.at_level(logging.WARNING, logger="azure.cosmos._telemetry"):
        if status == 404:
            with pytest.raises(CosmosResourceNotFoundError):
                native.read()
        else:
            assert native.read()["id"] == "order-42"
    assert "Rust diagnostic logging failed; operation result is unchanged" in caplog.text


def test_absent_summary_and_early_failure_do_not_invent_logs_rust(native):
    native.summary = None
    assert HEADER not in native.read().get_response_headers()
    assert not native.capture.records
    native.failure = ValueError("binding rejected request")
    with pytest.raises(ValueError, match="binding rejected"):
        native.read()
    assert not native.capture.records
    assert _telemetry._OPERATION.get() is None


def test_overlapping_calls_keep_logger_selection_rust(native):
    loggers = [make_logger() for _ in range(2)]

    async def run():
        return await asyncio.gather(
            *(
                native.container.read_item(
                    f"order-{index}",
                    partition_key="customer-17",
                    logger=logger,
                    timeout=10,
                )
                for index, (logger, _) in enumerate(loggers)
            )
        )

    if native.asynchronous:
        results = asyncio.run(run())
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(native.read, f"order-{index}", logger=logger, timeout=10)
                for index, (logger, _) in enumerate(loggers)
            ]
            results = [future.result() for future in futures]
    assert [row["id"] for row in results] == ["order-0", "order-1"]
    assert [len(capture.records) for _, capture in loggers] == [1, 1]
    assert not native.capture.records


def test_deferred_pages_log_each_available_summary_rust(feed):  # pylint: disable=redefined-outer-name
    logger, capture = make_logger()
    original = feed.binding.fetch_page_with_cursor.side_effect

    def page(*args, **kwargs):
        response = original(*args, **kwargs)
        return (*response[:4], SUMMARY)

    feed.binding.fetch_page_with_cursor.side_effect = page
    feed.binding.fetch_page_with_cursor_async.side_effect = page
    enabled = settings.tracing_enabled()
    settings.tracing_enabled = False
    try:
        pager = feed.proxy.read_all_items(logger=logger, logging_enable=True)
        assert not capture.records
        assert len(feed.collect(pager)) == 2
    finally:
        settings.tracing_enabled = enabled
    assert [r.levelno for r in capture.records] == [logging.DEBUG] * 4
    assert [r.diagnostics for r in capture.records] == [SUMMARY] * 4
    assert _telemetry._OPERATION.get() is None


@pytest.mark.parametrize("operation", ["list_databases", "query_databases", "list_containers", "query_containers"])
def test_metadata_pages_keep_per_call_logging_options_rust(native, monkeypatch, operation):
    native.configure()
    module = async_binding if native.asynchronous else sync_binding

    def page(*_args, **kwargs):
        assert not kwargs.get("include_attempts")
        key = "Databases" if operation.endswith("databases") else "DocumentCollections"
        return 200, 0, {}, json.dumps({key: [{"id": "sales"}]}).encode(), SUMMARY

    async def page_async(*args, **kwargs):
        return page(*args, **kwargs)

    monkeypatch.setattr(module, "_binding_function_by_name", lambda _: page_async if native.asynchronous else page)
    owner = native.client if operation.endswith("databases") else native.client.get_database_client("sales")
    method = getattr(owner, operation)
    args = ("SELECT * FROM c",) if operation.startswith("query") else ()
    pager = method(*args, logger=native.logger, logging_enable=True)
    assert not native.capture.records

    async def collect():
        return [item async for item in pager]

    rows = asyncio.run(collect()) if native.asynchronous else list(pager)
    assert [row["id"] for row in rows] == ["sales"]
    assert [(r.levelno, r.operation_type, r.diagnostics) for r in native.capture.records] == [
        (logging.DEBUG, operation, SUMMARY)
    ]
