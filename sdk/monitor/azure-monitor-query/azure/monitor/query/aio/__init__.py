# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._log_query_client_async import LogsClient
from ._metrics_query_client_async import MetricsClient

__all__ = [
    "LogsClient",
    "MetricsClient"
]
