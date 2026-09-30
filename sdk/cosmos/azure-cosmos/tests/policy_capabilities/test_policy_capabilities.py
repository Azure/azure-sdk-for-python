# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare policy capabilities without mistaking client startup for item work.

Set COSMOS_POLICY_AUDIT_BACKEND to core-python or rust and save each pytest
transcript. Failures are retained, not xfailed. The filtered-logging read and
assertions are adapted from the original sync/async logging functional tests;
their unrelated invalid-create and other-operation cases are not included.
"""

import asyncio
import importlib
from contextlib import contextmanager
import json
import logging
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._retry_utility import ConnectionRetryPolicy
from azure.cosmos.aio._retry_utility_async import _ConnectionRetryPolicy
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.documents import ConnectionPolicy
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from test_config import MockHandler
from test_cosmos_http_logging_policy import FilterStatusCode


@pytest.fixture(scope="module")
def backend():
    selected = os.environ.get("COSMOS_POLICY_AUDIT_BACKEND")
    if selected not in ("core-python", "rust"):
        pytest.skip("Set COSMOS_POLICY_AUDIT_BACKEND explicitly for the live policy audit")
    if not os.environ.get("ACCOUNT_HOST") or not os.environ.get("ACCOUNT_KEY"):
        pytest.skip("A configured account is required")
    return selected


@pytest.fixture(scope="module")
def saved_order(backend):
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as client:
        database = client.create_database("policy_audit_" + uuid.uuid4().hex)
        print(f"\nOwned policy-test database: {database.id}")
        try:
            container = database.create_container("orders", partition_key=PartitionKey(path="/customerId"))
            order = container.create_item({"id": "order-42", "customerId": "customer-17", "status": "paid"})
            yield database.id, dict(order)
        finally:
            client.delete_database(database.id)
            with pytest.raises(CosmosResourceNotFoundError) as deleted:
                database.read()
            assert deleted.value.status_code == 404
            print("\nPOLICY-CLEANUP " + json.dumps({"database": database.id, "status": 404}))


@contextmanager
def tracing():
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from azure.core import instrumentation
    from azure.core.settings import settings
    from unittest.mock import patch

    enabled, implementation = settings.tracing_enabled(), settings.tracing_implementation()
    provider, exporter = TracerProvider(), InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    settings.tracing_enabled, settings.tracing_implementation = True, None
    try:
        with patch.object(trace, "get_tracer_provider", return_value=provider):
            instrumentation._get_tracer_cached.cache_clear()
            yield exporter
    finally:
        settings.tracing_enabled, settings.tracing_implementation = enabled, implementation
        instrumentation._get_tracer_cached.cache_clear()
        provider.shutdown()


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("capability", [
    "raw_request_default", "raw_response_default", "http_logging", "diagnostic_logging",
    "filtered_logging", "network_span_namer", "connection_retry_policy",
    "headers_default", "headers_per_call",
])
def test_policy_capability(backend, saved_order, asynchronous, capability, monkeypatch):
    database_id, expected = saved_order
    events, prepared_headers = [], []
    handler = MockHandler()
    logger = logging.getLogger("policy-audit-" + uuid.uuid4().hex)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    target_id = "nonexistent_item" if capability == "filtered_logging" else expected["id"]
    target_path = f"/dbs/{database_id}/colls/orders/docs/{target_id}"

    def is_target(request):
        return request.url.split("?", 1)[0].rstrip("/").endswith(target_path)

    def request_hook(request):
        if is_target(request.http_request):
            events.append(("request", request.http_request.headers.get("x-alpha-bank-operation-id")))

    def response_hook(response):
        if is_target(response.http_request):
            events.append(("response", response.http_response.status_code))

    def span_namer(request):
        if is_target(request):
            events.append(("span_name", request.method))
        return "alpha-bank-http"

    class RetryPolicy(ConnectionRetryPolicy):
        def send(self, request):
            if is_target(request.http_request):
                events.append(("retry_policy", request.http_request.method))
            return super().send(request)

    class AsyncRetryPolicy(_ConnectionRetryPolicy):
        async def send(self, request):
            if is_target(request.http_request):
                events.append(("retry_policy", request.http_request.method))
            return await super().send(request)

    settings = {"logger": logger}
    operation_settings = {}
    if capability in ("raw_request_default", "headers_default", "headers_per_call"):
        settings["raw_request_hook"] = request_hook
    if capability == "raw_response_default":
        settings["raw_response_hook"] = response_hook
    if capability in ("diagnostic_logging", "filtered_logging"):
        settings["enable_diagnostics_logging"] = True
    if capability == "filtered_logging":
        handler.addFilter(FilterStatusCode())
    if capability == "network_span_namer":
        settings["network_span_namer"] = span_namer
        settings["tracing_attributes"] = {"alpha_bank.operation": "read-order-42"}
    if capability == "connection_retry_policy":
        if asynchronous:
            policy = ConnectionPolicy()
            policy.ConnectionRetryConfiguration = AsyncRetryPolicy()
            settings["connection_policy"] = policy
        else:
            settings["connection_retry_policy"] = RetryPolicy()
    if capability == "headers_default":
        settings["headers"] = {"x-alpha-bank-operation-id": "read-order-42"}
    if capability == "headers_per_call":
        operation_settings["initial_headers"] = {"x-alpha-bank-operation-id": "read-order-42"}
    observed = {}

    def prepare(client, exporter):
        assert client.client_connection._backend.name == backend
        if backend == "rust":
            binding = importlib.import_module(type(client._adapter).__module__)._rust_module
            method = "read_item_async" if asynchronous else "read_item"
            original = getattr(binding, method)

            async def async_execute(driver_handle, prepared, **kwargs):
                prepared_headers.append(dict(prepared.headers))
                return await original(driver_handle, prepared, **kwargs)

            def execute(driver_handle, prepared, **kwargs):
                prepared_headers.append(dict(prepared.headers))
                return original(driver_handle, prepared, **kwargs)

            monkeypatch.setattr(binding, method, async_execute if asynchronous else execute)
        handler.reset()
        events.clear()
        exporter.clear()
        observed["counters_before"] = (_binding_operation_count(), _rust_fallback_count())

    def finish(exporter, result, error):
        before = observed.pop("counters_before")
        observed.update({
            "capability": capability, "backend": backend, "surface": "aio" if asynchronous else "sync",
            "status": error.status_code if error else 200,
            "native_operation_delta": _binding_operation_count() - before[0],
            "fallback_delta": _rust_fallback_count() - before[1],
            "events": list(events),
            "target_log_records": sum(target_path in record.getMessage() for record in handler.messages),
            "diagnostic_records": sum(getattr(record, "resource_type", None) == "docs" for record in handler.messages),
            "operation_spans": sum(span.name == "ContainerProxy.read_item" for span in exporter.get_finished_spans()),
            "named_network_spans": sum(span.name == "alpha-bank-http" for span in exporter.get_finished_spans()),
            "attributed_network_spans": sum(
                span.name == "alpha-bank-http"
                and span.attributes.get("alpha_bank.operation") == "read-order-42"
                for span in exporter.get_finished_spans()
            ),
            "prepared_application_headers": [
                headers.get("x-alpha-bank-operation-id") for headers in prepared_headers
            ],
        })
        assert observed["fallback_delta"] == 0
        assert (observed["native_operation_delta"] > 0) if backend == "rust" else (
            observed["native_operation_delta"] == 0
        )
        if capability == "filtered_logging":
            assert isinstance(error, CosmosResourceNotFoundError) and error.status_code == 404
        else:
            assert error is None
            assert dict(result) == expected
        print("\nPOLICY-CAPTURE " + json.dumps(observed))

    async def run_async(exporter):
        async with AsyncCosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend, **settings,
        ) as client:
            container = client.get_database_client(database_id).get_container_client("orders")
            prepare(client, exporter)
            result, error = None, None
            try:
                result = await container.read_item(target_id, partition_key="customer-17", **operation_settings)
            except CosmosResourceNotFoundError as exc:
                error = exc
            finish(exporter, result, error)

    try:
        with tracing() as exporter:
            if asynchronous:
                asyncio.run(run_async(exporter))
            else:
                with CosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend, **settings,
                ) as client:
                    container = client.get_database_client(database_id).get_container_client("orders")
                    prepare(client, exporter)
                    result, error = None, None
                    try:
                        result = container.read_item(target_id, partition_key="customer-17", **operation_settings)
                    except CosmosResourceNotFoundError as exc:
                        error = exc
                    finish(exporter, result, error)
    finally:
        logger.removeHandler(handler)
        handler.close()

    if capability in ("raw_request_default", "raw_response_default", "connection_retry_policy"):
        assert events, f"{capability} did not run for the item request"
    elif capability == "network_span_namer":
        assert observed["operation_spans"] == 1
        assert events and observed["named_network_spans"] > 0
        assert observed["attributed_network_spans"] == observed["named_network_spans"]
    elif capability in ("headers_default", "headers_per_call"):
        actual = prepared_headers[-1].get("x-alpha-bank-operation-id") if backend == "rust" else events[-1][1]
        assert actual == "read-order-42"
    elif capability == "filtered_logging":
        # Preserve the missing-item logging assertions from both original tests.
        assert len(handler.messages) == 2
        request_log = handler.messages[0]
        response_log = handler.messages[1]
        assert response_log.status_code == 404
        assert request_log.resource_type == "docs"
        assert request_log.operation_type == "Read"
        assert len(handler.messages) == 2
    else:
        assert observed["target_log_records"] > 0
        if capability == "diagnostic_logging":
            assert observed["diagnostic_records"] > 0
