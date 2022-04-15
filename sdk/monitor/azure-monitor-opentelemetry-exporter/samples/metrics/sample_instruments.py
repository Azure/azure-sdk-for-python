# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using all instruments in the OpenTelemetry SDK. Metrics created
and recorded using the sdk are tracked and telemetry is exported to application insights with the
AzureMonitorMetricsExporter.
"""
import os

from opentelemetry import _metrics
from opentelemetry._metrics.measurement import Measurement
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

# Callback functions for observable instruments
def observable_counter_func():
    yield Measurement(1, {})


def observable_up_down_counter_func():
    yield Measurement(-10, {})


def observable_gauge_func():
    yield Measurement(9, {})

# Counter
counter = meter.create_counter("counter")
counter.add(1)

# Async Counter
observable_counter = meter.create_observable_counter(
    "observable_counter", observable_counter_func
)

# UpDownCounter
updown_counter = meter.create_up_down_counter("updown_counter")
updown_counter.add(1)
updown_counter.add(-5)

# Async UpDownCounter
observable_updown_counter = meter.create_observable_up_down_counter(
    "observable_updown_counter", observable_up_down_counter_func
)

# Histogram
histogram = meter.create_histogram("histogram")
histogram.record(99.9)

# Async Gauge
gauge = meter.create_observable_gauge("gauge", observable_gauge_func)

input(...)