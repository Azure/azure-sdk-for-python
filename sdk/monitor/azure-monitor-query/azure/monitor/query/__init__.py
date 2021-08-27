# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._logs_query_client import LogsQueryClient
from ._metrics_query_client import MetricsQueryClient

from ._models import (
    MetricAggregationType,
    LogsQueryResult,
    LogsTable,
    MetricsResult,
    LogsBatchQuery,
    MetricNamespace,
    MetricNamespaceClassification,
    MetricDefinition,
    MetricUnit,
    TimeSeriesElement,
    Metric,
    MetricValue,
    MetricClass,
    MetricAvailability
)

from ._version import VERSION

__all__ = [
    "MetricAggregationType",
    "LogsQueryClient",
    "LogsQueryResult",
    "LogsTable",
    "LogsBatchQuery",
    "MetricsQueryClient",
    "MetricNamespace",
    "MetricNamespaceClassification",
    "MetricDefinition",
    "MetricUnit",
    "MetricsResult",
    "TimeSeriesElement",
    "Metric",
    "MetricValue",
    "MetricClass",
    "MetricAvailability"
]

__version__ = VERSION
