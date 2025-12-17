# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer SDKStats implementation for Azure Monitor OpenTelemetry Exporter.

This module provides the implementation for collecting and reporting Customer SDKStats
metrics that track the usage and performance of the Azure Monitor OpenTelemetry Exporter.
"""

import threading
from typing import List, Dict, Any, Iterable, Optional
import os

from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW,
    CustomerSdkStatsProperties,
    DropCode,
    DropCodeType,
    RetryCode,
    RetryCodeType,
    CustomerSdkStatsMetricName,
    _CUSTOMER_SDKSTATS_LANGUAGE,
)

from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter._utils import (
    Singleton,
    get_compute_type,
)

from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    categorize_status_code,
    _get_customer_sdkstats_export_interval,
)
from azure.monitor.opentelemetry.exporter import VERSION

from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _CUSTOMER_SDKSTATS_STATE,
    _CUSTOMER_SDKSTATS_STATE_LOCK,
)


class _CustomerSdkStatsTelemetryCounters:
    def __init__(self):
        self.total_item_success_count: Dict[str, Any] = {}
        self.total_item_drop_count: Dict[str, Dict[DropCodeType, Dict[str, int]]] = {}
        self.total_item_retry_count: Dict[str, Dict[RetryCodeType, Dict[str, int]]] = {}


class CustomerSdkStatsMetrics(metaclass=Singleton):  # pylint: disable=too-many-instance-attributes
    def __init__(self, connection_string):
        self._counters = _CustomerSdkStatsTelemetryCounters()
        self._language = _CUSTOMER_SDKSTATS_LANGUAGE
        self._is_enabled = os.environ.get(_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW, "").lower() in ("true")
        if not self._is_enabled:
            return

        exporter_config = {
            "connection_string": connection_string,
            "instrumentation_collection": True,  # Prevent circular dependency
        }

        self._customer_sdkstats_exporter = AzureMonitorMetricExporter(**exporter_config)
        self._customer_sdkstats_exporter._is_customer_sdkstats = True
        metric_reader_options = {
            "exporter": self._customer_sdkstats_exporter,
            "export_interval_millis": _get_customer_sdkstats_export_interval(),
        }
        self._customer_sdkstats_metric_reader = PeriodicExportingMetricReader(**metric_reader_options)
        self._customer_sdkstats_meter_provider = MeterProvider(metric_readers=[self._customer_sdkstats_metric_reader])
        self._customer_sdkstats_meter = self._customer_sdkstats_meter_provider.get_meter(__name__)

        self._customer_properties = CustomerSdkStatsProperties(
            language=self._language,
            version=VERSION,
            compute_type=get_compute_type(),
        )

        self._success_gauge = self._customer_sdkstats_meter.create_observable_gauge(
            name=CustomerSdkStatsMetricName.ITEM_SUCCESS_COUNT.value,
            description="Tracks successful telemetry items sent to Azure Monitor",
            callbacks=[self._item_success_callback],
        )
        self._dropped_gauge = self._customer_sdkstats_meter.create_observable_gauge(
            name=CustomerSdkStatsMetricName.ITEM_DROP_COUNT.value,
            description="Tracks dropped telemetry items sent to Azure Monitor",
            callbacks=[self._item_drop_callback],
        )
        self._retry_gauge = self._customer_sdkstats_meter.create_observable_gauge(
            name=CustomerSdkStatsMetricName.ITEM_RETRY_COUNT.value,
            description="Tracks retry attempts for telemetry items sent to Azure Monitor",
            callbacks=[self._item_retry_callback],
        )

    def count_successful_items(self, count: int, telemetry_type: str) -> None:
        if not self._is_enabled or count <= 0:
            return

        if telemetry_type in self._counters.total_item_success_count:
            self._counters.total_item_success_count[telemetry_type] += count
        else:
            self._counters.total_item_success_count[telemetry_type] = count

    def count_dropped_items(
        self, count: int, telemetry_type: str, drop_code: DropCodeType, exception_message: Optional[str] = None
    ) -> None:
        if not self._is_enabled or count <= 0:
            return

        # Get or create the drop_code map for this telemetry_type
        if telemetry_type not in self._counters.total_item_drop_count:
            self._counters.total_item_drop_count[telemetry_type] = {}
        drop_code_map = self._counters.total_item_drop_count[telemetry_type]

        # Get or create the reason map for this drop_code
        if drop_code not in drop_code_map:
            drop_code_map[drop_code] = {}
        reason_map = drop_code_map[drop_code]

        # Generate a low-cardinality, informative reason description
        reason = self._get_drop_reason(drop_code, exception_message)

        # Update the count for this reason
        current_count = reason_map.get(reason, 0)
        reason_map[reason] = current_count + count

    def count_retry_items(
        self, count: int, telemetry_type: str, retry_code: RetryCodeType, exception_message: Optional[str] = None
    ) -> None:
        if not self._is_enabled or count <= 0:
            return

        if telemetry_type not in self._counters.total_item_retry_count:
            self._counters.total_item_retry_count[telemetry_type] = {}
        retry_code_map = self._counters.total_item_retry_count[telemetry_type]

        if retry_code not in retry_code_map:
            retry_code_map[retry_code] = {}
        reason_map = retry_code_map[retry_code]

        reason = self._get_retry_reason(retry_code, exception_message)

        current_count = reason_map.get(reason, 0)
        reason_map[reason] = current_count + count

    def _item_success_callback(
        self, options: CallbackOptions
    ) -> Iterable[Observation]:  # pylint: disable=unused-argument
        if not getattr(self, "_is_enabled", False):
            return []

        observations: List[Observation] = []

        for telemetry_type, count in self._counters.total_item_success_count.items():
            if count > 0:
                attributes = {
                    "language": self._customer_properties.language,
                    "version": self._customer_properties.version,
                    "compute_type": self._customer_properties.compute_type,
                    "telemetry_type": telemetry_type,
                }
                observations.append(Observation(count, dict(attributes)))

        return observations

    def _item_drop_callback(self, options: CallbackOptions) -> Iterable[Observation]:  # pylint: disable=unused-argument
        if not getattr(self, "_is_enabled", False):
            return []
        observations: List[Observation] = []
        for telemetry_type, drop_code_map in self._counters.total_item_drop_count.items():
            for drop_code, reason_map in drop_code_map.items():
                for reason, count in reason_map.items():
                    if count > 0:
                        attributes = {
                            "language": self._customer_properties.language,
                            "version": self._customer_properties.version,
                            "compute_type": self._customer_properties.compute_type,
                            "drop.code": drop_code,
                            "drop.reason": reason,
                            "telemetry_type": telemetry_type,
                        }
                        observations.append(Observation(count, dict(attributes)))

        return observations

    def _item_retry_callback(
        self, options: CallbackOptions
    ) -> Iterable[Observation]:  # pylint: disable=unused-argument
        if not getattr(self, "_is_enabled", False):
            return []
        observations: List[Observation] = []
        for telemetry_type, retry_code_map in self._counters.total_item_retry_count.items():
            for retry_code, reason_map in retry_code_map.items():
                for reason, count in reason_map.items():
                    if count > 0:
                        attributes = {
                            "language": self._customer_properties.language,
                            "version": self._customer_properties.version,
                            "compute_type": self._customer_properties.compute_type,
                            "retry.code": retry_code,
                            "retry.reason": reason,
                            "telemetry_type": telemetry_type,
                        }
                        observations.append(Observation(count, dict(attributes)))

        return observations

    def _get_drop_reason(self, drop_code: DropCodeType, exception_message: Optional[str] = None) -> str:
        if isinstance(drop_code, int):
            return categorize_status_code(drop_code)

        if drop_code == DropCode.CLIENT_EXCEPTION:
            return exception_message if exception_message else "unknown_exception"

        drop_code_reasons = {
            DropCode.CLIENT_READONLY: "readonly_mode",
            DropCode.CLIENT_STORAGE_DISABLED: "local storage is disabled",
            DropCode.CLIENT_PERSISTENCE_CAPACITY: "persistence_full",
        }

        return drop_code_reasons.get(drop_code, "unknown_reason")

    def _get_retry_reason(self, retry_code: RetryCodeType, exception_message: Optional[str] = None) -> str:
        if isinstance(retry_code, int):
            return categorize_status_code(retry_code)

        if retry_code == RetryCode.CLIENT_EXCEPTION:
            return exception_message if exception_message else "unknown_exception"

        retry_code_reasons = {
            RetryCode.CLIENT_TIMEOUT: "client_timeout",
            RetryCode.UNKNOWN: "unknown_reason",
        }
        return retry_code_reasons.get(retry_code, "unknown_reason")


# Global customer sdkstats singleton
_CUSTOMER_SDKSTATS_METRICS = None
_CUSTOMER_SDKSTATS_LOCK = threading.Lock()


# pylint: disable=global-statement
# pylint: disable=protected-access
def collect_customer_sdkstats(exporter):
    global _CUSTOMER_SDKSTATS_METRICS
    # Only start customer sdkstats if did not exist before
    if _CUSTOMER_SDKSTATS_METRICS is None:
        with _CUSTOMER_SDKSTATS_LOCK:
            # Double-check inside the lock to avoid race conditions
            if _CUSTOMER_SDKSTATS_METRICS is None:
                connection_string = (
                    f"InstrumentationKey={exporter._instrumentation_key};" f"IngestionEndpoint={exporter._endpoint}"
                )
                _CUSTOMER_SDKSTATS_METRICS = CustomerSdkStatsMetrics(connection_string)

    exporter._customer_sdkstats_metrics = _CUSTOMER_SDKSTATS_METRICS
    if hasattr(exporter, "storage") and exporter.storage:
        exporter.storage._customer_sdkstats_metrics = _CUSTOMER_SDKSTATS_METRICS


def shutdown_customer_sdkstats_metrics() -> None:
    global _CUSTOMER_SDKSTATS_METRICS
    shutdown_success = False
    if _CUSTOMER_SDKSTATS_METRICS is not None:
        with _CUSTOMER_SDKSTATS_LOCK:
            try:
                if _CUSTOMER_SDKSTATS_METRICS._customer_sdkstats_meter_provider is not None:
                    _CUSTOMER_SDKSTATS_METRICS._customer_sdkstats_meter_provider.shutdown()
                    _CUSTOMER_SDKSTATS_METRICS = None
                    shutdown_success = True
            except:  # pylint: disable=bare-except
                pass
        if shutdown_success:
            with _CUSTOMER_SDKSTATS_STATE_LOCK:
                _CUSTOMER_SDKSTATS_STATE["SHUTDOWN"] = True
