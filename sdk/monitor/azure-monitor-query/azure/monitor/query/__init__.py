# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._log_query_client import LogQueryClient
from ._metrics_query_client import MetricsQueryClient

from ._models import (
    LogQueryResults,
    LogQueryResultTable,
    LogQueryResultColumn,
    MetricsResponse
)

from ._generated.models import MetricNamespaceCollection
    
from ._version import VERSION

__all__ = [
    "LogQueryClient",
    "LogQueryResults",
    "LogQueryResultColumn",
    "LogQueryResultTable",
    "MetricsQueryClient",
    "MetricsResponse",
    "MetricNamespaceCollection"
]

__version__ = VERSION
