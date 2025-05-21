# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import threading
from threading import Timer

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter._constants import _INITIAL_DELAY_SECONDS
from azure.monitor.opentelemetry.exporter.statsbeat._exporter import _StatsBeatExporter
from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat_metrics import _StatsbeatMetrics
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _STATSBEAT_STATE,
    _STATSBEAT_STATE_LOCK,
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _get_stats_connection_string,
    _get_stats_long_export_interval,
    _get_stats_short_export_interval,
)

_STATSBEAT_METRICS = None
_STATSBEAT_LOCK = threading.Lock()

def _delayed_export_statsbeat():
    """
    Function to perform a delayed export of statsbeat metrics
    after the initial delay period has passed.
    """
    # Check if we're in a shutdown state
    with _STATSBEAT_STATE_LOCK:
        if _STATSBEAT_STATE["SHUTDOWN"]:
            return

    if _STATSBEAT_METRICS is not None and _STATSBEAT_METRICS._meter_provider is not None:
        try:
            # Trigger a forced export of the metrics after the delay
            _STATSBEAT_METRICS._meter_provider.force_flush()
        except:  # pylint: disable=bare-except
            pass

# pylint: disable=global-statement
# pylint: disable=protected-access
def collect_statsbeat_metrics(exporter) -> None:
    global _STATSBEAT_METRICS
    # Only start statsbeat if did not exist before
    if _STATSBEAT_METRICS is None:
        with _STATSBEAT_LOCK:
            statsbeat_exporter = _StatsBeatExporter(
                connection_string=_get_stats_connection_string(exporter._endpoint),
                disable_offline_storage=exporter._disable_offline_storage,
            )
            reader = PeriodicExportingMetricReader(
                statsbeat_exporter,
                export_interval_millis=_get_stats_short_export_interval() * 1000,  # 15m by default
            )
            mp = MeterProvider(
                metric_readers=[reader],
                resource=Resource.get_empty(),
            )
            # long_interval_threshold represents how many collects for short interval
            # should have passed before a long interval collect
            long_interval_threshold = _get_stats_long_export_interval() // _get_stats_short_export_interval()
            _STATSBEAT_METRICS = _StatsbeatMetrics(
                mp,
                exporter._instrumentation_key,
                exporter._endpoint,
                exporter._disable_offline_storage,
                long_interval_threshold,
                exporter._credential is not None,
                exporter._distro_version,
            )        # Export some initial stats on program start
        mp.force_flush()
        # initialize non-initial stats
        _STATSBEAT_METRICS.init_non_initial_metrics()

        # Schedule a second export after the initial delay to send feature, instrumentation,
        # and attach statsbeat metrics (which have a 15-second delay)
        timer = Timer(_INITIAL_DELAY_SECONDS, _delayed_export_statsbeat)
        timer.daemon = True  # Set as daemon so it doesn't block program exit
        timer.start()

def shutdown_statsbeat_metrics() -> None:
    global _STATSBEAT_METRICS
    shutdown_success = False
    if _STATSBEAT_METRICS is not None:
        with _STATSBEAT_LOCK:
            try:
                # Cancel any pending timers by marking for shutdown
                with _STATSBEAT_STATE_LOCK:
                    _STATSBEAT_STATE["SHUTDOWN"] = True

                if _STATSBEAT_METRICS._meter_provider is not None:
                    _STATSBEAT_METRICS._meter_provider.shutdown()
                    _STATSBEAT_METRICS = None
                    shutdown_success = True
            except:  # pylint: disable=bare-except
                pass
        if shutdown_success:
            with _STATSBEAT_STATE_LOCK:
                _STATSBEAT_STATE["SHUTDOWN"] = True
