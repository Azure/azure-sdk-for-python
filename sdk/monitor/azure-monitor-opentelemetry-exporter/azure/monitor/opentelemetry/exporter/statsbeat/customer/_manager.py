# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer SDK Stats Manager for Azure Monitor OpenTelemetry Exporter.

This module provides the CustomerSdkStatsManager class for collecting and reporting
Customer SDK Stats metrics that track the usage and performance of the Azure Monitor
OpenTelemetry Exporter.
"""

import threading
from typing import List, Dict, Any, Iterable, Optional, Union
from enum import Enum

from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter._constants import (
    DropCode,
    DropCodeType,
    RetryCode,
    RetryCodeType,
    CustomerSdkStatsMetricName,
    _CUSTOMER_SDKSTATS_LANGUAGE,
    _exception_categories,
    _REQUEST,
    _DEPENDENCY,
)

from azure.monitor.opentelemetry.exporter._utils import (
    Singleton,
    get_compute_type,
)

from ._utils import get_customer_sdkstats_export_interval, categorize_status_code, is_customer_sdkstats_enabled


class CustomerSdkStatsStatus(Enum):
    """Status enumeration for Customer SDK Stats Manager."""
    DISABLED = "disabled"           # Feature is disabled via environment variable
    UNINITIALIZED = "uninitialized" # Manager created but not initialized
    ACTIVE = "active"              # Fully initialized and operational
    SHUTDOWN = "shutdown"          # Has been shut down


class _CustomerSdkStatsTelemetryCounters:
    def __init__(self):
        self.total_item_success_count: Dict[str, Any] = {}  # type: ignore
        self.total_item_drop_count: Dict[str, Dict[DropCodeType, Dict[str, Dict[bool, int]]]] = {}  # type: ignore #pylint: disable=too-many-nested-blocks
        self.total_item_retry_count: Dict[str, Dict[RetryCodeType, Dict[str, int]]] = {}  # type: ignore


class CustomerSdkStatsManager(metaclass=Singleton): # pylint: disable=too-many-instance-attributes
    def __init__(self):
        # Initialize instance attributes that remain constant. Called only once due to Singleton metaclass.
        self._initialization_lock = threading.Lock()  # For initialization/shutdown operations
        self._counters_lock = threading.Lock()        # For counter operations and callbacks

        # Determine initial status based on environment
        if is_customer_sdkstats_enabled():
            self._status = CustomerSdkStatsStatus.UNINITIALIZED
        else:
            self._status = CustomerSdkStatsStatus.DISABLED

        self._counters = _CustomerSdkStatsTelemetryCounters()
        self._language = _CUSTOMER_SDKSTATS_LANGUAGE

        # Initialize connection-dependent attributes to None
        self._customer_sdkstats_exporter = None
        self._customer_sdkstats_metric_reader = None
        self._customer_sdkstats_meter_provider = None
        self._customer_sdkstats_meter = None

        # Initialize customer properties if enabled
        if self._status != CustomerSdkStatsStatus.DISABLED:
            from azure.monitor.opentelemetry.exporter import VERSION
            # Pre-build base attributes for all metrics to avoid recreation on each callback
            self._base_attributes: Optional[Dict[str, Any]] = {  # type: ignore
                "language": self._language,
                "version": VERSION,
                "compute_type": get_compute_type(),
            }
        else:
            self._base_attributes = None

        # Initialize gauge references (gauges will be created in initialize method once meter is available)
        self._success_gauge = None
        self._dropped_gauge = None
        self._retry_gauge = None

    @property
    def status(self) -> CustomerSdkStatsStatus:
        """Get the current status of the manager.

        :return: Current status
        :rtype: CustomerSdkStatsStatus
        """
        return self._status  # type: ignore

    @property
    def is_enabled(self) -> bool:
        """Check if customer SDK stats collection is enabled.

        :return: True if enabled, False otherwise
        :rtype: bool
        """
        return self._status != CustomerSdkStatsStatus.DISABLED  # type: ignore

    @property
    def is_initialized(self) -> bool:
        """Check if the manager is initialized and ready to collect stats.

        :return: True if initialized, False otherwise
        :rtype: bool
        """
        return self._status == CustomerSdkStatsStatus.ACTIVE  # type: ignore

    @property
    def is_shutdown(self) -> bool:
        """Check if the manager has been shut down.

        :return: True if shut down, False otherwise
        :rtype: bool
        """
        return self._status == CustomerSdkStatsStatus.SHUTDOWN  # type: ignore

    def initialize(self, connection_string: str) -> bool:
        """Initialize Customer SDKStats collection with the provided connection string.

        :param connection_string: Azure Monitor connection string
        :type connection_string: str
        :return: True if initialization was successful, False otherwise
        :rtype: bool
        """
        if not self.is_enabled:
            return False

        if not connection_string:
            return False

        with self._initialization_lock:
            if self.is_initialized:
                # Already initialized, return True
                return True

            return self._do_initialize(connection_string)

    def _do_initialize(self, connection_string: str) -> bool:
        """Internal initialization method.

        :param connection_string: Azure Monitor connection string
        :type connection_string: str
        :return: True if initialization was successful, False otherwise
        :rtype: bool
        """
        try:
            # Use delayed import to avoid circular import
            from azure.monitor.opentelemetry.exporter.export.metrics._exporter import AzureMonitorMetricExporter

            self._customer_sdkstats_exporter = AzureMonitorMetricExporter(
                connection_string=connection_string,
                is_customer_sdkstats=True,
            )
            metric_reader_options = {
                "exporter": self._customer_sdkstats_exporter,
                "export_interval_millis": get_customer_sdkstats_export_interval() * 1000  # Default 15m
            }
            self._customer_sdkstats_metric_reader = PeriodicExportingMetricReader(**metric_reader_options)
            self._customer_sdkstats_meter_provider = MeterProvider(
                metric_readers=[self._customer_sdkstats_metric_reader]
            )
            self._customer_sdkstats_meter = self._customer_sdkstats_meter_provider.get_meter(__name__)

            self._success_gauge = self._customer_sdkstats_meter.create_observable_gauge(
                name=CustomerSdkStatsMetricName.ITEM_SUCCESS_COUNT.value,
                description="Tracks successful telemetry items sent to Azure Monitor",
                callbacks=[self._item_success_callback]
            )
            self._dropped_gauge = self._customer_sdkstats_meter.create_observable_gauge(
                name=CustomerSdkStatsMetricName.ITEM_DROP_COUNT.value,
                description="Tracks dropped telemetry items sent to Azure Monitor",
                callbacks=[self._item_drop_callback]
            )
            self._retry_gauge = self._customer_sdkstats_meter.create_observable_gauge(
                name=CustomerSdkStatsMetricName.ITEM_RETRY_COUNT.value,
                description="Tracks retry attempts for telemetry items sent to Azure Monitor",
                callbacks=[self._item_retry_callback]
            )

            # Set status to active after successful initialization
            self._status = CustomerSdkStatsStatus.ACTIVE
            return True

        except Exception:  # pylint: disable=broad-except
            # Clean up on failure and revert to uninitialized
            self._cleanup()
            return False

    def _cleanup(self) -> None:
        """Clean up resources on initialization failure."""
        self._customer_sdkstats_exporter = None
        self._customer_sdkstats_metric_reader = None
        self._customer_sdkstats_meter_provider = None
        self._customer_sdkstats_meter = None
        self._success_gauge = None
        self._dropped_gauge = None
        self._retry_gauge = None
        # Revert to uninitialized if not disabled
        if self._status != CustomerSdkStatsStatus.DISABLED:
            self._status = CustomerSdkStatsStatus.UNINITIALIZED

    def shutdown(self) -> bool:
        """Shutdown customer SDKStats metrics collection.

        :return: True if shutdown was successful, False otherwise
        :rtype: bool
        """
        if self.is_shutdown or not self.is_initialized:
            return False

        shutdown_success = False

        with self._initialization_lock:
            try:
                if self._customer_sdkstats_meter_provider is not None:
                    self._customer_sdkstats_meter_provider.shutdown()
                    shutdown_success = True
            except:  # pylint: disable=bare-except
                pass
            finally:
                # Always cleanup resources regardless of shutdown success
                self._cleanup()
                # Mark as shutdown if we attempted shutdown (even if it failed)
                self._status = CustomerSdkStatsStatus.SHUTDOWN

        return shutdown_success

    def count_successful_items(self, count: int, telemetry_type: str) -> None:
        if not self.is_initialized or count <= 0:
            return
        with self._counters_lock:
            if telemetry_type in self._counters.total_item_success_count:
                self._counters.total_item_success_count[telemetry_type] += count
            else:
                self._counters.total_item_success_count[telemetry_type] = count

    def count_dropped_items(
        self, count: int, telemetry_type: str, drop_code: DropCodeType, telemetry_success: Union[bool, None],
        exception_message: Optional[str] = None
    ) -> None:
        if not self.is_initialized or count <= 0 or telemetry_success is None:
            return
        with self._counters_lock:
            if telemetry_type not in self._counters.total_item_drop_count:
                self._counters.total_item_drop_count[telemetry_type] = {}
            drop_code_map = self._counters.total_item_drop_count[telemetry_type]

            if drop_code not in drop_code_map:
                drop_code_map[drop_code] = {}
            reason_map = drop_code_map[drop_code]

            reason = self._get_drop_reason(drop_code, exception_message)

            if reason not in reason_map:
                reason_map[reason] = {}
            success_map = reason_map[reason]

            success_key = telemetry_success

            current_count = success_map.get(success_key, 0)
            success_map[success_key] = current_count + count

    def count_retry_items(
        self, count: int, telemetry_type: str, retry_code: RetryCodeType,
        exception_message: Optional[str] = None
    ) -> None:
        if not self.is_initialized or count <= 0:
            return

        with self._counters_lock:
            if telemetry_type not in self._counters.total_item_retry_count:
                self._counters.total_item_retry_count[telemetry_type] = {}
            retry_code_map = self._counters.total_item_retry_count[telemetry_type]

            if retry_code not in retry_code_map:
                retry_code_map[retry_code] = {}
            reason_map = retry_code_map[retry_code]

            reason = self._get_retry_reason(retry_code, exception_message)

            current_count = reason_map.get(reason, 0)
            reason_map[reason] = current_count + count

    def _item_success_callback(self, options: CallbackOptions) -> Iterable[Observation]: # pylint: disable=unused-argument
        if not self.is_initialized or not self._base_attributes:
            return []

        observations: List[Observation] = []

        with self._counters_lock:
            for telemetry_type, count in self._counters.total_item_success_count.items():
                if count > 0:
                    # Create attributes by copying base and adding telemetry-specific data
                    attributes = self._base_attributes.copy()
                    attributes["telemetry_type"] = telemetry_type
                    observations.append(Observation(count, attributes))

            # Reset counts after reading
            self._counters.total_item_success_count.clear()

        return observations

    def _item_drop_callback(self, options: CallbackOptions) -> Iterable[Observation]: # pylint: disable=unused-argument
        if not self.is_initialized or not self._base_attributes:
            return []
        observations: List[Observation] = []
        # pylint: disable=too-many-nested-blocks

        with self._counters_lock:
            for telemetry_type, drop_code_map in self._counters.total_item_drop_count.items():
                for drop_code, reason_map in drop_code_map.items():
                    for reason, success_map in reason_map.items():
                        for success_tracker, count in success_map.items():
                            if count > 0:
                                # Create attributes by copying base and adding drop-specific data
                                attributes = self._base_attributes.copy()
                                attributes["drop.code"] = drop_code
                                attributes["drop.reason"] = reason
                                attributes["telemetry_type"] = telemetry_type
                                if telemetry_type in (_REQUEST, _DEPENDENCY):
                                    attributes["telemetry_success"] = success_tracker
                                observations.append(Observation(count, attributes))

            # Reset counts after reading
            self._counters.total_item_drop_count.clear()

        return observations

    def _item_retry_callback(self, options: CallbackOptions) -> Iterable[Observation]: # pylint: disable=unused-argument
        if not self.is_initialized or not self._base_attributes:
            return []
        observations: List[Observation] = []

        with self._counters_lock:
            for telemetry_type, retry_code_map in self._counters.total_item_retry_count.items():
                for retry_code, reason_map in retry_code_map.items():
                    for reason, count in reason_map.items():
                        if count > 0:
                            # Create attributes by copying base and adding retry-specific data
                            attributes = self._base_attributes.copy()
                            attributes["retry.code"] = retry_code
                            attributes["retry.reason"] = reason
                            attributes["telemetry_type"] = telemetry_type
                            observations.append(Observation(count, attributes))

            # Reset counts after reading
            self._counters.total_item_retry_count.clear()

        return observations

    def _get_drop_reason(self, drop_code: DropCodeType, exception_message: Optional[str] = None) -> str:
        if isinstance(drop_code, int):
            return categorize_status_code(drop_code)

        if drop_code == DropCode.CLIENT_EXCEPTION:
            return exception_message if exception_message else _exception_categories.CLIENT_EXCEPTION.value

        drop_code_reasons = {
            DropCode.CLIENT_READONLY: "Client readonly",
            DropCode.CLIENT_STORAGE_DISABLED: "Client local storage disabled",
            DropCode.CLIENT_PERSISTENCE_CAPACITY: "Client persistence capacity",
            DropCode.UNKNOWN: "Unknown reason"
        }

        return drop_code_reasons.get(drop_code, DropCode.UNKNOWN)

    def _get_retry_reason(self, retry_code: RetryCodeType, exception_message: Optional[str] = None) -> str:
        if isinstance(retry_code, int):
            return categorize_status_code(retry_code)

        if retry_code == RetryCode.CLIENT_EXCEPTION:
            return exception_message if exception_message else _exception_categories.CLIENT_EXCEPTION.value

        retry_code_reasons = {
            RetryCode.CLIENT_TIMEOUT: "Client timeout",
            RetryCode.UNKNOWN: "Unknown reason",
        }
        return retry_code_reasons.get(retry_code, RetryCode.UNKNOWN)
