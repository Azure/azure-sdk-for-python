# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from time import sleep

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics
from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricExporter,
    MetricsData,
    PeriodicExportingMetricReader,
)


class PrintMetricExporter(MetricExporter):
    """Minimal exporter that prints metric data."""

    def export(self, metrics_data: MetricsData, **kwargs) -> MetricExportResult:  # type: ignore[override]
        # In a real exporter, send metrics_data to your backend
        print(f"exported metrics: {metrics_data}")
        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis: float = 30000, **kwargs) -> None:  # type: ignore[override]
        return None

    def force_flush(self, timeout_millis: float = 30000, **kwargs) -> bool:  # type: ignore[override]
        return True


# Add a custom reader; the SDK will append its own Azure Monitor reader
custom_reader = PeriodicExportingMetricReader(
    PrintMetricExporter(),
    export_interval_millis=5000,
)

configure_azure_monitor(
    enable_performance_counters=False,
    metric_readers=[custom_reader],
)

meter = metrics.get_meter_provider().get_meter("metric-readers-sample")
counter = meter.create_counter("example.counter")

for _ in range(3):
    counter.add(1)
    sleep(1)
