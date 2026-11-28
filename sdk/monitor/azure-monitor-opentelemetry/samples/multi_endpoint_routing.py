# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Route logs, spans, events, and metrics to two trusted Application Insights resources.

Replace the example instrumentation keys and ingestion endpoints in destinations
with each resource's InstrumentationKey and IngestionEndpoint connection-string values.
"""

import os
from logging import INFO, getLogger

from opentelemetry import metrics, trace

from azure.monitor.opentelemetry._configure import configure_azure_monitor


def main() -> None:
    os.environ["APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES"] = "multi_endpoint_routing"
    # Live Metrics needs a host connection string, unlike per-item routing.
    configure_azure_monitor(logger_name=__name__, sampling_ratio=1.0, enable_live_metrics=False)

    destinations = [
        {
            "microsoft.instrumentation_key": "363331ca-f431-4119-bdcd-31a75920f958",
            "microsoft.ingestion_endpoint": "https://eastus-8.in.applicationinsights.azure.com/",
            "microsoft.multi_endpoint_cloud_role": "routing-destination-1",
        },
        {
            "microsoft.instrumentation_key": "6a64694d-b7be-4dff-af27-ea70f53c9ea2",
            "microsoft.ingestion_endpoint": "https://australiaeast-1.in.applicationinsights.azure.com/",
            "microsoft.multi_endpoint_cloud_role": "routing-destination-2",
        },
    ]
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    tracer = trace.get_tracer(__name__)
    counter = metrics.get_meter(__name__).create_counter("routed_operations")

    for destination in destinations:
        with tracer.start_as_current_span(
            "routed-operation", kind=trace.SpanKind.SERVER, attributes=destination
        ) as span:
            # Events inherit the span's route; logs and measurements need their own attributes.
            span.add_event("Routed event")
            logger.info("Routed log", extra=destination)
            counter.add(1, attributes=destination)

    input("Press Enter to exit.\n")


if __name__ == "__main__":
    main()
