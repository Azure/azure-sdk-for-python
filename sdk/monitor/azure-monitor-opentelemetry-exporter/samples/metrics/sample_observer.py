# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import psutil
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricsExporter

metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)
exporter = AzureMonitorMetricsExporter(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
metrics.get_meter_provider().start_pipeline(meter, exporter, 2)


# Callback to gather cpu usage
def get_cpu_usage_callback(observer):
    for (number, percent) in enumerate(psutil.cpu_percent(percpu=True)):
        labels = {"cpu_number": str(number)}
        observer.observe(percent, labels)


meter.register_updownsumobserver(
    callback=get_cpu_usage_callback,
    name="cpu_percent",
    description="per-cpu usage",
    unit="1",
    value_type=float,
    label_keys=("cpu_number",),
)


# Callback to gather RAM memory usage
def get_ram_usage_callback(observer):
    ram_percent = psutil.virtual_memory().percent
    observer.observe(ram_percent, {})


meter.register_updownsumobserver(
    callback=get_ram_usage_callback,
    name="ram_percent",
    description="RAM memory usage",
    unit="1",
    value_type=float,
    label_keys=(),
)

input("Press any key to exit...")
