# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._log_query_client import LogsClient
from ._metrics_query_client import MetricsClient

from ._models import (
    LogsQueryResults,
    LogsQueryResultTable,
    LogsQueryResultColumn,
    MetricsResult,
    LogsBatchResponseError,
    LogsQueryRequest,
    LogsQueryBody,
    LogsBatchResponse,
    MetricNamespace,
    MetricDefinition
)

from ._version import VERSION

__all__ = [
    "LogsClient",
    "LogsBatchResponse",
    "LogsBatchResponseError",
    "LogsQueryResults",
    "LogsQueryResultColumn",
    "LogsQueryResultTable",
    "LogsQueryRequest",
    "LogsQueryBody",
    "MetricsClient",
    "MetricNamespace",
    "MetricDefinition",
    "MetricsResult",
]

__version__ = VERSION
