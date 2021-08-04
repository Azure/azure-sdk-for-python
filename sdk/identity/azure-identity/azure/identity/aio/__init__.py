# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for asynchronous Azure SDK clients."""

from ._credentials import (
    AuthorizationCodeCredential,
    AzureApplicationCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    VisualStudioCodeCredential,
)


__all__ = [
    "AuthorizationCodeCredential",
    "AzureApplicationCredential",
    "AzureCliCredential",
    "AzurePowerShellCredential",
    "CertificateCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "ChainedTokenCredential",
    "SharedTokenCacheCredential",
    "VisualStudioCodeCredential",
]
