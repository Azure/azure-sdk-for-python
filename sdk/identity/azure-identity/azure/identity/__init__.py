# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for Azure SDK clients."""

from ._auth_record import AuthenticationRecord
from ._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from ._constants import AzureAuthorityHosts, KnownAuthorities
from ._credentials import (
    AzureCliCredential,
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
    VisualStudioCodeCredential,
)
from ._persistent_cache import TokenCachePersistenceOptions


__all__ = [
    "AuthenticationRecord",
    "AuthenticationRequiredError",
    "AuthorizationCodeCredential",
    "AzureAuthorityHosts",
    "AzureCliCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "CredentialUnavailableError",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "KnownAuthorities",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "TokenCachePersistenceOptions",
    "UsernamePasswordCredential",
    "VisualStudioCodeCredential",
]

from ._version import VERSION

__version__ = VERSION
