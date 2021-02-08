# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from azure.opentelemetry.exporter.azuremonitor import AzureMonitorMetricsExporter
from azure.opentelemetry.sdk.azuremonitor.auto_collection import AutoCollection

# Add Span Processor to get metrics about traces
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer_provider().get_tracer(__name__)

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)
exporter = AzureMonitorMetricsExporter(
    connection_string="InstrumentationKey=<INSTRUMENTATION KEY HERE>"
)

testing_label_set = {"environment": "testing"}

# Automatically collect performance counters
auto_collection = AutoCollection(meter=meter, labels=testing_label_set)

metrics.get_meter_provider().start_pipeline(meter, exporter, 2)

input("Press any key to exit...")
