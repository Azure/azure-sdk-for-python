# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
)

# pylint: disable=line-too-long
_DEFAULT_NON_EU_STATS_CONNECTION_STRING = "InstrumentationKey=c4a29126-a7cb-47e5-b348-11414998b11e;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/"
_DEFAULT_EU_STATS_CONNECTION_STRING = "InstrumentationKey=7dc56bab-3c0c-4e9f-9ebb-d1acadee8d0f;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/"
_DEFAULT_STATS_SHORT_EXPORT_INTERVAL = 900  # 15 minutes
_DEFAULT_STATS_LONG_EXPORT_INTERVAL = 86400  # 24 hours
_EU_ENDPOINTS = [
    "westeurope",
    "northeurope",
    "francecentral",
    "francesouth",
    "germanywestcentral",
    "norwayeast",
    "norwaywest",
    "swedencentral",
    "switzerlandnorth",
    "switzerlandwest",
    "uksouth",
    "ukwest",
]

_STATSBEAT_METER_PROVIDER = None
_STATSBEAT_LOCK = threading.Lock()

# pylint: disable=global-statement
# pylint: disable=protected-access
def collect_statsbeat_metrics(exporter) -> None:
    global _STATSBEAT_METER_PROVIDER
    # Only start statsbeat if did not exist before
    if _STATSBEAT_METER_PROVIDER is None:
        with _STATSBEAT_LOCK:
            statsbeat_exporter = _StatsBeatExporter(
                connection_string=_get_stats_connection_string(exporter._endpoint),
                disable_offline_storage=exporter._disable_offline_storage,
            )
            reader = PeriodicExportingMetricReader(
                statsbeat_exporter,
                export_interval_millis=_get_stats_short_export_interval() * 1000,  # 15m by default
            )
            _STATSBEAT_METER_PROVIDER = MeterProvider(metric_readers=[reader])
            # long_interval_threshold represents how many collects for short interval
            # should have passed before a long interval collect
            long_interval_threshold = _get_stats_long_export_interval() / _get_stats_short_export_interval()
            metrics = _StatsbeatMetrics(
                _STATSBEAT_METER_PROVIDER,
                exporter._instrumentation_key,
                exporter._endpoint,
                exporter._disable_offline_storage,
                long_interval_threshold,
            )
        # Export some initial stats on program start
        _STATSBEAT_METER_PROVIDER.force_flush()
        # initialize non-initial stats
        metrics.init_non_initial_metrics()


def shutdown_statsbeat_metrics() -> None:
    global _STATSBEAT_METER_PROVIDER
    shutdown_success = False
    if _STATSBEAT_METER_PROVIDER is not None:
        with _STATSBEAT_LOCK:
            try:
                _STATSBEAT_METER_PROVIDER.shutdown()
                _STATSBEAT_METER_PROVIDER = None
                shutdown_success = True
            except:  # pylint: disable=bare-except
                pass
        if shutdown_success:
            with _STATSBEAT_STATE_LOCK:
                _STATSBEAT_STATE["SHUTDOWN"] = True


def _get_stats_connection_string(endpoint: str) -> str:
    cs_env = os.environ.get("APPLICATION_INSIGHTS_STATS_CONNECTION_STRING")
    if cs_env:
        return cs_env
    for endpoint_location in _EU_ENDPOINTS:
        if endpoint_location in endpoint:
            # Use statsbeat EU endpoint if user is in EU region
            return _DEFAULT_EU_STATS_CONNECTION_STRING
    return _DEFAULT_NON_EU_STATS_CONNECTION_STRING


# seconds
def _get_stats_short_export_interval() -> float:
    ei_env = os.environ.get("APPLICATION_INSIGHTS_STATS_SHORT_EXPORT_INTERVAL")
    if ei_env:
        return int(ei_env)
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL


# seconds
def _get_stats_long_export_interval() -> float:
    ei_env = os.environ.get("APPLICATION_INSIGHTS_STATS_LONG_EXPORT_INTERVAL")
    if ei_env:
        return int(ei_env)
    return _DEFAULT_STATS_LONG_EXPORT_INTERVAL
