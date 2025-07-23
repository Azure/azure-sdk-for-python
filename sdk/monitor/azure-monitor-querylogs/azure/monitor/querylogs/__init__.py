# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._logs_query_client import LogsQueryClient

from ._enums import LogsQueryStatus
from ._exceptions import LogsQueryError
from ._models import (
    LogsQueryResult,
    LogsTable,
    LogsQueryPartialResult,
    LogsTableRow,
    LogsBatchQuery,
)

from ._version import VERSION

__all__ = [
    "LogsQueryClient",
    "LogsQueryResult",
    "LogsQueryPartialResult",
    "LogsQueryStatus",
    "LogsQueryError",
    "LogsTable",
    "LogsTableRow",
    "LogsBatchQuery",
]

__version__ = VERSION
