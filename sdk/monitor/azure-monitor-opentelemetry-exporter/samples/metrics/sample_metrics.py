# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry metrics sdk. Metrics created and recorded using the
sdk are tracked and telemetry is exported to application insights with the AzureMonitorMetricsExporter.
"""
import os

from opentelemetry import _metrics
from opentelemetry.sdk._metrics import MeterProvider
from opentelemetry.sdk._metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
_metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

# Create a namespaced meter
meter = _metrics.get_meter_provider().get_meter("sample")

# Create Counter instrument with the meter
counter = meter.create_counter("counter")
counter.add(1)
