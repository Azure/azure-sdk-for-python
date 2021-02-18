# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.data.tables._models import TableServiceStats

from ._entity import TableEntity, EntityProperty, EdmType
from ._table_shared_access_signature import generate_table_sas, generate_account_sas
from ._table_client import TableClient
from ._table_service_client import TableServiceClient
from ._models import (
    AccessPolicy,
    Metrics,
    RetentionPolicy,
    TableAnalyticsLogging,
    TableSasPermissions,
    CorsRule,
    UpdateMode,
    SASProtocol,
    TableItem,
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    BatchTransactionResult,
    BatchErrorException,
)
from ._policies import ExponentialRetry, LinearRetry
from ._version import VERSION
from ._deserialize import TableErrorCode
from ._table_batch import TableBatchOperations

__version__ = VERSION

__all__ = [
    "TableClient",
    "TableServiceClient",
    "ExponentialRetry",
    "LinearRetry",
    "LocationMode",
    "ResourceTypes",
    "AccountSasPermissions",
    "TableErrorCode",
    "TableServiceStats",
    "TableSasPermissions",
    "AccessPolicy",
    "TableAnalyticsLogging",
    "Metrics",
    "generate_account_sas",
    "CorsRule",
    "UpdateMode",
    "TableItem",
    "TableEntity",
    "EntityProperty",
    "EdmType",
    "RetentionPolicy",
    "generate_table_sas",
    "SASProtocol",
    "BatchTransactionResult",
    "TableBatchOperations",
    "BatchErrorException",
]
