# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .adls_gen1 import AzureDataLakeGen1Schema
from .azure_storage import AzureBlobSchema, AzureDataLakeGen2Schema, AzureFileSchema, AzureStorageSchema
from .credentials import (
    AccountKeySchema,
    BaseTenantCredentialSchema,
    CertificateSchema,
    NoneCredentialsSchema,
    SasTokenSchema,
    ServicePrincipalSchema,
)

__all__ = [
    "AccountKeySchema",
    "AzureBlobSchema",
    "AzureDataLakeGen1Schema",
    "AzureDataLakeGen2Schema",
    "AzureFileSchema",
    "AzureStorageSchema",
    "BaseTenantCredentialSchema",
    "CertificateSchema",
    "NoneCredentialsSchema",
    "SasTokenSchema",
    "ServicePrincipalSchema",
]
