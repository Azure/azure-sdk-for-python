# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._logs_query_client import LogsQueryClient
from ._metrics_query_client import MetricsQueryClient

from ._exceptions import LogsQueryError

from ._models import (
    MetricAggregationType,
    LogsQueryResult,
    LogsTable,
    LogsQueryPartialResult,
    LogsQueryStatus,
    LogsTableRow,
    MetricsQueryResult,
    LogsBatchQuery,
    MetricNamespace,
    MetricNamespaceClassification,
    MetricDefinition,
    MetricUnit,
    TimeSeriesElement,
    Metric,
    MetricValue,
    MetricClass,
    MetricAvailability,
)

from ._version import VERSION

__all__ = [
    "MetricAggregationType",
    "LogsQueryClient",
    "LogsQueryResult",
    "LogsQueryPartialResult",
    "LogsQueryStatus",
    "LogsQueryError",
    "LogsTable",
    "LogsTableRow",
    "LogsBatchQuery",
    "MetricsQueryClient",
    "MetricNamespace",
    "MetricNamespaceClassification",
    "MetricDefinition",
    "MetricUnit",
    "MetricsQueryResult",
    "TimeSeriesElement",
    "Metric",
    "MetricValue",
    "MetricClass",
    "MetricAvailability",
]

__version__ = VERSION
