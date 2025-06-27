# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer Statsbeat implementation for Azure Monitor OpenTelemetry Exporter.

This module provides the implementation for collecting and reporting customer statsbeat
metrics that track the usage and performance of the Azure Monitor OpenTelemetry Exporter.
"""

from typing import List, Dict, Any, Iterable
import logging
import os

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
)
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat_types import (
    CustomerStatsbeatProperties,
    DropCode, 
    RetryCode,
    CustomerStatsbeatMetricName,
    STATSBEAT_LANGUAGE
)
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version, 
    _is_on_app_service, 
    _is_on_functions, 
    _is_on_aks,
    Singleton
)

logger = logging.getLogger(__name__)

class CustomerStatsbeatMetrics(_StatsbeatMetrics, metaclass=Singleton):

    _instance_initialized = False

    def __init__(self, options):
        self.total_item_success_count: Dict[str, Any] = {}
        self.total_item_drop_count: Dict[str, Dict[str, Dict[str, int]]] = {}
        self.total_item_retry_count: Dict[str, Any] = {}
        
        self._language = STATSBEAT_LANGUAGE
        
        self._is_enabled = os.environ.get(_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW, "").lower() in ("true")
        if not self._is_enabled:
            logger.debug(
                "Customer statsbeat is disabled. "
                f"Enable it by setting {_APPLICATIONINSIGHTS_STATSBEAT_ENABLED_PREVIEW}=true"
            )
            return

        exporter_config = {
            "connection_string": f"InstrumentationKey={options.instrumentation_key};"
                                 f"IngestionEndpoint={options.endpoint_url}"
        }
        self._customer_statsbeat_exporter = AzureMonitorMetricExporter(**exporter_config)
        
        # Configure metric reader
        metric_reader_options = {
            "exporter": self._customer_statsbeat_exporter,
            "export_interval_millis": _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
        }
        self._customer_statsbeat_metric_reader = PeriodicExportingMetricReader(**metric_reader_options)
        
        self._customer_statsbeat_meter_provider = MeterProvider(
            metric_readers=[self._customer_statsbeat_metric_reader]
        )
        
        super().__init__(
            meter_provider=self._customer_statsbeat_meter_provider,
            instrumentation_key=options.instrumentation_key,
            endpoint=options.endpoint_url,
            disable_offline_storage=False,
            long_interval_threshold=15,  # Default to 15 minutes
            has_credential=False,
            distro_version=""
        )
        
        self._customer_statsbeat_meter = self._customer_statsbeat_meter_provider.get_meter(
            __name__
        )
        
        def get_compute_type():
            if _is_on_functions():
                return "functions"
            elif _is_on_app_service():
                # cspell:disable-next-line
                return "appsvc"
            elif _is_on_aks():
                return "aks"
            return "Other"

        self._customer_properties = CustomerStatsbeatProperties(
            language=self._language,
            version=_get_sdk_version(),
            compute_type=get_compute_type()
        )
        self._success_gauge = self._customer_statsbeat_meter.create_observable_gauge(
            name=CustomerStatsbeatMetricName.ITEM_SUCCESS_COUNT.value,
            description="Tracks successful telemetry items sent to Azure Monitor",
            callbacks=[self._item_success_callback]
        )

        CustomerStatsbeatMetrics._instance_initialized = True
        
    def count_successful_items(self, count: int, telemetry_type: str) -> None:
        if not self._is_enabled or count <= 0:
            return
        
        if telemetry_type in self.total_item_success_count:
            self.total_item_success_count[telemetry_type] += count
        else:
           self.total_item_success_count[telemetry_type] = count


    def _item_success_callback(self, options: CallbackOptions) -> Iterable[Observation]:
        if not getattr(self, "_is_enabled", False):
            return []

        observations: List[Observation] = []
        for telemetry_type, count in self.total_item_success_count.items():
            attributes = {
                "language": self._customer_properties.language,
                "version": self._customer_properties.version,
                "compute_type": self._customer_properties.compute_type,
                "telemetry_type": telemetry_type
            }

            observations.append(Observation(count, dict(attributes)))

            # Reset count after reporting
            #self.total_item_success_count[telemetry_type] = 0
            
        return observations
    
def collect_customer_statsbeat(exporter):
    if getattr(exporter, '_is_stats_exporter', lambda: False)():
        return
    statsbeat_options = {
                'instrumentation_key': exporter._instrumentation_key,
                'endpoint_url': exporter._endpoint,
                'network_collection_interval': _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
            }
    exporter._customer_statsbeat_metrics = CustomerStatsbeatMetrics(statsbeat_options)
    # Connect storage with customer statsbeat if storage exists
    if hasattr(exporter, 'storage') and exporter.storage:
        exporter.storage._customer_statsbeat_metrics = exporter._customer_statsbeat_metrics
