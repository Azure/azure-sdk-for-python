# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Customer SDK Stats module for Azure Monitor OpenTelemetry Exporter."""

from ._customer_sdkstats import (
    collect_customer_sdkstats,
    shutdown_customer_sdkstats_metrics,
)

from ._state import (
    get_customer_stats_manager,
)

__all__ = [
    "get_customer_stats_manager",
    "collect_customer_sdkstats", 
    "shutdown_customer_sdkstats_metrics",
]
