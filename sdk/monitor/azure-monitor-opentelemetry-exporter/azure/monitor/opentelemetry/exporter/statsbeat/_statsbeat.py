# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics

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
            )
            reader = PeriodicExportingMetricReader(
                statsbeat_exporter,
                export_interval_millis=_get_stats_short_export_interval() * 1000,  # 15m by default
            )
            _STATSBEAT_METER_PROVIDER = MeterProvider(metric_readers=[reader])
            statsbeat_metrics = _StatsbeatMetrics(
                _STATSBEAT_METER_PROVIDER,
                exporter._instrumentation_key,
                exporter._endpoint,
            )
            return statsbeat_metrics
            # Export some initial stats on program start
            # TODO: initial stats
            # TODO: set context
            # execution_context.set_is_exporter(True)
            # exporter.export_metrics(_STATSBEAT_METRICS.get_initial_metrics())
            # execution_context.set_is_exporter(False)
        # TODO: state
        # with _STATSBEAT_STATE_LOCK:
        #     _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] = 0
        #     _STATSBEAT_STATE["INITIAL_SUCCESS"] = 0
        #     _STATSBEAT_STATE["SHUTDOWN"] = False

# TODO
# def shutdown_statsbeat_metrics() -> None:
#     global _STATSBEAT_METER_PROVIDER
#     shutdown_success = False
#     if _STATSBEAT_METER_PROVIDER is not None:
#         with _STATSBEAT_LOCK:
#             try:
#                 _STATSBEAT_METER_PROVIDER.shutdown()
#                 _STATSBEAT_METER_PROVIDER = None
#                 shutdown_success = True
#             except:
#                 pass
#         if shutdown_success:
#             # with _STATSBEAT_STATE_LOCK:
#             #     _STATSBEAT_STATE["SHUTDOWN"] = True
#             pass


def _get_stats_connection_string(endpoint: str) -> str:
    cs_env = os.environ.get("APPLICATION_INSIGHTS_STATS_CONNECTION_STRING")
    if cs_env:
        return cs_env
    for ep in _EU_ENDPOINTS:
        if ep in endpoint:
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
