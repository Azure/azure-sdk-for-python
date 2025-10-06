# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import TYPE_CHECKING

from azure.monitor.opentelemetry.exporter.statsbeat._state import set_statsbeat_customer_sdkstats_feature_set

from ._state import get_customer_stats_manager

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter.export._base import BaseExporter


# pylint: disable=protected-access
def collect_customer_sdkstats(exporter: "BaseExporter") -> None:  # type: ignore
    # Initialize customer SDKStats collection using global manager instance.
    # Uses the global CustomerSdkStatsManager instance for better performance
    # and cleaner access patterns.
    customer_stats = get_customer_stats_manager()
    # Check if already initialized (thread-safe check)
    if not customer_stats.is_initialized:
        # The initialize method is thread-safe and handles double-initialization
        customer_stats.initialize(connection_string=exporter._connection_string)  # type: ignore
    set_statsbeat_customer_sdkstats_feature_set()

def shutdown_customer_sdkstats_metrics() -> None:
    # Shutdown customer SDKStats metrics collection.
    customer_stats = get_customer_stats_manager()
    customer_stats.shutdown()  # Use the global manager instance
