# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer Statsbeat implementation for Azure Monitor OpenTelemetry Exporter.

This module provides the implementation for collecting and reporting customer statsbeat
metrics that track the usage and performance of the Azure Monitor OpenTelemetry Exporter.
"""

from typing import List, Dict, Any, Iterable
import os

from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    CustomerStatsbeatProperties,
    #DropCode,
    #RetryCode,
    CustomerStatsbeatMetricName,
    _CUSTOMER_STATSBEAT_LANGUAGE,
)

from azure.monitor.opentelemetry.exporter.statsbeat._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter._utils import (
    Singleton,
    get_compute_type,
)

from azure.monitor.opentelemetry.exporter import VERSION

class _CustomerStatsbeatTelemetryCounters:
    def __init__(self):
        self.total_item_success_count: Dict[str, Any] = {}

class CustomerStatsbeatMetrics(metaclass=Singleton):
    def __init__(self, options):
        self._counters = _CustomerStatsbeatTelemetryCounters()
        self._language = _CUSTOMER_STATSBEAT_LANGUAGE
        self._is_enabled = os.environ.get(_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW, "").lower() in ("true")
        if not self._is_enabled:
            return

        exporter_config = {
            "connection_string": options.connection_string,
        }
        self._customer_statsbeat_exporter = AzureMonitorMetricExporter(**exporter_config)
        metric_reader_options = {
            "exporter": self._customer_statsbeat_exporter,
            "export_interval_millis": _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
        }
        self._customer_statsbeat_metric_reader = PeriodicExportingMetricReader(**metric_reader_options)
        self._customer_statsbeat_meter_provider = MeterProvider(
            metric_readers=[self._customer_statsbeat_metric_reader]
        )
        self._customer_statsbeat_meter = self._customer_statsbeat_meter_provider.get_meter(__name__)
        self._customer_properties = CustomerStatsbeatProperties(
            language=self._language,
            version=VERSION,
            compute_type=get_compute_type(),
        )
        self._success_gauge = self._customer_statsbeat_meter.create_observable_gauge(
            name=CustomerStatsbeatMetricName.ITEM_SUCCESS_COUNT.value,
            description="Tracks successful telemetry items sent to Azure Monitor",
            callbacks=[self._item_success_callback]
        )

    def count_successful_items(self, count: int, telemetry_type: str) -> None:
        if not self._is_enabled or count <= 0:
            return
        if telemetry_type in self._counters.total_item_success_count:
            self._counters.total_item_success_count[telemetry_type] += count
        else:
            self._counters.total_item_success_count[telemetry_type] = count

    def _item_success_callback(self, options: CallbackOptions) -> Iterable[Observation]: # pylint: disable=unused-argument
        if not getattr(self, "_is_enabled", False):
            return []

        observations: List[Observation] = []
        for telemetry_type, count in self._counters.total_item_success_count.items():
            attributes = {
                "language": self._customer_properties.language,
                "version": self._customer_properties.version,
                "compute_type": self._customer_properties.compute_type,
                "telemetry_type": telemetry_type
            }
            observations.append(Observation(count, dict(attributes)))

        return observations
