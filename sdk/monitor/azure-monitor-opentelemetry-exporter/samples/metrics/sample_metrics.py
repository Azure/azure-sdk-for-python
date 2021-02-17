# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricsExporter

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)
exporter = AzureMonitorMetricsExporter(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
metrics.get_meter_provider().start_pipeline(meter, exporter, 5)

requests_counter = meter.create_counter(
    name="requests",
    description="number of requests",
    unit="1",
    value_type=int,
)

testing_labels = {"environment": "testing"}

requests_counter.add(25, testing_labels)

input("Press any key to exit...")
