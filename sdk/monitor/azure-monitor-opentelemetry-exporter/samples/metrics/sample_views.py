# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
This example shows how to customize the metrics that are output by the SDK using Views. Metrics created
and recorded using the sdk are tracked and telemetry is exported to application insights with the
AzureMonitorMetricExporter.
"""
import os

from opentelemetry import metrics
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
# Create a view matching the counter instrument `my.counter`
# and configure the new name `my.counter.total` for the result metrics stream
change_metric_name_view = View(
    instrument_type=Counter,
    instrument_name="my.counter",
    name="my.counter.total",
)
# Metrics are reported every 1 minute
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(
    metric_readers=[
        reader,
    ],
    views=[
        change_metric_name_view,
    ],
)
metrics.set_meter_provider(provider)

meter = metrics.get_meter_provider().get_meter("view-name-change")
my_counter = meter.create_counter("my.counter")
my_counter.add(100)
