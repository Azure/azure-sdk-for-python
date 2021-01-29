# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# pylint: disable=import-error
# pylint: disable=no-member
# pylint: disable=no-name-in-module
import time

import requests
from opentelemetry import metrics
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider

from azure.opentelemetry.exporter.azuremonitor import AzureMonitorMetricsExporter

# Use the default sdk implementation
metrics.set_meter_provider(MeterProvider(stateful=False))

# Track telemetry from the requests library
RequestsInstrumentor().instrument()
meter = RequestsInstrumentor().meter
exporter = AzureMonitorMetricsExporter(
    connection_string="InstrumentationKey=<INSTRUMENTATION KEY HERE>"
)
# Export standard metrics from requests library to Azure Monitor
metrics.get_meter_provider().start_pipeline(meter, exporter, 5)

for x in range(10):
    for y in range(10):
        requests.get("http://example.com")
        time.sleep(2)
    time.sleep(5)

input("Press any key to exit...")
