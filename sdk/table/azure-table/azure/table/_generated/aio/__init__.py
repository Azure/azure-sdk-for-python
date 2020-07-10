# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
__all__ = [
    'TableClient',
    'TableServiceClient',
]

from azure.table._aio._table_client_async import TableClient
from azure.table._aio._table_service_client_async import TableServiceClient

