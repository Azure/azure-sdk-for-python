# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Public Rust-backed create/read proof with locally inspected spans.

Set COSMOSDBCONNECTIONSTRING to an authorized test account. Database sales and
container orders must already exist with partition key /customerId. The sample
creates and removes one unique synthetic order; it never changes the resources.
Use --conflict for a setup create followed by a measured duplicate create.
Without that flag, the measured call is the original Bite 15 successful create.
Use --read for a successful read of the setup order, or --read-missing for
a read of a different, absent ID returning 404. Only the measured client
request is inspected or optionally exported.
OpenTelemetry, its SDK, and a rebuilt azure.cosmos._rust extension are required.
Use --azure-monitor to also export an allowlisted copy of the measured trace.
Install samples/requirements-telemetry.txt and set
APPLICATIONINSIGHTS_CONNECTION_STRING in the same terminal first. Local-only
remains the default. Export success is not proof of visibility in Azure.
"""

import argparse
import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
import threading
from typing import Optional, Sequence
import uuid

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from azure.core.settings import settings
from azure.cosmos import _rust
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError

_PROOF_RESOURCE = Resource(
    {
        "service.name": "cosmos-rust-telemetry-proof",
        "service.instance.id": "synthetic-proof",
    }
)
_PROOF_NAMES = frozenset(("checkout", "ContainerProxy.create_item", "ContainerProxy.read_item", "cosmosdb.request"))
_PROOF_ATTRIBUTES = frozenset(
    (
        "cosmos.poc.request_count",
        "cosmos.poc.retained_request_count",
        "cosmos.poc.driver_status_code",
        "cosmos.poc.execution_context",
    )
)
_LOGGER = logging.getLogger(__name__)


class MeasuredTraceExporter(SpanExporter):
    """Send only sanitized measured spans; retain export outcomes for the proof.

    :param delegate: Exporter receiving the sanitized spans.
    :type delegate: ~opentelemetry.sdk.trace.export.SpanExporter
    """

    def __init__(self, delegate: SpanExporter) -> None:
        self.delegate = delegate
        self.trace_id: Optional[int] = None
        self.exported = 0
        self.failed = False
        self._lock = threading.Lock()

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        selected = [
            ReadableSpan(
                name=span.name,
                context=span.context,
                parent=span.parent,
                resource=_PROOF_RESOURCE,
                kind=span.kind,
                start_time=span.start_time,
                end_time=span.end_time,
                status=trace.Status(span.status.status_code),
                attributes={k: v for k, v in span.attributes.items() if k in _PROOF_ATTRIBUTES},
            )
            for span in spans
            if span.context.trace_id == self.trace_id and span.name in _PROOF_NAMES
        ]
        if not selected:
            return SpanExportResult.SUCCESS
        try:
            result = self.delegate.export(selected)
        # Exporters may raise arbitrary errors containing private configuration.
        except Exception:  # pylint: disable=broad-exception-caught
            result = SpanExportResult.FAILURE
        with self._lock:
            if result == SpanExportResult.SUCCESS:
                self.exported += len(selected)
            else:
                self.failed = True
                _LOGGER.error("Azure trace export failed; destination visibility is not established.")
        return result

    def verify(self, expected_count: int) -> None:
        with self._lock:
            if self.failed or self.exported != expected_count:
                raise RuntimeError(
                    f"Azure export incomplete: {self.exported}/{expected_count} spans reported successful; "
                    "check exporter diagnostics and destination access. Do not rerun a database write "
                    "just to retry telemetry."
                )

    def shutdown(self) -> None:
        self.delegate.shutdown()


def configure_recording(
    azure_monitor: bool = False,
) -> tuple[TracerProvider, InMemorySpanExporter, Optional[MeasuredTraceExporter]]:
    azure_exporter = None
    if azure_monitor:
        connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
        if not connection_string:
            raise ValueError(
                "--azure-monitor requires APPLICATIONINSIGHTS_CONNECTION_STRING in this process. "
                "Set it locally in the same terminal; do not paste it into chat."
            )
        # This standalone proof sends traces only, not exporter health/resource metrics.
        for name in (
            "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL",
            "APPLICATIONINSIGHTS_SDKSTATS_DISABLED",
            "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED",
            "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED",
        ):
            os.environ[name] = "true"
        from azure.monitor.opentelemetry.exporter import (
            ApplicationInsightsSampler,
            AzureMonitorTraceExporter,
        )

        provider = TracerProvider(resource=_PROOF_RESOURCE, sampler=ApplicationInsightsSampler(1.0))
        try:
            delegate = AzureMonitorTraceExporter(
                connection_string=connection_string,
                disable_offline_storage=True,
                tracer_provider=provider,
            )
        except Exception:
            provider.shutdown()
            raise ValueError(
                "Could not initialize Azure export; check local connection string and authentication."
            ) from None
        azure_exporter = MeasuredTraceExporter(delegate)
        provider.add_span_processor(BatchSpanProcessor(azure_exporter))
    else:
        provider = TracerProvider()
    local_exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(local_exporter))
    return provider, local_exporter, azure_exporter


async def run_proof(exporter, *, conflict=False, read=False, not_found=False, azure_exporter=None):
    if (not_found and not read) or (conflict and read):
        raise ValueError("A read proof cannot measure a create conflict; not_found requires read")
    proof_name = "telemetry-bite26" if read else ("telemetry-bite22" if conflict else "telemetry-bite15")
    operation_name = "ContainerProxy.read_item" if read else "ContainerProxy.create_item"
    expected_driver_status = 404 if not_found else (200 if read else (409 if conflict else 201))
    failed = conflict or not_found
    order = {
        "id": proof_name + "-" + uuid.uuid4().hex,
        "customerId": proof_name,
        "total": 125.5,
    }
    # The selector is private migration scaffolding, not a customer-facing option.
    async with CosmosClient.from_connection_string(os.environ["COSMOSDBCONNECTIONSTRING"], _backend="rust") as client:
        container = client.get_database_client("sales").get_container_client("orders")
        properties = await container.read()
        if properties["partitionKey"]["paths"] != ["/customerId"]:
            raise ValueError("sales/orders must use partition key /customerId")
        created = False
        public_exception = None
        try:
            if conflict or read:
                await container.create_item(order, no_response=False, timeout=30, tracing_options={"enabled": False})
                created = True
            exporter.clear()
            with trace.get_tracer("customer.checkout").start_as_current_span("checkout") as checkout:
                if azure_exporter is not None:
                    azure_exporter.trace_id = checkout.get_span_context().trace_id
                try:
                    if read:
                        target = order["id"] + "-missing" if not_found else order["id"]
                        result = await container.read_item(target, partition_key=order["customerId"], timeout=30)
                    else:
                        result = await container.create_item(order, no_response=False, timeout=30)
                        created = True
                except (CosmosResourceExistsError, CosmosResourceNotFoundError) as error:
                    if not failed or error.status_code != expected_driver_status:
                        raise
                    response_headers = error.headers
                    public_exception = type(error).__name__
                else:
                    if failed:
                        raise AssertionError("The expected failing operation unexpectedly succeeded")
                    if result["id"] != order["id"]:
                        raise AssertionError("The returned order ID differs from the expected ID")
                    if read and any(result[key] != value for key, value in order.items()):
                        raise AssertionError("The measured read did not return the saved order")
                    response_headers = result.get_response_headers()
            saved = await container.read_item(
                order["id"], partition_key=order["customerId"], tracing_options={"enabled": False}
            )
            if any(saved[key] != value for key, value in order.items()):
                raise AssertionError("The service backend did not return the saved order")
            trace_id = checkout.get_span_context().trace_id
            spans = [span for span in exporter.get_finished_spans() if span.context.trace_id == trace_id]
            operations = [span for span in spans if span.name == operation_name]
            attempts = [span for span in spans if span.name == "cosmosdb.request"]
            if len(operations) != 1:
                raise AssertionError("Expected exactly one measured operation span")
            operation = operations[0]
            expected_status = trace.StatusCode.ERROR if failed else trace.StatusCode.UNSET
            if operation.status.status_code is not expected_status:
                raise AssertionError("The operation span status differs from the public outcome")
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
                if attempt.kind is not trace.SpanKind.CLIENT:
                    raise AssertionError("Expected a client attempt span")
            terminal = max(attempts, key=lambda span: span.end_time)
            if terminal.attributes["cosmos.poc.driver_status_code"] != expected_driver_status:
                raise AssertionError("The last completed attempt has an unexpected driver status")
            if not response_headers.get("x-ms-cosmos-sdk-diagnostics"):
                raise AssertionError("The response must retain diagnostic text")
            evidence = {
                "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "binding": Path(_rust.__file__).name,
                "database": "sales",
                "container": "orders",
                "mode": "read-missing" if not_found else ("read" if read else ("conflict" if conflict else "success")),
                "public_exception": public_exception,
                "expected_status": expected_driver_status,
                "saved_order_verified": True,
                "trace_id": f"{trace_id:032x}",
                "request_count": total,
                "retained_request_count": retained,
                "diagnostic_text_present": bool(response_headers.get("x-ms-cosmos-sdk-diagnostics")),
                "spans": [
                    {
                        "name": span.name,
                        "span_id": f"{span.context.span_id:016x}",
                        "parent_span_id": f"{span.parent.span_id:016x}" if span.parent else None,
                        "start_ns": span.start_time,
                        "end_ns": span.end_time,
                        "status": span.status.status_code.name,
                        "attributes": {
                            key: value for key, value in span.attributes.items() if key.startswith("cosmos.poc.")
                        },
                    }
                    for span in spans
                ],
            }
        finally:
            operation_error = sys.exc_info()[1]
            if created:
                try:
                    await container.delete_item(order["id"], partition_key=order["customerId"])
                    try:
                        await container.read_item(order["id"], partition_key=order["customerId"])
                    except CosmosResourceNotFoundError:
                        pass
                    else:
                        raise AssertionError("The synthetic order still exists after deletion")
                except Exception as cleanup_error:
                    if operation_error is not None:
                        raise operation_error from cleanup_error
                    raise
            elif operation_error is not None:
                print(
                    f"Create ownership was not confirmed; no delete attempted for "
                    f"id={order['id']}, customerId={order['customerId']}.",
                    file=sys.stderr,
                )
        evidence["test_order_deleted"] = True
        return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--conflict", action="store_true", help="Measure a duplicate create returning 409")
    mode.add_argument("--read", action="store_true", help="Measure a read of the setup order returning 200")
    mode.add_argument("--read-missing", action="store_true", help="Measure a read of an absent ID returning 404")
    parser.add_argument("--azure-monitor", action="store_true", help="Also send the sanitized measured trace to Azure")
    args = parser.parse_args()
    provider, exporter, azure_exporter = configure_recording(args.azure_monitor)
    trace.set_tracer_provider(provider)
    settings.tracing_enabled = True
    settings.tracing_implementation = None
    try:
        evidence = asyncio.run(
            run_proof(
                exporter,
                conflict=args.conflict,
                read=args.read or args.read_missing,
                not_found=args.read_missing,
                azure_exporter=azure_exporter,
            )
        )
        # Preserve the local proof and correlation ID even if delivery fails.
        print(json.dumps(evidence, indent=2), flush=True)
        if not provider.force_flush():
            raise RuntimeError("Span processors did not flush successfully; Azure visibility is unverified.")
        if azure_exporter is not None:
            azure_exporter.verify(len(evidence["spans"]))
            print(
                f"Azure exporter reported success for {azure_exporter.exported} measured spans. "
                f"Verify operation_Id == '{evidence['trace_id']}' in Application Insights Logs; "
                "ingestion visibility has not yet been checked.",
                file=sys.stderr,
            )
    finally:
        provider.shutdown()


if __name__ == "__main__":
    main()
