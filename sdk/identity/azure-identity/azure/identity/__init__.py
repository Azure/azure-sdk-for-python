# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for Azure SDK clients."""

from ._auth_record import AuthenticationRecord
from ._enums import RegionalAuthority
from ._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from ._constants import AzureAuthorityHosts, KnownAuthorities
from ._credentials import (
    AuthorizationCodeCredential,
    AzureApplicationCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    OnBehalfOfCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
    VisualStudioCodeCredential,
)
from ._persistent_cache import TokenCachePersistenceOptions
from ._user_assertion import UserAssertion


__all__ = [
    "AuthenticationRecord",
    "AuthenticationRequiredError",
    "AuthorizationCodeCredential",
    "AzureApplicationCredential",
    "AzureAuthorityHosts",
    "AzureCliCredential",
    "AzurePowerShellCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "CredentialUnavailableError",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "KnownAuthorities",
    "OnBehalfOfCredential",
    "RegionalAuthority",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "TokenCachePersistenceOptions",
    "UserAssertion",
    "UsernamePasswordCredential",
    "VisualStudioCodeCredential",
]

from ._version import VERSION

__version__ = VERSION
