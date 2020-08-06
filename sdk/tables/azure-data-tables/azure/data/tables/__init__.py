# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.data.tables._models import TableServiceStats

from ._entity import TableEntity, EntityProperty, EdmType
from ._shared.table_shared_access_signature import generate_table_sas, \
    generate_account_sas
from ._table_client import TableClient
from ._table_service_client import TableServiceClient

from ._models import (
    AccessPolicy,
    Metrics,
    RetentionPolicy, TableAnalyticsLogging, TableSasPermissions, CorsRule, UpdateMode, SASProtocol, Table,
)
from ._shared.models import (
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    TableErrorCode
)
from ._shared.policies import ExponentialRetry, LinearRetry
from ._version import VERSION

__version__ = VERSION

__all__ = [
    'TableClient',
    'TableServiceClient',
    'ExponentialRetry',
    'LinearRetry',
    'LocationMode',
    'ResourceTypes',
    'AccountSasPermissions',
    'TableErrorCode',
    'TableServiceStats',
    'TableSasPermissions',
    'AccessPolicy',
    'TableAnalyticsLogging',
    'Metrics',
    'generate_account_sas',
    'CorsRule',
    'UpdateMode',
    'Table',
    'TableEntity',
    'EntityProperty',
    'EdmType',
    'RetentionPolicy',
    'generate_table_sas',
    'SASProtocol'
]
