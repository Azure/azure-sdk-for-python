# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Compiled-binding proofs for returned connection errors, deadlines and cancellation.

Use an authorized loopback Cosmos emulator in COSMOSDBCONNECTIONSTRING with
sales.orders already present, partitioned by /customerId. No resources are
created. Client-scoped Rust transport faults intercept every CreateItem before
forwarding it; this is not a physical socket outage or a Python binding mock.
Each unique synthetic order is checked absent before and after the call.
No spans are uploaded. Run in a fresh process with a rebuilt extension.

The timeout case retains the normal public settings and records which timer
wins. The binding-timeout case overrides only the prepared driver budget to
30 seconds while keeping the public/binding deadline at one second. That
test-only input seam isolates the outer timer; all driver calls and results
remain real. Cancellation waits for a confirmed create-transport fault hit.
"""

import argparse
import asyncio
from contextlib import nullcontext, suppress
from dataclasses import replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.parse import urlparse
from unittest.mock import patch
import uuid

from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _rust
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceNotFoundError
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

DELAY_MS = 3000
TIMEOUT_SECONDS = 1


def emulator_connection_string():
    connection = os.environ["COSMOSDBCONNECTIONSTRING"]
    fields = dict(part.split("=", 1) for part in connection.split(";") if "=" in part)
    endpoint = urlparse(fields.get("AccountEndpoint", ""))
    if endpoint.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("Failure proofs require an authorized loopback emulator")
    return connection


async def require_absent(container, order):
    try:
        await container.read_item(
            order["id"], partition_key=order["customerId"], timeout=10, tracing_options={"enabled": False}
        )
    except CosmosResourceNotFoundError:
        return
    raise AssertionError(
        "Faulted create unexpectedly stored its unique synthetic order; "
        f"manual reconciliation required for id={order['id']}, customerId={order['customerId']}"
    )


async def wait_for_hit(hit_count, task):
    expires = time.monotonic() + 10
    while hit_count() == 0:
        if task.done():
            await task
            raise AssertionError("Create finished without reaching the injected transport fault")
        if time.monotonic() >= expires:
            raise AssertionError("Create did not reach the injected transport fault in ten seconds")
        await asyncio.sleep(0.005)


def inspect_spans(exporter, trace_id, mode, failure, payload):
    spans = [s for s in exporter.get_finished_spans() if s.context.trace_id == trace_id]
    operations = [s for s in spans if s.name == "ContainerProxy.create_item"]
    attempts = [s for s in spans if s.name == "cosmosdb.request"]
    checkouts = [s for s in spans if s.name == "checkout"]
    if len(checkouts) != 1 or len(operations) != (1 if mode == "enabled" else 0):
        raise AssertionError("Unexpected checkout or operation span count")
    if operations:
        operation = operations[0]
        if operation.parent.span_id != checkouts[0].context.span_id:
            raise AssertionError("Operation is not a child of the measured checkout")
        if failure != "cancellation" and operation.status.status_code != trace.StatusCode.ERROR:
            raise AssertionError("Failed operation must have ERROR status")
    if mode == "enabled" and (failure == "connection" or payload is not None):
        if not isinstance(payload, dict) or payload["schema_version"] != 1 or payload["error"] is not None:
            raise AssertionError("Compiled exception must carry versioned diagnostics")
        records = payload["attempts"]
        if not 0 < len(records) == payload["retained_request_count"] <= payload["request_count"]:
            raise AssertionError("Connection proof requires retained request diagnostics")
        if failure == "connection" and any(r["end_ns"] is None for r in records):
            raise AssertionError("Connection proof requires completed attempts, not invented times")
        records = [r for r in records if r["end_ns"] is not None]
        for span in attempts:
            if span.parent.span_id != operation.context.span_id:
                raise AssertionError("Attempt is not attached to its own operation")
            if not operation.start_time <= span.start_time <= span.end_time <= operation.end_time:
                raise AssertionError("Attempt interval is outside its operation")
            if span.kind != trace.SpanKind.CLIENT:
                raise AssertionError("Request attempts must be CLIENT spans")
        actual_fields = sorted(
            (
                s.start_time,
                s.end_time,
                s.attributes["cosmos.poc.driver_status_code"],
                s.attributes["cosmos.poc.execution_context"],
            )
            for s in attempts
        )
        expected_fields = sorted(
            (r["start_ns"], r["end_ns"], r["driver_status_code"], r["execution_context"]) for r in records
        )
        if actual_fields != expected_fields:
            raise AssertionError("Attempt fields differ from the compiled binding diagnostics")
        for name in ("request_count", "retained_request_count"):
            if operation.attributes["cosmos.poc." + name] != payload[name]:
                raise AssertionError("Operation count differs from compiled diagnostics")
    elif attempts or payload is not None:
        raise AssertionError("Disabled or interrupted calls must not invent attempt data")
    return [
        {
            "name": s.name,
            "span_id": f"{s.context.span_id:016x}",
            "parent_span_id": f"{s.parent.span_id:016x}" if s.parent else None,
            "start_ns": s.start_time,
            "end_ns": s.end_time,
            "status": s.status.status_code.name,
            "attributes": {k: v for k, v in s.attributes.items() if k.startswith("cosmos.poc.")},
        }
        for s in spans
    ]


async def run_case(exporter, connection, failure, mode):
    rule_id = "telemetry-" + uuid.uuid4().hex
    order = {"id": rule_id, "customerId": rule_id, "total": 125.5}
    rule = {
        "id": rule_id,
        "operation_type": "CreateItem",
        "error_type": "ConnectionError",
        "delay_ms": 0 if failure == "connection" else DELAY_MS,
    }
    settings.tracing_enabled = mode != "global-disabled"
    async with CosmosClient.from_connection_string(
        connection,
        _backend="rust",
        _fault_injection_rules=[rule],
    ) as client:
        container = client.get_database_client("sales").get_container_client("orders")
        properties = await container.read()
        if properties["partitionKey"]["paths"] != ["/customerId"]:
            raise ValueError("sales.orders must be partitioned by /customerId")
        await require_absent(container, order)
        adapter = container._get_item_helper()._backend
        driver_handle = await adapter._ensure_driver_handle()

        def hits():
            return _rust._debug_fault_injection_rule_hit_count(driver_handle, rule_id)

        if hits() != 0:
            raise AssertionError("Setup unexpectedly consumed the create fault")
        exporter.clear()
        timeout = TIMEOUT_SECONDS if failure in ("timeout", "binding-timeout") else 30
        caught = None
        payload = None
        start = time.monotonic()
        with trace.get_tracer("customer.checkout").start_as_current_span("checkout") as checkout:

            async def create():
                options = {"enabled": False} if mode == "per-call-disabled" else {}
                return await container.create_item(order, timeout=timeout, tracing_options=options)

            original_prepare = adapter._with_client_headers

            def isolate_binding_deadline(prepared):
                prepared = original_prepare(prepared)
                return replace(prepared, settings=replace(prepared.settings, timeout_seconds=30))

            # Separate the two timers only in this named boundary test. No binding
            # call, driver result or diagnostic field is replaced by Python.
            deadline_scope = (
                patch.object(adapter, "_with_client_headers", side_effect=isolate_binding_deadline)
                if failure == "binding-timeout"
                else nullcontext()
            )
            with deadline_scope:
                task = asyncio.create_task(create())
                try:
                    if failure == "cancellation":
                        await wait_for_hit(hits, task)
                        task.cancel()
                    try:
                        await task
                    except (ServiceResponseError, CosmosClientTimeoutError, asyncio.CancelledError) as error:
                        caught = error
                    else:
                        raise AssertionError("Faulted create unexpectedly returned successfully")
                finally:
                    if not task.done():
                        task.cancel()
                        with suppress(asyncio.CancelledError):
                            await task
        elapsed = time.monotonic() - start
        expected = {
            "connection": (ServiceResponseError,),
            "timeout": (CosmosClientTimeoutError, ServiceResponseError),
            "binding-timeout": (CosmosClientTimeoutError,),
            "cancellation": (asyncio.CancelledError,),
        }[failure]
        if type(caught) not in expected:
            raise AssertionError(f"Unexpected public exception: {type(caught).__name__}") from caught
        cause = caught.__cause__
        payload = getattr(cause, "_cosmos_attempt_payload", None)
        timeout_source = None
        if type(caught) is ServiceResponseError:
            if not isinstance(cause, _rust._DriverTransportError):
                raise AssertionError("Expected the real compiled binding exception as cause")
            if failure == "timeout":
                if "408/20008" not in str(cause):
                    raise AssertionError("Public timeout returned a non-timeout driver failure")
                timeout_source = "returned_driver_result"
        elif failure in ("timeout", "binding-timeout"):
            if not isinstance(cause, TimeoutError):
                raise AssertionError("Expected binding TimeoutError as timeout cause")
            timeout_source = "binding_deadline"
        if hits() == 0:
            raise AssertionError("Failure happened before the intended create transport")
        if failure != "connection" and elapsed >= DELAY_MS / 1000:
            raise AssertionError("Interruption waited for the injected delay to finish")
        trace_id = checkout.get_span_context().trace_id
        spans = inspect_spans(exporter, trace_id, mode, failure, payload)
        hit_count = hits()
        if payload is not None and payload["request_count"] != hit_count:
            raise AssertionError("Recorded request count differs from actual transport fault hits")
        if failure != "connection":
            await asyncio.sleep(DELAY_MS / 1000 + 0.2)
            if hits() != hit_count:
                raise AssertionError("Driver continued retrying after interruption")
            if inspect_spans(exporter, trace_id, mode, failure, payload) != spans:
                raise AssertionError("Late telemetry appeared after interrupted operation completion")
        await require_absent(container, order)
        return {
            "failure": failure,
            "mode": mode,
            "elapsed_seconds": elapsed,
            "timeout_source": timeout_source,
            "driver_timeout_override_seconds": 30 if failure == "binding-timeout" else None,
            "public_exception": type(caught).__name__,
            "cause": type(cause).__name__ if cause else None,
            "fault_hits": hit_count,
            "order_absent": True,
            "trace_id": f"{trace_id:032x}",
            "spans": spans,
            "diagnostics": payload,
        }


async def run_proofs(exporter, failure):
    connection = emulator_connection_string()
    cases = []
    failures = ("connection", "timeout", "binding-timeout", "cancellation") if failure == "all" else (failure,)
    for selected in failures:
        group = []
        for mode in ("enabled", "per-call-disabled", "global-disabled"):
            group.append(await run_case(exporter, connection, selected, mode))
        if len({case["fault_hits"] for case in group}) != 1:
            raise AssertionError("Fault attempt counts changed with telemetry configuration")
        cases.extend(group)
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "binding": Path(_rust.__file__).name,
        "fault_mechanism": "Rust driver transport injection, before service send",
        "physical_socket_outage": False,
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--failure",
        choices=("all", "connection", "timeout", "binding-timeout", "cancellation"),
        default="all",
    )
    args = parser.parse_args()
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    settings.tracing_implementation = None
    try:
        evidence = asyncio.run(run_proofs(exporter, args.failure))
        if not provider.force_flush():
            raise RuntimeError("Local exporter did not flush")
        print(json.dumps(evidence, indent=2))
    finally:
        provider.shutdown()


if __name__ == "__main__":
    main()
