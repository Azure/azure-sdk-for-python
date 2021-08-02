# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._logs_query_client import LogsQueryClient
from ._metrics_query_client import MetricsQueryClient

from ._models import (
    AggregationType,
    LogsBatchQueryResult,
    LogsQueryResult,
    LogsQueryResultTable,
    LogsQueryResultColumn,
    MetricsResult,
    LogsBatchResultError,
    LogsBatchQueryRequest,
    MetricNamespace,
    MetricDefinition,
    MetricsMetadataValue,
    TimeSeriesElement,
    Metric,
    MetricValue,
    MetricAvailability
)

from ._version import VERSION

__all__ = [
    "AggregationType",
    "LogsQueryClient",
    "LogsBatchQueryResult",
    "LogsBatchResultError",
    "LogsQueryResult",
    "LogsQueryResultColumn",
    "LogsQueryResultTable",
    "LogsBatchQueryRequest",
    "MetricsQueryClient",
    "MetricNamespace",
    "MetricDefinition",
    "MetricsResult",
    "MetricsMetadataValue",
    "TimeSeriesElement",
    "Metric",
    "MetricValue",
    "MetricAvailability"
]

__version__ = VERSION
