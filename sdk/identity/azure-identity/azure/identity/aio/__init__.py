# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for asynchronous Azure SDK clients."""

from ._credentials import (
    AuthorizationCodeCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    OnBehalfOfCredential,
    SharedTokenCacheCredential,
    VisualStudioCodeCredential,
    ClientAssertionCredential,
)


__all__ = [
    "AuthorizationCodeCredential",
    "AzureCliCredential",
    "AzurePowerShellCredential",
    "CertificateCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "OnBehalfOfCredential",
    "ChainedTokenCredential",
    "SharedTokenCacheCredential",
    "VisualStudioCodeCredential",
    "ClientAssertionCredential",
]
