# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._log_query_client import LogQueryClient
from ._metrics_query_client import MetricsQueryClient
from ._generated.models import (
    BatchResponse,
    QueryResults as LogQueryResults,
    Table as QueryTable,
    Column as QueryResultColum,
    Response as MetricsResponse,
)
    
from ._version import VERSION

__all__ = [
    "BatchResponse",
    "LogQueryClient",
    "MetricsQueryClient",
    "LogQueryResults",
    "QueryTable",
    "QueryResultColum",
    "MetricsResponse"
]

__version__ = VERSION
