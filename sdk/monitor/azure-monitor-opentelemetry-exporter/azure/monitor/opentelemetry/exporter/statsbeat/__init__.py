# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Statsbeat metrics collection module.

This module provides a singleton-based, thread-safe manager for collecting
and reporting statsbeat metrics.
"""

from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import (
    collect_statsbeat_metrics,
    shutdown_statsbeat_metrics,
)
from azure.monitor.opentelemetry.exporter.statsbeat._manager import (
    StatsbeatConfig,
    StatsbeatManager,
)

__all__ = [
    'StatsbeatConfig',
    'StatsbeatManager', 
    'collect_statsbeat_metrics',
    'shutdown_statsbeat_metrics',
]
