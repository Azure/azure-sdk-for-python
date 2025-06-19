# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Statsbeat package for Azure Monitor OpenTelemetry Exporter."""

from typing import Any, List

from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat_types import (
    TelemetryType, DropCode, RetryCode, CustomerStatsbeat, CustomStatsbeatCounter
)

# DO NOT import CustomerStatsbeatMetrics here to avoid circular imports
# The class will be available via the lazy import below

# Define CustomerStatsbeatMetrics for type checking only
CustomerStatsbeatMetrics: Any = None

__all__: List[str] = [
    'TelemetryType',
    'DropCode',
    'RetryCode',
    'CustomerStatsbeat',
    'CustomStatsbeatCounter',
    'CustomerStatsbeatMetrics',
]

# Avoid circular imports by using lazy import
def __getattr__(name):
    if name == "CustomerStatsbeatMetrics":
        from azure.monitor.opentelemetry.exporter.statsbeat._customer_statsbeat import CustomerStatsbeatMetrics
        return CustomerStatsbeatMetrics
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
