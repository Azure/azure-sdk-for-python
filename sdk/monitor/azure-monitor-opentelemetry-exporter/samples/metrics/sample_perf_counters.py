# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricsExporter
from azure.monitor.opentelemetry.sdk.auto_collection import AutoCollection

# Add Span Processor to get metrics about traces
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer_provider().get_tracer(__name__)

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)
exporter = AzureMonitorMetricsExporter(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

testing_label_set = {"environment": "testing"}

# Automatically collect performance counters
auto_collection = AutoCollection(meter=meter, labels=testing_label_set)

metrics.get_meter_provider().start_pipeline(meter, exporter, 2)

input("Press any key to exit...")
