# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for Azure SDK clients."""

from ._constants import KnownAuthorities
from ._credentials import (
    AuthorizationCodeCredential,
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
)


__all__ = [
    "AuthorizationCodeCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "KnownAuthorities",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "UsernamePasswordCredential",
]
