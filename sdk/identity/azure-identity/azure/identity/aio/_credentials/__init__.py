# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .auth_file import AuthFileCredential
from .authorization_code import AuthorizationCodeCredential
from .chained import ChainedTokenCredential
from .default import DefaultAzureCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .client_credential import CertificateCredential, ClientSecretCredential
from .shared_cache import SharedTokenCacheCredential


__all__ = [
    "AuthFileCredential",
    "AuthorizationCodeCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
]
