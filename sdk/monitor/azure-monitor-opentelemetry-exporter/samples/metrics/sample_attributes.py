# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using different attributes with instruments in the OpenTelemetry SDK.
Metrics created and recorded using the sdk are tracked and telemetry is exported to application insights
with the AzureMonitorMetricExporter.
"""
import os

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
# Metrics are reported every 1 minute
reader = PeriodicExportingMetricReader(exporter)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

attribute_set1 = {
    "key1": "val1"
}
attribute_set2 = {
    "key2": "val2"
}
large_attribute_set = {}
for i in range(20):
    key = "key{}".format(i)
    val = "val{}".format(i)
    large_attribute_set[key] = val

meter = metrics.get_meter_provider().get_meter("sample")

# Counter
counter = meter.create_counter("attr1_counter")
counter.add(1, attribute_set1)

# Counter2
counter2 = meter.create_counter("attr2_counter")
counter2.add(10, attribute_set1)
counter2.add(30, attribute_set2)

# Counter3
counter3 = meter.create_counter("large_attr_counter")
counter3.add(100, attribute_set1)
counter3.add(200, large_attribute_set)
