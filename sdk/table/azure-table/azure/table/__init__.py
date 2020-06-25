# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.table._shared.shared_access_signature import generate_account_sas, generate_table_sas
from azure.table._table_client import TableClient
from azure.table._table_service_client import TableServiceClient

from ._version import VERSION
from ._shared.policies import ExponentialRetry, LinearRetry
from ._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    StorageErrorCode
)
from ._message_encoding import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)
from ._models import (
    TableProperties,
    AccessPolicy,
    Metrics,
    CorsRule,
    RetentionPolicy, TableAnalyticsLogging, TableSasPermissions,
)

__version__ = VERSION

__all__ = [
    'TableClient',
    'TableServiceClient',
    'ExponentialRetry',
    'LinearRetry',
    'LocationMode',
    'ResourceTypes',
    'AccountSasPermissions',
    'StorageErrorCode',
    'TableSasPermissions',
    'AccessPolicy',
    'TextBase64EncodePolicy',
    'TextBase64DecodePolicy',
    'BinaryBase64EncodePolicy',
    'BinaryBase64DecodePolicy',
    'TableAnalyticsLogging',
    'Metrics',
    'CorsRule',
    'RetentionPolicy',
    'generate_account_sas',
    'generate_table_sas'
]
