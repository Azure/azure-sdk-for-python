# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Private Bite 15 proof: one Rust-backed write and locally inspected spans.

Set COSMOSDBCONNECTIONSTRING to an authorized test account. Database sales and
container orders must already exist with partition key /customerId. The sample
creates and removes one unique synthetic order; it never changes the resources.
OpenTelemetry, its SDK, and a rebuilt azure.cosmos._rust extension are required.
"""

import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid

from azure.core.settings import settings
from azure.cosmos import _rust
from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio._telemetry_poc import create_item_with_attempt_tracing
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


async def run_proof(exporter):
    order = {
        "id": "telemetry-bite15-" + uuid.uuid4().hex,
        "customerId": "telemetry-bite15",
        "total": 125.5,
    }
    # The selector is private migration scaffolding, not a customer-facing option.
    async with CosmosClient.from_connection_string(
        os.environ["COSMOSDBCONNECTIONSTRING"], _backend="rust"
    ) as client:
        container = client.get_database_client("sales").get_container_client("orders")
        properties = await container.read()
        if properties["partitionKey"]["paths"] != ["/customerId"]:
            raise ValueError("sales/orders must use partition key /customerId")
        exporter.clear()
        try:
            with trace.get_tracer("customer.checkout").start_as_current_span("checkout") as checkout:
                result = await create_item_with_attempt_tracing(
                    container, order, no_response=False, timeout=30
                )
            if result["id"] != order["id"]:
                raise AssertionError("The created order ID differs from the submitted ID")
            read = await container.read_item(order["id"], partition_key=order["customerId"])
            if read["total"] != order["total"]:
                raise AssertionError("The service backend did not return the saved order")
            trace_id = checkout.get_span_context().trace_id
            spans = [
                span for span in exporter.get_finished_spans()
                if span.context.trace_id == trace_id
            ]
            operations = [span for span in spans if span.name == "ContainerProxy.create_item"]
            attempts = [span for span in spans if span.name == "cosmosdb.request"]
            if len(operations) != 1:
                raise AssertionError("Expected exactly one create operation span")
            operation = operations[0]
            total = operation.attributes["cosmos.poc.request_count"]
            retained = operation.attributes["cosmos.poc.retained_request_count"]
            if not 0 < len(attempts) == retained <= total:
                raise AssertionError("This proof requires complete retained attempt records")
            if operation.parent.span_id != checkout.get_span_context().span_id:
                raise AssertionError("The operation must belong to checkout")
            for attempt in attempts:
                if attempt.parent.span_id != operation.context.span_id:
                    raise AssertionError("Attempts must be siblings under the create operation")
                if not operation.start_time <= attempt.start_time <= attempt.end_time <= operation.end_time:
                    raise AssertionError("Recorded attempts must fit within the create operation")
            evidence = {
                "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "binding": Path(_rust.__file__).name,
                "database": "sales",
                "container": "orders",
                "trace_id": f"{trace_id:032x}",
                "request_count": total,
                "retained_request_count": retained,
                "diagnostic_text_present": bool(
                    result.get_response_headers().get("x-ms-cosmos-sdk-diagnostics")
                ),
                "spans": [
                    {
                        "name": span.name,
                        "span_id": f"{span.context.span_id:016x}",
                        "parent_span_id": f"{span.parent.span_id:016x}" if span.parent else None,
                        "start_ns": span.start_time,
                        "end_ns": span.end_time,
                        "attributes": {
                            key: value for key, value in span.attributes.items()
                            if key.startswith("cosmos.poc.")
                        },
                    }
                    for span in spans
                ],
            }
        finally:
            operation_error = sys.exc_info()[1]
            try:
                await container.delete_item(order["id"], partition_key=order["customerId"])
            except CosmosResourceNotFoundError:
                if operation_error is None:
                    raise
            except Exception as cleanup_error:
                if operation_error is not None:
                    raise operation_error from cleanup_error
                raise
        evidence["test_order_deleted"] = True
        return evidence


def main():
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    settings.tracing_enabled = True
    settings.tracing_implementation = None
    try:
        evidence = asyncio.run(run_proof(exporter))
        if not provider.force_flush():
            raise RuntimeError("The local exporter did not flush successfully")
        print(json.dumps(evidence, indent=2))
    finally:
        provider.shutdown()


if __name__ == "__main__":
    main()
